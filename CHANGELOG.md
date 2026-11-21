# Changelog

> Author: AKO_studio

## [1.2.0] - 2026-11-21
### Changed
- GUI 由 Agent Card 表单改为简洁的**视觉名片生成器**：仅填公司名/姓名/职务/电话/邮箱/通讯地址 + Logo，选排版模板与色系，窗口内实时预览，保存 PNG

### Added
- `src/gui/card_render.py`：Pillow 名片绘制，8 种排版模板 × 12 套色系，中文渲染与 Logo 合成
- `tests/test_card_render.py`：覆盖全部模板/色系组合、非法输入、Logo、尺寸
- README 按 GUI（主用）+ CLI（保留）双能力重写

## [1.1.0] - 2026-11-21
### Added
- Tkinter 桌面 GUI（初版为 Agent Card 表单，v1.2.0 已被名片 GUI 替换）
- `run_gui.bat` 双击启动脚本（自动探测带 tkinter 的 Python）
- `src/core/form_config.py` 表单与配置互转，列表/映射字段支持类型化解析
- `src/core/card_generator.py` 抽取 `write_card()`，CLI 与 GUI 共用原子写入
- `tests/test_form_config.py` 覆盖表单转换与生成链路

---

## [1.0.0] - 2026-07-30
### Added
- Initial version with standard AKO agent structure
- CLI-driven operation support
- Basic configuration management
- Implemented config-driven Agent Card YAML generation with validation and CLI override
- Replaced structural-only tests with functional and end-to-end tests

---
> Author: AKO_studio
