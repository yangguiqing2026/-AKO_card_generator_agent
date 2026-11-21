# ============================================
# Author: AKO_studio
# Agent: AKO_card_generator
# Business card rendering (Pillow), template + palette driven
# Layout/palette ideas collected from GitHub & web business-card designs:
#   - GitHub: business-card-designer (left/center/right layouts; font & color presets)
#   - Web: minimal / centered / color-block / vertical / logo-dominant layouts
#   - Web: navy+gold, charcoal+gold, forest+ivory, burgundy+gold, etc. palettes
# ============================================

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

CARD_W = 1050
CARD_H = 600

# ---------- templates ----------

TEMPLATES = ("classic", "centered", "banner", "split", "vertical", "minimal", "corporate", "elegant")
TEMPLATE_LABELS = {
    "classic": "经典（左对齐）",
    "centered": "简约（居中）",
    "banner": "色块（横幅）",
    "split": "双色（左右分栏）",
    "vertical": "竖排（信息靠右）",
    "minimal": "极简（细线框）",
    "corporate": "商务（顶栏+底线）",
    "elegant": "优雅（深色底）",
}

# ---------- palettes (hex) ----------
# Each: bg, primary (color block), heading, body, rule, on_primary
PALETTES = {
    "deep_blue": {
        "label": "深蓝", "bg": "#FFFFFF", "primary": "#1F3A5F",
        "heading": "#1F3A5F", "body": "#44515E", "rule": "#C7D2DE",
        "on_primary": "#FFFFFF",
    },
    "forest": {
        "label": "森林绿", "bg": "#FFFFFF", "primary": "#1F3D2E",
        "heading": "#1E4636", "body": "#4A5B53", "rule": "#C3D2C9",
        "on_primary": "#F2EDE3",
    },
    "charcoal": {
        "label": "炭灰", "bg": "#FBFBFA", "primary": "#2B2B2B",
        "heading": "#1A1A1A", "body": "#4F4F4F", "rule": "#C9C9C9",
        "on_primary": "#FFFFFF",
    },
    "navy_gold": {
        "label": "藏青金", "bg": "#FFFFFF", "primary": "#16294A",
        "heading": "#16294A", "body": "#4A5563", "rule": "#C8A24A",
        "on_primary": "#C8A24A",
    },
    "burgundy_gold": {
        "label": "酒红金", "bg": "#FFFFFF", "primary": "#6E1F2B",
        "heading": "#5E202B", "body": "#5B464A", "rule": "#C8A24A",
        "on_primary": "#E8D4A8",
    },
    "slate": {
        "label": "石板蓝", "bg": "#F7F9FB", "primary": "#3B5A73",
        "heading": "#2E485D", "body": "#4C5C68", "rule": "#C2CEDA",
        "on_primary": "#FFFFFF",
    },
    "teal": {
        "label": "青碧", "bg": "#F5FBFA", "primary": "#134E4A",
        "heading": "#134E4A", "body": "#3E5F5C", "rule": "#BFD8D3",
        "on_primary": "#FFFFFF",
    },
    "plum": {
        "label": "梅紫", "bg": "#FBF8FC", "primary": "#401940",
        "heading": "#401940", "body": "#57465A", "rule": "#D9A6A6",
        "on_primary": "#F0DCE0",
    },
    "klein_blue": {
        "label": "克莱因蓝", "bg": "#FFFFFF", "primary": "#1B3FA0",
        "heading": "#1B3FA0", "body": "#3F4A66", "rule": "#B9C6E8",
        "on_primary": "#FFFFFF",
    },
    "terracotta": {
        "label": "陶土橙", "bg": "#FFFCF7", "primary": "#C05A3E",
        "heading": "#A94A31", "body": "#5C4A42", "rule": "#E0C4B6",
        "on_primary": "#FFF4EC",
    },
    "gold": {
        "label": "暖金", "bg": "#FFFCF4", "primary": "#8A6A2F",
        "heading": "#6E5422", "body": "#5C533F", "rule": "#DCCDA6",
        "on_primary": "#FFFFFF",
    },
    "black_silver": {
        "label": "黑银", "bg": "#111111", "primary": "#C7CBD1",
        "heading": "#FFFFFF", "body": "#C7CBD1", "rule": "#4A4A4A",
        "on_primary": "#111111",
    },
}

# ---------- fonts ----------
FONT_PRESETS = {
    "微软雅黑": "C:/Windows/Fonts/msyh.ttc",
    "微软雅黑粗": "C:/Windows/Fonts/msyhbd.ttc",
    "黑体": "C:/Windows/Fonts/simhei.ttf",
    "宋体": "C:/Windows/Fonts/simsun.ttc",
    "等线": "C:/Windows/Fonts/Deng.ttf",
}
FONT_CANDIDATES = tuple(FONT_PRESETS.values())

# ---------- icons ----------
ICON_CHOICES = ("none", "phone", "mail", "globe", "pin", "link")
ICON_LABELS = {
    "none": "无", "phone": "电话", "mail": "信封",
    "globe": "地球", "pin": "定位", "link": "链接",
}

REQUIRED_FIELDS = ("company", "name", "title", "phone", "email", "address")


def _rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def find_font(size, bold=False, font_path=None):
    """Return a truetype font; prefer explicit path, then Chinese-capable fonts."""
    if font_path:
        try:
            return ImageFont.truetype(font_path, size)
        except (OSError, ValueError):
            pass
    for path in FONT_CANDIDATES:
        if Path(path).is_file():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def load_logo(path, max_size=(240, 200)):
    """Load a logo image, returning an RGBA image scaled to fit max_size."""
    if not path:
        return None
    logo = Image.open(path).convert("RGBA")
    logo.thumbnail(max_size, Image.LANCZOS)
    return logo


def _text(draw, xy, text, font, fill, anchor=None):
    draw.text(xy, text or "", font=font, fill=_rgb(fill), anchor=anchor)


def _field(fields, key):
    return str(fields.get(key, "") or "").strip()


def _draw_icon(draw, cx, cy, kind, size, color):
    """Draw a small vector icon centered at (cx, cy). No-op for 'none'."""
    if kind == "none" or kind not in ICON_CHOICES:
        return
    c = _rgb(color)
    r = size / 2.0
    w = max(1, int(size * 0.10))
    box = [cx - r, cy - r, cx + r, cy + r]
    if kind == "phone":
        draw.arc(box, 130, 185, fill=c, width=w)
        draw.arc(box, 310, 365, fill=c, width=w)
        draw.line([(cx - r * 0.6, cy - r * 0.6), (cx + r * 0.6, cy + r * 0.6)], fill=c, width=w)
    elif kind == "mail":
        draw.rectangle(box, outline=c, width=w)
        draw.line([(cx - r, cy - r), (cx, cy + r * 0.15), (cx + r, cy - r)], fill=c, width=w)
    elif kind == "globe":
        draw.ellipse(box, outline=c, width=w)
        draw.line([(cx - r, cy), (cx + r, cy)], fill=c, width=w)
        draw.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r], outline=c, width=w)
    elif kind == "pin":
        draw.ellipse([cx - r * 0.75, cy - r * 0.75, cx + r * 0.75, cy + r * 0.75], outline=c, width=w)
        draw.polygon(
            [(cx - r * 0.4, cy + r * 0.4), (cx, cy + r * 1.15), (cx + r * 0.4, cy + r * 0.4)],
            outline=c,
        )
    elif kind == "link":
        draw.rounded_rectangle(
            [cx - r, cy - r * 0.5, cx + r * 0.25, cy + r * 0.5], radius=r * 0.5, outline=c, width=w
        )
        draw.rounded_rectangle(
            [cx - r * 0.25, cy - r * 0.5, cx + r, cy + r * 0.5], radius=r * 0.5, outline=c, width=w
        )


def _contact_lines(fields, icons, draw, x, y, body_font, colors, line_gap, icon_size):
    """Draw phone/email/address rows with optional leading icons. Returns new y."""
    mapping = (
        ("phone", "phone"), ("email", "mail"),
        ("website", "globe"), ("address", "pin"),
    )
    for key, default_icon in mapping:
        value = _field(fields, key)
        if not value:
            continue
        icon_kind = (icons or {}).get(key, default_icon)
        if icon_kind != "none":
            _draw_icon(draw, x + icon_size / 2, y + body_font.size * 0.55, icon_kind, icon_size, colors["primary"])
            _text(draw, (x + icon_size + int(icon_size * 0.4), y), value, body_font, colors["body"])
        else:
            _text(draw, (x, y), value, body_font, colors["body"])
        y += line_gap
    return y


def _fonts(h, sizes, font_path):
    return {
        "name": find_font(int(sizes.get("name", h * 0.088)), bold=True, font_path=font_path),
        "company": find_font(int(sizes.get("company", h * 0.050)), bold=True, font_path=font_path),
        "company_en": find_font(int(sizes.get("company_en", h * 0.036)), font_path=font_path),
        "title": find_font(int(h * 0.040), font_path=font_path),
        "body": find_font(int(h * 0.032), font_path=font_path),
        "icon": int(h * 0.032),
    }


def _place_logo(image, logo, position, anchor_xy, align_hint=None):
    """Place logo near anchor_xy based on a coarse position hint; return bottom y."""
    x, y = anchor_xy
    pos = (position or "top-left").lower()
    if align_hint == "center" or pos.startswith("center"):
        x = x - logo.width // 2
    elif pos.startswith("right"):
        x = x - logo.width
    image.paste(logo, (int(x), int(y)), logo)
    return y + logo.height


def render_card(
    fields,
    template="classic",
    palette="deep_blue",
    logo=None,
    size=None,
    font_path=None,
    sizes=None,
    logo_layout=None,
    icons=None,
):
    """Render a business card to a PIL Image (RGB).

    sizes: dict with company/company_en/name pixel sizes.
    logo_layout: dict with scale (float) and position string.
    icons: dict phone/email/address -> ICON_CHOICES value ('none' = no icon).
    """
    if template not in TEMPLATES:
        raise ValueError("未知排版模板: {}".format(template))
    if palette not in PALETTES:
        raise ValueError("未知色系: {}".format(palette))

    width, height = size or (CARD_W, CARD_H)
    colors = PALETTES[palette]
    sizes = sizes or {}
    logo_layout = logo_layout or {}

    image = Image.new("RGB", (width, height), _rgb(colors["bg"]))
    draw = ImageDraw.Draw(image)

    logo_img = load_logo(logo) if isinstance(logo, (str, Path)) else logo

    scale = float(logo_layout.get("scale", 1.0) or 1.0)
    if logo_img is not None and abs(scale - 1.0) > 1e-6:
        nw = max(1, int(logo_img.width * scale))
        nh = max(1, int(logo_img.height * scale))
        logo_img = logo_img.resize((nw, nh), Image.LANCZOS)

    common = dict(
        image=image, draw=draw, fields=fields, colors=colors, logo=logo_img,
        font_path=font_path, sizes=sizes, logo_layout=logo_layout, icons=icons,
    )

    renderer = {
        "classic": _render_classic, "centered": _render_centered,
        "banner": _render_banner, "split": _render_split,
        "vertical": _render_vertical, "minimal": _render_minimal,
        "corporate": _render_corporate, "elegant": _render_elegant,
    }[template]
    renderer(**common)
    return image


def _name_block(draw, x, y, fields, f, colors, show_company=True):
    """Draw company(+en)/name/title block; return new y."""
    if show_company:
        _text(draw, (x, y), _field(fields, "company"), f["company"], colors["primary"])
        y += f["company"].size + int(f["company"].size * 0.06)
        if _field(fields, "company_en"):
            _text(draw, (x, y), _field(fields, "company_en"), f["company_en"], colors["body"])
            y += f["company_en"].size + int(f["company_en"].size * 0.2)
        y += int(f["name"].size * 0.12)
    _text(draw, (x, y), _field(fields, "name"), f["name"], colors["heading"])
    y += f["name"].size + int(f["name"].size * 0.14)
    _text(draw, (x, y), _field(fields, "title"), f["title"], colors["body"])
    return y + f["title"].size


def _render_classic(image, draw, fields, colors, logo, font_path, sizes, logo_layout, icons):
    w, h = image.size
    pad, left = int(h * 0.11), int(h * 0.13)
    f = _fonts(h, sizes, font_path)

    logo_h = (logo.height + int(h * 0.025)) if logo else 0
    y = pad + logo_h
    if logo is not None:
        y = _place_logo(image, logo, logo_layout.get("position"), (left, pad)) + int(h * 0.025)

    y = _name_block(draw, left, y, fields, f, colors)
    y += int(h * 0.06)
    draw.line([(left, y), (w - pad, y)], fill=_rgb(colors["rule"]), width=max(1, h // 300))
    y += int(h * 0.05)
    _contact_lines(fields, icons, draw, left, y, f["body"], colors, int(h * 0.085), f["icon"])
    draw.rectangle([0, 0, max(2, w // 260), h], fill=_rgb(colors["primary"]))


def _render_centered(image, draw, fields, colors, logo, font_path, sizes, logo_layout, icons):
    w, h = image.size
    cx = w // 2
    f = _fonts(h, sizes, font_path)
    pad = int(h * 0.06)

    y = pad
    if logo is not None:
        y = _place_logo(image, logo, logo_layout.get("position"), (cx, pad), align_hint="center") + int(h * 0.025)

    _text(draw, (cx, y), _field(fields, "company"), f["company"], colors["primary"], anchor="ma")
    y += f["company"].size + int(f["company"].size * 0.06)
    if _field(fields, "company_en"):
        _text(draw, (cx, y), _field(fields, "company_en"), f["company_en"], colors["body"], anchor="ma")
        y += f["company_en"].size + int(f["company_en"].size * 0.2)
    y += int(f["name"].size * 0.12)
    _text(draw, (cx, y), _field(fields, "name"), f["name"], colors["heading"], anchor="ma")
    y += f["name"].size + int(f["name"].size * 0.14)
    _text(draw, (cx, y), _field(fields, "title"), f["title"], colors["body"], anchor="ma")
    y += f["title"].size + int(h * 0.05)

    half = int(w * 0.12)
    draw.line([(cx - half, y), (cx + half, y)], fill=_rgb(colors["rule"]), width=max(1, h // 300))
    y += int(h * 0.05)

    for key, default_icon in (
        ("phone", "phone"), ("email", "mail"),
        ("website", "globe"), ("address", "pin"),
    ):
        value = _field(fields, key)
        if not value:
            continue
        kind = (icons or {}).get(key, default_icon)
        if kind != "none":
            tw = int(draw.textlength(value, font=f["body"]))
            total = f["icon"] + int(f["icon"] * 0.4) + tw
            start = cx - total // 2
            _draw_icon(draw, start + f["icon"] // 2, y + f["body"].size * 0.55, kind, f["icon"], colors["primary"])
            _text(draw, (start + f["icon"] + int(f["icon"] * 0.4), y), value, f["body"], colors["body"])
        else:
            _text(draw, (cx, y), value, f["body"], colors["body"], anchor="ma")
        y += int(h * 0.075)

    draw.rectangle([0, 0, w - 1, h - 1], outline=_rgb(colors["primary"]), width=max(1, h // 200))


def _render_banner(image, draw, fields, colors, logo, font_path, sizes, logo_layout, icons):
    w, h = image.size
    banner_h = int(h * 0.36)
    pad = int(h * 0.09)
    f = _fonts(h, sizes, font_path)

    draw.rectangle([0, 0, w, banner_h], fill=_rgb(colors["primary"]))
    x = pad
    if logo is not None:
        ly = (banner_h - logo.height) // 2
        pos = (logo_layout.get("position") or "").lower()
        if pos.endswith("right"):
            x = w - pad - logo.width
            image.paste(logo, (x, ly), logo)
            x = pad
        else:
            image.paste(logo, (x, ly), logo)
            x += logo.width + pad

    by = int(banner_h * 0.12)
    _text(draw, (x, by), _field(fields, "company"), f["company"], colors["on_primary"])
    by += f["company"].size + int(banner_h * 0.035)
    if _field(fields, "company_en"):
        _text(draw, (x, by), _field(fields, "company_en"), f["company_en"], colors["on_primary"])
        by += f["company_en"].size + int(banner_h * 0.03)
    _text(draw, (x, by), _field(fields, "name"), f["name"], colors["on_primary"])

    y = banner_h + int(h * 0.08)
    _text(draw, (pad, y), _field(fields, "title"), f["title"], colors["heading"])
    y += f["title"].size + int(h * 0.07)
    _contact_lines(fields, icons, draw, pad, y, f["body"], colors, int(h * 0.10), f["icon"])


def _render_split(image, draw, fields, colors, logo, font_path, sizes, logo_layout, icons):
    w, h = image.size
    split = int(w * 0.36)
    f = _fonts(h, sizes, font_path)

    draw.rectangle([0, 0, split, h], fill=_rgb(colors["primary"]))
    x, y = int(split * 0.12), int(h * 0.12)
    max_text_w = split - 2 * x
    if logo is not None:
        image.paste(logo, (x, y), logo)
        y += logo.height + int(h * 0.06)

    def fit_font(text, font, base_size):
        """Shrink font until text fits the left color block."""
        size = base_size
        while size > 10 and draw.textlength(text, font=font) > max_text_w:
            size -= 2
            font = find_font(size, font_path=font_path)
        return font

    _text(draw, (x, y), _field(fields, "company"),
          fit_font(_field(fields, "company"), f["company"], f["company"].size), colors["on_primary"])
    y += f["company"].size + int(h * 0.01)
    if _field(fields, "company_en"):
        en_font = fit_font(_field(fields, "company_en"), f["company_en"], f["company_en"].size)
        _text(draw, (x, y), _field(fields, "company_en"), en_font, colors["on_primary"])

    rx = split + int(h * 0.10)
    ry = int(h * 0.14)
    _text(draw, (rx, ry), _field(fields, "name"), f["name"], colors["heading"])
    ry += f["name"].size + int(h * 0.02)
    _text(draw, (rx, ry), _field(fields, "title"), f["title"], colors["body"])
    ry += f["title"].size + int(h * 0.07)
    draw.line([(rx, ry), (w - int(h * 0.10), ry)], fill=_rgb(colors["rule"]), width=max(1, h // 300))
    ry += int(h * 0.05)
    _contact_lines(fields, icons, draw, rx, ry, f["body"], colors, int(h * 0.085), f["icon"])


def _render_vertical(image, draw, fields, colors, logo, font_path, sizes, logo_layout, icons):
    w, h = image.size
    bar = int(h * 0.16)
    f = _fonts(h, sizes, font_path)

    draw.rectangle([w - bar, 0, w, h], fill=_rgb(colors["primary"]))
    pad = int(h * 0.11)
    y = pad
    if logo is not None:
        image.paste(logo, (pad, y), logo)
        y += logo.height + int(h * 0.03)

    y = _name_block(draw, pad, y, fields, f, colors)
    y += int(h * 0.05)
    _contact_lines(fields, icons, draw, pad, y, f["body"], colors, int(h * 0.075), f["icon"])


def _render_minimal(image, draw, fields, colors, logo, font_path, sizes, logo_layout, icons):
    w, h = image.size
    f = _fonts(h, sizes, font_path)
    pad = int(h * 0.10)

    draw.rectangle([pad // 2, pad // 2, w - pad // 2 - 1, h - pad // 2 - 1],
                   outline=_rgb(colors["rule"]), width=max(1, h // 400))

    x, y = pad, pad
    if logo is not None:
        image.paste(logo, (x, y), logo)
        y += logo.height + int(h * 0.02)
    y = _name_block(draw, x, y, fields, f, colors)

    rx = int(w * 0.56)
    ry = pad + int(h * 0.05)
    _contact_lines(fields, icons, draw, rx, ry, f["body"], colors, int(h * 0.085), f["icon"])
    draw.rectangle([pad, h - pad // 2 - int(h * 0.012), w - pad, h - pad // 2 - int(h * 0.012) + max(1, h // 300)],
                   fill=_rgb(colors["primary"]))


def _render_corporate(image, draw, fields, colors, logo, font_path, sizes, logo_layout, icons):
    w, h = image.size
    bar = int(h * 0.12)
    f = _fonts(h, sizes, font_path)

    draw.rectangle([0, 0, w, bar], fill=_rgb(colors["primary"]))
    draw.rectangle([0, h - max(2, h // 100), w, h], fill=_rgb(colors["primary"]))

    x, y = int(h * 0.11), int(h * 0.18)
    if logo is not None:
        image.paste(logo, (x, y), logo)
        y += logo.height + int(h * 0.025)
    y = _name_block(draw, x, y, fields, f, colors, show_company=True)

    rx = int(w * 0.55)
    ry = int(h * 0.20)
    _contact_lines(fields, icons, draw, rx, ry, f["body"], colors, int(h * 0.085), f["icon"])


def _render_elegant(image, draw, fields, colors, logo, font_path, sizes, logo_layout, icons):
    w, h = image.size
    f = _fonts(h, sizes, font_path)
    pad = int(h * 0.12)

    draw.rectangle([0, 0, w, h], fill=_rgb(colors["primary"]))
    # On a dark ground all text/icons must use the light "on_primary" tone.
    light = dict(colors)
    light["primary"] = colors["on_primary"]
    light["heading"] = colors["on_primary"]
    light["body"] = colors["on_primary"]
    rule_color = colors["rule"]

    x, y = pad, pad
    if logo is not None:
        image.paste(logo, (x, y), logo)
        y += logo.height + int(h * 0.03)
    y = _name_block(draw, x, y, fields, f, light)

    draw.line([(x, y), (w - pad, y)], fill=_rgb(rule_color), width=max(1, h // 300))
    y += int(h * 0.05)
    _contact_lines(fields, icons, draw, x, y, f["body"], light, int(h * 0.08), f["icon"])
