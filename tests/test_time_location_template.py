import json
import unittest
from unittest.mock import patch

from core.geocoding import _format_state_city, extract_gps_coordinates
from core.jinja2renders import exif_location, time_with_location
from core.util import get_template


class TimeLocationTemplateTests(unittest.TestCase):
    def test_text_location_is_appended_to_time(self):
        exif = {
            'DateTimeOriginal': '2026:06:19 11:30:00',
            'Location': '南岸',
            'City': '布里斯班',
            'State': '昆士兰',
            'Country': '澳大利亚',
        }
        self.assertEqual(
            time_with_location(exif),
            '2026:06:19 11:30 · 昆士兰 南岸',
        )

    @patch(
        'core.jinja2renders.reverse_geocode_state_city',
        return_value='Queensland Brisbane',
    )
    def test_gps_position_is_reverse_geocoded(self, reverse_geocode):
        exif = {
            'DateTimeOriginal': '2026:06:19 11:30:00',
            'GPSPosition': '27 deg 25 min 58.57 sec S, 153 deg 10 min 16.27 sec E',
        }
        self.assertEqual(
            exif_location(exif),
            'Queensland Brisbane',
        )
        latitude, longitude = reverse_geocode.call_args.args
        self.assertAlmostEqual(latitude, -27.432936, places=5)
        self.assertAlmostEqual(longitude, 153.171186, places=5)

    def test_decimal_gps_coordinates_are_parsed(self):
        coordinates = extract_gps_coordinates({
            'GPSLatitude': '27.4329367',
            'GPSLatitudeRef': 'South',
            'GPSLongitude': '153.1711867',
            'GPSLongitudeRef': 'East',
        })
        self.assertAlmostEqual(coordinates[0], -27.4329367)
        self.assertAlmostEqual(coordinates[1], 153.1711867)

    def test_suburb_is_preferred_over_city(self):
        self.assertEqual(
            _format_state_city({
                'suburb': 'Wynnum',
                'city': 'Brisbane',
                'state': 'Queensland',
            }),
            'Queensland Wynnum',
        )

    def test_explicit_sublocation_is_preferred_over_city(self):
        self.assertEqual(
            exif_location({
                'State': 'Queensland',
                'City': 'Brisbane',
                'Sub-location': 'Saint Lucia',
            }),
            'Queensland Saint Lucia',
        )

    def test_missing_location_matches_standard_time_output(self):
        exif = {'DateTimeOriginal': '2026:06:19 11:30:00'}
        self.assertEqual(time_with_location(exif), '2026:06:19 11:30')

    def test_new_template_renders_valid_pipeline_json(self):
        rendered = get_template('标准时间加地点').render({
            'exif': {
                'ImageWidth': '6000',
                'ImageHeight': '4000',
                'DateTimeOriginal': '2026:06:19 11:30:00',
                'CameraModelName': 'Camera',
                'LensModel': 'Lens',
                'FocalLengthIn35mmFormat': '35 mm',
                'FNumber': '2.8',
                'ShutterSpeed': '1/250',
                'ISO': '100',
                'City': 'Brisbane',
            }
        })
        pipeline = json.loads(rendered)
        self.assertEqual(
            pipeline[0]['right_bottom']['text'],
            '2026:06:19 11:30 · Brisbane',
        )
        self.assertEqual(len(pipeline), 1)
        self.assertEqual(pipeline[0]['processor_name'], 'watermark')
        self.assertEqual(pipeline[0]['delimiter_color'], '#D8D8D6')


if __name__ == '__main__':
    unittest.main()
