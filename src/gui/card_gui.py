# ============================================
# Author: AKO_studio
# Agent: AKO_card_generator
# Business card GUI (Tkinter + Pillow), product name: AKO_card_genenrator
# ============================================

import sys
from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.gui.card_render import (  # noqa: E402
    FONT_PRESETS,
    ICON_CHOICES,
    ICON_LABELS,
    PALETTES,
    TEMPLATE_LABELS,
    TEMPLATES,
    render_card,
)

APP_NAME = "AKO_card_genenrator"

FIELDS = ("company", "company_en", "name", "title", "phone", "email", "website", "address")
FIELD_LABELS = {
    "company": "公司名(中)",
    "company_en": "公司名(英)",
    "name": "姓名",
    "title": "职务",
    "phone": "电话",
    "email": "邮箱",
    "website": "网址",
    "address": "通讯地址",
}
CONTACT_FIELDS = ("phone", "email", "website", "address")
DEFAULT_ICONS = {"phone": "phone", "email": "mail", "website": "globe", "address": "pin"}

LOGO_POSITIONS = {
    "左对齐": "top-left", "居中": "center", "右对齐": "top-right",
}
PREVIEW_W = 560
PREVIEW_H = 320


class CardGui:
    """Form with basic info / text & logo / icon & style tabs; live PNG preview."""

    def __init__(self, root):
        self.root = root
        self.root.title("{} - AKO_studio".format(APP_NAME))
        self.root.geometry("1120x720")
        self.root.minsize(1000, 640)

        self.entries = {}
        self.icon_vars = {}
        self.logo_path = ""
        self.logo_var = tk.StringVar(value="未选择")

        self.template_var = tk.StringVar(value=TEMPLATES[0])
        self.palette_var = tk.StringVar(value="deep_blue")
        self.font_var = tk.StringVar(value="微软雅黑")
        self.size_company = tk.IntVar(value=30)
        self.size_company_en = tk.IntVar(value=22)
        self.size_name = tk.IntVar(value=53)
        self.logo_pos_var = tk.StringVar(value="左对齐")
        self.logo_scale = tk.DoubleVar(value=1.0)

        self.output_var = tk.StringVar(value=str(PROJECT_ROOT / "AKO_business_card.png"))
        self.status_var = tk.StringVar(value="就绪")
        self._preview_photo = None

        self._build_layout()
        self._refresh_preview()

    # ---------- layout ----------

    def _build_layout(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        notebook = ttk.Notebook(left)
        notebook.pack(fill=tk.BOTH, expand=True)

        self._tab_basic(notebook)
        self._tab_text_logo(notebook)
        self._tab_style(notebook)

        save_box = ttk.LabelFrame(left, text="保存", padding=8)
        save_box.pack(fill=tk.X, pady=(10, 0))
        ttk.Entry(save_box, textvariable=self.output_var).pack(fill=tk.X, pady=(0, 6))
        btn_row = ttk.Frame(save_box)
        btn_row.pack(fill=tk.X)
        ttk.Button(btn_row, text="浏览...", command=self.on_pick_output).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btn_row, text="保存 PNG", command=self.on_save).pack(side=tk.LEFT)

        # Right: preview + actions.
        right = ttk.Frame(main, padding=(12, 0, 0, 0))
        right.pack(side=tk.RIGHT, fill=tk.BOTH)

        preview_box = ttk.LabelFrame(right, text="预览", padding=10)
        preview_box.pack(fill=tk.BOTH, expand=True)
        self.preview_label = tk.Label(preview_box, background="#EFEFEF")
        self.preview_label.pack(fill=tk.BOTH, expand=True)

        actions = ttk.Frame(right, padding=(0, 10, 0, 0))
        actions.pack(fill=tk.X)
        ttk.Button(actions, text="刷新预览", command=self.on_preview).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(actions, text="打开目录", command=self.on_open_dir).pack(side=tk.LEFT)

        ttk.Label(right, textvariable=self.status_var, anchor=tk.W, padding=(0, 8, 0, 0)).pack(fill=tk.X)

        for var in self.entries.values():
            var.trace_add("write", self._on_change)

    def _tab_basic(self, notebook):
        tab = ttk.Frame(notebook, padding=10)
        notebook.add(tab, text="基本信息")
        for i, field in enumerate(FIELDS):
            ttk.Label(tab, text=FIELD_LABELS[field], width=12).grid(
                row=i, column=0, sticky="nw", padx=(0, 6), pady=5
            )
            if field == "address":
                addr = tk.Text(tab, height=3, wrap=tk.WORD)
                addr.grid(row=i, column=1, sticky="ew", pady=5)
                addr.bind("<KeyRelease>", self._on_change)
                setattr(self, "_text_{}".format(field), addr)
            else:
                var = tk.StringVar()
                self.entries[field] = var
                ttk.Entry(tab, textvariable=var).grid(row=i, column=1, sticky="ew", pady=5)
        tab.columnconfigure(1, weight=1)

    def _tab_text_logo(self, notebook):
        tab = ttk.Frame(notebook, padding=10)
        notebook.add(tab, text="文字与 Logo")

        box = ttk.LabelFrame(tab, text="字体与字号（像素）", padding=8)
        box.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(box, text="字体").grid(row=0, column=0, sticky="w", pady=4)
        font_combo = ttk.Combobox(
            box, textvariable=self.font_var, values=list(FONT_PRESETS), state="readonly", width=16
        )
        font_combo.grid(row=0, column=1, sticky="w", padx=(6, 0), pady=4)
        font_combo.bind("<<ComboboxSelected>>", self._on_change)

        for i, (label, var) in enumerate(
            (("公司中文大小", self.size_company),
             ("公司英文大小", self.size_company_en),
             ("姓名大小", self.size_name)), start=1
        ):
            ttk.Label(box, text=label).grid(row=i, column=0, sticky="w", pady=4)
            spin = ttk.Spinbox(box, from_=12, to=90, textvariable=var, width=8, command=self._on_change)
            spin.grid(row=i, column=1, sticky="w", padx=(6, 0), pady=4)
            spin.bind("<KeyRelease>", self._on_change)

        logobox = ttk.LabelFrame(tab, text="Logo", padding=8)
        logobox.pack(fill=tk.X)
        ttk.Label(logobox, text="图片").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Button(logobox, text="选择图片...", command=self.on_pick_logo).grid(row=0, column=1, sticky="w", pady=4)
        ttk.Label(logobox, textvariable=self.logo_var, foreground="#666").grid(row=1, column=1, sticky="w")

        ttk.Label(logobox, text="位置").grid(row=2, column=0, sticky="w", pady=4)
        pos_combo = ttk.Combobox(
            logobox, textvariable=self.logo_pos_var, values=list(LOGO_POSITIONS), state="readonly", width=16
        )
        pos_combo.grid(row=2, column=1, sticky="w", padx=(6, 0), pady=4)
        pos_combo.bind("<<ComboboxSelected>>", self._on_change)

        ttk.Label(logobox, text="大小").grid(row=3, column=0, sticky="w", pady=4)
        scale = ttk.Scale(logobox, from_=0.5, to=2.0, orient=tk.HORIZONTAL,
                          variable=self.logo_scale, command=self._on_change, length=160)
        scale.grid(row=3, column=1, sticky="w", padx=(6, 0), pady=4)

    def _tab_style(self, notebook):
        tab = ttk.Frame(notebook, padding=10)
        notebook.add(tab, text="图标与样式")

        iconbox = ttk.LabelFrame(tab, text="联系方式图标（选【无】不显示）", padding=8)
        iconbox.pack(fill=tk.X, pady=(0, 10))
        for i, field in enumerate(CONTACT_FIELDS):
            ttk.Label(iconbox, text=FIELD_LABELS[field], width=10).grid(row=i, column=0, sticky="w", pady=4)
            var = tk.StringVar(value=ICON_LABELS[DEFAULT_ICONS[field]])
            self.icon_vars[field] = var
            combo = ttk.Combobox(
                iconbox, textvariable=var, values=list(ICON_LABELS.values()), state="readonly", width=14
            )
            combo.grid(row=i, column=1, sticky="w", padx=(6, 0), pady=4)
            combo.bind("<<ComboboxSelected>>", self._on_change)

        stylebox = ttk.LabelFrame(tab, text="排版模板与色系", padding=8)
        stylebox.pack(fill=tk.X)
        ttk.Label(stylebox, text="排版模板").grid(row=0, column=0, sticky="w", pady=4)
        tpl_combo = ttk.Combobox(
            stylebox, textvariable=self.template_var, values=list(TEMPLATE_LABELS.values()),
            state="readonly", width=20,
        )
        tpl_combo.grid(row=0, column=1, sticky="w", padx=(6, 0), pady=4)
        tpl_combo.bind("<<ComboboxSelected>>", self._on_change)

        ttk.Label(stylebox, text="色系").grid(row=1, column=0, sticky="w", pady=4)
        pal_combo = ttk.Combobox(
            stylebox, textvariable=self.palette_var,
            values=[p["label"] for p in PALETTES.values()], state="readonly", width=20,
        )
        pal_combo.grid(row=1, column=1, sticky="w", padx=(6, 0), pady=4)
        pal_combo.bind("<<ComboboxSelected>>", self._on_change)

    # ---------- helpers ----------

    def _collect_fields(self):
        values = {}
        for field in FIELDS:
            widget = getattr(self, "_text_{}".format(field), None)
            if widget is not None:
                values[field] = widget.get("1.0", tk.END).strip()
            else:
                values[field] = self.entries[field].get()
        return values

    def _selected(self, var, mapping, default):
        label = var.get()
        for key, value in mapping.items():
            if value == label:
                return key
        return default

    def _selected_palette(self):
        label = self.palette_var.get()
        for key, meta in PALETTES.items():
            if meta["label"] == label:
                return key
        return next(iter(PALETTES))

    def _selected_icons(self):
        reverse = {label: key for key, label in ICON_LABELS.items()}
        return {
            field: reverse.get(self.icon_vars[field].get(), DEFAULT_ICONS[field])
            for field in CONTACT_FIELDS
        }

    def _render_image(self):
        font_path = FONT_PRESETS.get(self.font_var.get())
        return render_card(
            self._collect_fields(),
            template=self._selected(self.template_var, TEMPLATE_LABELS, TEMPLATES[0]),
            palette=self._selected_palette(),
            logo=self.logo_path or None,
            font_path=font_path,
            sizes={
                "company": self.size_company.get(),
                "company_en": self.size_company_en.get(),
                "name": self.size_name.get(),
            },
            logo_layout={
                "position": LOGO_POSITIONS.get(self.logo_pos_var.get(), "top-left"),
                "scale": self.logo_scale.get(),
            },
            icons=self._selected_icons(),
        )

    def _refresh_preview(self):
        try:
            image = self._render_image()
        except Exception as exc:  # noqa: BLE001
            self.status_var.set("预览失败: {}".format(exc))
            return
        thumb = image.copy()
        thumb.thumbnail((PREVIEW_W, PREVIEW_H), ImageTk.Image.LANCZOS)
        self._preview_photo = ImageTk.PhotoImage(thumb)
        self.preview_label.configure(image=self._preview_photo)
        self.status_var.set("预览已更新（{}×{}）".format(*image.size))

    # ---------- events ----------

    def _on_change(self, *_args):
        self._refresh_preview()

    def on_preview(self):
        self._refresh_preview()

    def on_pick_logo(self):
        path = filedialog.askopenfilename(
            title="选择 Logo 图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp"), ("所有文件", "*.*")],
        )
        if not path:
            return
        self.logo_path = path
        self.logo_var.set(Path(path).name)
        self._refresh_preview()

    def on_pick_output(self):
        path = filedialog.asksaveasfilename(
            title="保存名片 PNG", defaultextension=".png",
            filetypes=[("PNG 图片", "*.png"), ("所有文件", "*.*")],
            initialdir=str(PROJECT_ROOT),
            initialfile=Path(self.output_var.get()).name or "AKO_business_card.png",
        )
        if path:
            self.output_var.set(path)

    def _target_path(self):
        raw = self.output_var.get().strip()
        target = Path(raw) if raw else PROJECT_ROOT / "AKO_business_card.png"
        return target if target.is_absolute() else PROJECT_ROOT / target

    def on_save(self):
        target = self._target_path()
        try:
            image = self._render_image()
            target.parent.mkdir(parents=True, exist_ok=True)
            image.save(target, format="PNG")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("保存失败", str(exc), parent=self.root)
            self.status_var.set("保存失败: {}".format(exc))
            return
        self.status_var.set("已保存: {}".format(target))
        messagebox.showinfo("保存成功", "名片已保存:\n{}".format(target), parent=self.root)

    def on_open_dir(self):
        folder = self._target_path().parent
        if not folder.is_dir():
            folder = PROJECT_ROOT
        try:
            if sys.platform.startswith("win"):
                import os

                os.startfile(str(folder))  # noqa: S606
            elif sys.platform == "darwin":
                import subprocess

                subprocess.run(["open", str(folder)], check=False)
            else:
                import subprocess

                subprocess.run(["xdg-open", str(folder)], check=False)
            self.status_var.set("已打开目录: {}".format(folder))
        except OSError as exc:
            messagebox.showerror("打开失败", str(exc), parent=self.root)


def main():
    root = tk.Tk()
    CardGui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
