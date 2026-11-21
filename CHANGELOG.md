# Changelog

> Author: AKO_studio

## [1.3.0] - 2026-11-21
### Added
- 公司英文名输入项，随名片渲染（可单独调字号）
- 字体可选（微软雅黑/黑体/宋体/等线等）与公司中文/英文/姓名字号调整
- Logo 位置（左/中/右）与大小（0.5～2.0 倍滑块）可调
- 网址字段，联系方式四栏（电话/邮箱/网址/地址）各自可选预设图标（电话/信封/地球/定位/链接/无）
- 排版模板由 3 种增至 8 种、色系由 6 套增至 12 套（参考 GitHub 与网上名片设计）
- GUI 改为三分页布局（基本信息 / 文字与 Logo / 图标与样式）

### Changed
- 产品名按 AKO 命名规范改为 `AKO_card_genenrator`（窗口标题、README 同步）
- 修复 split 模板英文公司名溢出色块、elegant 模板深色底文字对比度不足

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
