import json
import re
import threading
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from core import BASE_DIR
from core.configs import load_config
from core.logger import logger


_CACHE_PATH = BASE_DIR / 'config' / 'geocoding_cache.json'
_CACHE_KEY_VERSION = 'locality-v2'
_cache_lock = threading.Lock()
_request_lock = threading.Lock()
_cache = None
_last_request_at = 0.0


def _parse_coordinate(value, ref: str = ''):
    if value is None:
        return None

    text = str(value).strip()
    numbers = [float(item) for item in re.findall(r'-?\d+(?:\.\d+)?', text)]
    if not numbers:
        return None

    coordinate = abs(numbers[0])
    if len(numbers) >= 2:
        coordinate += numbers[1] / 60
    if len(numbers) >= 3:
        coordinate += numbers[2] / 3600

    direction = f'{text} {ref}'.upper()
    is_negative_direction = bool(
        re.search(r'\b(?:S|SOUTH|W|WEST)\b', direction)
    )
    if numbers[0] < 0 or is_negative_direction:
        coordinate = -coordinate
    return coordinate


def extract_gps_coordinates(exif: dict):
    exif = exif or {}
    latitude = _parse_coordinate(
        exif.get('GPSLatitude'),
        exif.get('GPSLatitudeRef', ''),
    )
    longitude = _parse_coordinate(
        exif.get('GPSLongitude'),
        exif.get('GPSLongitudeRef', ''),
    )
    if latitude is not None and longitude is not None:
        return latitude, longitude

    position = str(exif.get('GPSPosition', '')).strip()
    if position:
        parts = [part.strip() for part in position.split(',', 1)]
        if len(parts) == 2:
            latitude = _parse_coordinate(parts[0])
            longitude = _parse_coordinate(parts[1])
            if latitude is not None and longitude is not None:
                return latitude, longitude
    return None


def _load_cache():
    global _cache
    with _cache_lock:
        if _cache is not None:
            return _cache
        try:
            _cache = json.loads(_CACHE_PATH.read_text(encoding='utf-8'))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            _cache = {}
        return _cache


def _save_cache():
    _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp_path = _CACHE_PATH.with_suffix('.tmp')
    temp_path.write_text(
        json.dumps(_cache, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    temp_path.replace(_CACHE_PATH)


def _format_state_city(address: dict) -> str:
    state = next(
        (str(address[key]).strip() for key in ('state', 'region') if address.get(key)),
        '',
    )
    locality = next(
        (
            str(address[key]).strip()
            for key in (
                'suburb',
                'city_district',
                'neighbourhood',
                'quarter',
                'locality',
                'town',
                'village',
                'municipality',
                'city',
                'county',
            )
            if address.get(key)
        ),
        '',
    )
    return ' '.join(dict.fromkeys(part for part in (state, locality) if part))


def reverse_geocode_state_city(latitude: float, longitude: float) -> str:
    global _last_request_at

    config = load_config()
    if not config.getboolean('geocoding', 'enabled', fallback=True):
        return ''

    cache_key = f'{_CACHE_KEY_VERSION}:{latitude:.5f},{longitude:.5f}'
    cache = _load_cache()
    with _cache_lock:
        if cache_key in cache:
            return cache[cache_key]

    endpoint = config.get(
        'geocoding',
        'endpoint',
        fallback='https://nominatim.openstreetmap.org/reverse',
    )
    language = config.get('geocoding', 'language', fallback='en')
    user_agent = config.get(
        'geocoding',
        'user_agent',
        fallback='semi-utils/2.1.6 (local photo metadata tool)',
    )
    timeout = config.getfloat('geocoding', 'timeout', fallback=8.0)

    query = urlencode({
        'format': 'jsonv2',
        'lat': latitude,
        'lon': longitude,
        'zoom': 18,
        'addressdetails': 1,
        'layer': 'address',
        'accept-language': language,
    })
    request = Request(
        f'{endpoint}?{query}',
        headers={
            'User-Agent': user_agent,
            'Accept-Language': language,
        },
    )

    try:
        # The public Nominatim service permits at most one request per second.
        with _request_lock:
            wait_seconds = 1.0 - (time.monotonic() - _last_request_at)
            if wait_seconds > 0:
                time.sleep(wait_seconds)
            with urlopen(request, timeout=timeout) as response:
                payload = json.load(response)
            _last_request_at = time.monotonic()
        location = _format_state_city(payload.get('address', {}))
    except Exception as exc:
        logger.warning(
            f'Reverse geocoding failed for {latitude}, {longitude}: {exc}'
        )
        return ''

    with _cache_lock:
        cache[cache_key] = location
        try:
            _save_cache()
        except OSError as exc:
            logger.warning(f'Unable to save geocoding cache: {exc}')
    return location
