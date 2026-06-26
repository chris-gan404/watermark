import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageCms

import processor  # noqa: F401 - registers the image processors
from core.util import convert_heic_to_jpeg
from processor.core import start_process


def srgb_profile_bytes() -> bytes:
    profile = ImageCms.createProfile("sRGB")
    return ImageCms.ImageCmsProfile(profile).tobytes()


class ColorProfileTests(unittest.TestCase):
    def test_pipeline_preserves_source_icc_profile(self):
        icc_profile = srgb_profile_bytes()

        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "input.jpg"
            output_path = Path(temp_dir) / "output.jpg"
            exif = Image.Exif()
            exif[0x0132] = "2026:06:19 17:00:00"
            exif[0x8825] = {
                1: "S",
                2: (27.0, 25.0, 58.57),
                3: "E",
                4: (153.0, 10.0, 16.27),
                6: 44.0,
            }
            Image.new("RGB", (16, 16), (10, 80, 220)).save(
                input_path,
                icc_profile=icc_profile,
                exif=exif,
            )

            start_process(
                [{
                    "processor_name": "resize",
                    "width": 16,
                    "height": 16,
                    "save_buffer": False,
                }],
                input_path=str(input_path),
                output_path=str(output_path),
            )

            with Image.open(output_path) as output_image:
                self.assertEqual(output_image.info.get("icc_profile"), icc_profile)
                self.assertEqual(len(output_image.getexif()), 0)

    def test_preview_conversion_preserves_icc_profile(self):
        icc_profile = srgb_profile_bytes()

        with tempfile.TemporaryDirectory() as temp_dir:
            # A PNG fixture is enough to exercise the helper's decoded-image
            # to JPEG profile-preservation path.
            input_path = Path(temp_dir) / "input.png"
            Image.new("RGB", (8, 8), (10, 80, 220)).save(
                input_path,
                icc_profile=icc_profile,
            )

            jpeg_buffer = convert_heic_to_jpeg(str(input_path))
            with Image.open(jpeg_buffer) as output_image:
                self.assertEqual(output_image.info.get("icc_profile"), icc_profile)


if __name__ == "__main__":
    unittest.main()
