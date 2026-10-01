import importlib.util
import tempfile
import unittest
from pathlib import Path

from PIL import Image

spec = importlib.util.spec_from_file_location(
    "layout_stickers", Path(__file__).parents[1] / "scripts/layout_stickers.py")
layout = importlib.util.module_from_spec(spec)
spec.loader.exec_module(layout)


class TransparencyTests(unittest.TestCase):
    def prepare_image(self, image):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            image.save(base / "sticker.png")
            return layout.prepare(
                {"items": [{"path": "sticker.png", "sizes": ["medium"]}]}, base)

    def test_fully_transparent_rgba_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "fully transparent"):
            self.prepare_image(Image.new("RGBA", (1000, 1000), (0, 0, 0, 0)))

    def test_fully_transparent_palette_is_rejected(self):
        image = Image.new("P", (1000, 1000), 0)
        image.info["transparency"] = 0
        with self.assertRaisesRegex(ValueError, "fully transparent"):
            self.prepare_image(image)

    def test_palette_with_visible_pixels_is_accepted(self):
        image = Image.new("P", (1000, 1000), 0)
        image.info["transparency"] = 0
        image.putpixel((500, 500), 1)
        _, items, _ = self.prepare_image(image)
        self.assertEqual(len(items), 1)

    def test_opaque_rgb_is_accepted(self):
        _, items, _ = self.prepare_image(Image.new("RGB", (1000, 1000), "red"))
        self.assertEqual(len(items), 1)


if __name__ == "__main__":
    unittest.main()
