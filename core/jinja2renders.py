from jinja2 import pass_context

from core.configs import logos_dir
from core.geocoding import extract_gps_coordinates, reverse_geocode_state_city

MAX_LOCATION_CHARS = 24
ELLIPSIS = '...'

DATE_KEYS = (
    'DateTimeOriginal',
    'CreateDate',
    'DigitalCreationDate',
    'DateCreated',
    'DateTimeCreated',
    'DigitalCreationDateTime',
)


@pass_context
def vw(context, percent):
    exif = context.get('exif', {})
    return int(int(exif.get('ImageWidth', 0)) * percent / 100)


@pass_context
def vh(context, percent):
    exif = context.get('exif', {})
    return int(int(exif.get('ImageHeight', 0)) * percent / 100)


@pass_context
def auto_logo(context, brand: str = None):
    exif = context.get('exif', {})
    brand = (brand or exif.get('Make', 'default')).lower()

    for f in logos_dir.iterdir():
        if f.suffix.lower() in {'.png', '.jpg', '.jpeg'} and f.stem.lower() in brand:
            return str(f.absolute()).replace('\\', '/')
    default_logo = logos_dir / 'default.png'
    if default_logo.exists():
        return str(default_logo.absolute()).replace('\\', '/')
    return None


def _first_exif_value(exif: dict, keys: tuple[str, ...]) -> str:
    for key in keys:
        value = exif.get(key)
        if value is not None:
            value = str(value).strip()
            if value and value not in {'-', '0'}:
                return value
    return ''


def exif_location(exif: dict) -> str:
    """Return a state/locality label, resolving GPS when necessary."""
    exif = exif or {}
    state = _first_exif_value(
        exif,
        ('State', 'Province-State', 'ProvinceState'),
    )
    locality = _first_exif_value(
        exif,
        ('Sub-location', 'Sublocation', 'Location'),
    )
    if locality:
        return ' '.join(
            dict.fromkeys(part for part in (state, locality) if part)
        )

    coordinates = extract_gps_coordinates(exif)
    if coordinates:
        return reverse_geocode_state_city(*coordinates)

    city = _first_exif_value(exif, ('City',))
    if state or city:
        return ' '.join(dict.fromkeys(part for part in (state, city) if part))

    return ''


def time_with_location(exif: dict) -> str:
    """Format standard timestamp and append EXIF location when present."""
    exif = exif or {}
    timestamp = (_first_exif_value(exif, DATE_KEYS) or '0')[:16]
    location = _ellipsize(exif_location(exif), MAX_LOCATION_CHARS)
    return f'{timestamp} · {location}' if location else timestamp


def _ellipsize(value: str, max_chars: int) -> str:
    value = (value or '').strip()
    if len(value) <= max_chars:
        return value
    return f'{value[:max_chars - len(ELLIPSIS)]}{ELLIPSIS}'
