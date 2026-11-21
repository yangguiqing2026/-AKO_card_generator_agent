# ============================================
# Author: AKO_studio
# Agent: AKO_card_generator
# Tests for business card rendering
# ============================================

import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.gui.card_render import (  # noqa: E402
    CARD_H,
    CARD_W,
    FONT_PRESETS,
    ICON_CHOICES,
    PALETTES,
    TEMPLATES,
    render_card,
)


def sample_fields():
    return {
        "company": "贵州阿格建筑科技有限公司",
        "company_en": "Guizhou Age Architecture Technology Co., Ltd.",
        "name": "张三",
        "title": "技术总监",
        "phone": "138-0000-0000",
        "email": "zhangsan@example.com",
        "website": "https://www.ako.example.com",
        "address": "贵州省贵阳市观山湖区",
    }


class TestCardRender(unittest.TestCase):

    def test_all_templates_and_palettes_render(self):
        for template in TEMPLATES:
            for palette in PALETTES:
                with self.subTest(template=template, palette=palette):
                    image = render_card(sample_fields(), template, palette)
                    self.assertEqual(image.size, (CARD_W, CARD_H))
                    self.assertEqual(image.mode, "RGB")

    def test_unknown_template_raises(self):
        with self.assertRaisesRegex(ValueError, "模板"):
            render_card(sample_fields(), template="nope")

    def test_unknown_palette_raises(self):
        with self.assertRaisesRegex(ValueError, "色系"):
            render_card(sample_fields(), palette="nope")

    def test_custom_size(self):
        image = render_card(sample_fields(), size=(800, 480))
        self.assertEqual(image.size, (800, 480))

    def test_empty_fields_render_blank_card(self):
        image = render_card({}, template="centered", palette="charcoal")
        self.assertEqual(image.size, (CARD_W, CARD_H))

    def test_logo_path_is_composited(self):
        with tempfile.TemporaryDirectory() as tmp:
            logo_path = Path(tmp) / "logo.png"
            Image.new("RGBA", (80, 60), (255, 0, 0, 255)).save(logo_path)
            image = render_card(sample_fields(), logo=str(logo_path))
            self.assertIsInstance(image, Image.Image)
            self.assertEqual(image.size, (CARD_W, CARD_H))

    def test_logo_as_pil_image(self):
        logo = Image.new("RGBA", (60, 40), (0, 128, 0, 255))
        image = render_card(sample_fields(), template="banner", logo=logo)
        self.assertIsInstance(image, Image.Image)

    def test_palette_background_differs(self):
        light = render_card(sample_fields(), palette="deep_blue")
        dark_bg = render_card(sample_fields(), palette="charcoal")
        # Different palettes produce different pixel content overall.
        self.assertNotEqual(light.tobytes(), dark_bg.tobytes())

    def test_company_en_changes_output(self):
        fields = sample_fields()
        with_en = render_card(fields)
        without_en = render_card(dict(fields, company_en=""))
        self.assertNotEqual(with_en.tobytes(), without_en.tobytes())

    def test_font_path_is_honored(self):
        path = FONT_PRESETS["黑体"]
        if not Path(path).is_file():
            self.skipTest("font not available")
        image = render_card(sample_fields(), font_path=path)
        self.assertEqual(image.size, (CARD_W, CARD_H))

    def test_custom_font_sizes(self):
        small = render_card(sample_fields(), sizes={"name": 30, "company": 18, "company_en": 14})
        large = render_card(sample_fields(), sizes={"name": 70, "company": 45, "company_en": 30})
        self.assertNotEqual(small.tobytes(), large.tobytes())

    def test_logo_scale_changes_output(self):
        logo = Image.new("RGBA", (60, 40), (0, 128, 0, 255))
        small = render_card(sample_fields(), logo=logo, logo_layout={"scale": 0.6})
        large = render_card(sample_fields(), logo=logo, logo_layout={"scale": 1.8})
        self.assertNotEqual(small.tobytes(), large.tobytes())

    def test_all_logo_positions_render(self):
        logo = Image.new("RGBA", (60, 40), (0, 128, 0, 255))
        for pos in ("top-left", "center", "top-right"):
            with self.subTest(pos=pos):
                image = render_card(
                    sample_fields(), logo=logo, logo_layout={"position": pos}
                )
                self.assertEqual(image.size, (CARD_W, CARD_H))

    def test_all_icons_render(self):
        for icon in ICON_CHOICES:
            with self.subTest(icon=icon):
                image = render_card(
                    sample_fields(),
                    icons={"phone": icon, "email": icon, "website": icon, "address": icon},
                )
                self.assertIsInstance(image, Image.Image)

    def test_icons_none_vs_phone_differ(self):
        none = render_card(sample_fields(), icons={"phone": "none"})
        phone = render_card(sample_fields(), icons={"phone": "phone"})
        self.assertNotEqual(none.tobytes(), phone.tobytes())

    def test_website_field_renders(self):
        with_web = render_card(sample_fields())
        no_web = render_card(dict(sample_fields(), website=""))
        self.assertNotEqual(with_web.tobytes(), no_web.tobytes())

    def test_gui_module_compiles(self):
        import py_compile

        gui_path = PROJECT_ROOT / "src" / "gui" / "card_gui.py"
        py_compile.compile(str(gui_path), doraise=True)


if __name__ == "__main__":
    unittest.main()
