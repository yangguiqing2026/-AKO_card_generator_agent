# Ako Card Generator

> Author: AKO_studio
> Version: 1.2.0
> Date: 2026-11-21

两套能力：

1. **桌面名片生成器（GUI，主用）**：填写公司/姓名/职务/电话/邮箱/通讯地址 + Logo，选排版模板与色系，窗口内实时预览，一键保存 PNG。
2. **AKO Agent Card（CLI）**：配置驱动的 Agent Card YAML 生成工具，供 AKO fleet 注册与检索。

## 一、桌面名片生成器（GUI）

无需常驻服务，需要时双击拉起。项目根目录的 `run_gui.bat` 自动寻找带 Tkinter 的 Python 并以无控制台方式启动。

```text
双击 run_gui.bat
# 或手动指定带 tkinter + pillow 的解释器：
py -3.12 src/gui/card_gui.py
```

界面字段：

- 公司名（中/英）、姓名、职务、电话、邮箱、网址、通讯地址
- Logo（可选，选择图片即时合成到名片，可调位置与大小）
- 排版模板（8 种）：经典 / 简约 / 色块 / 双色 / 竖排 / 极简 / 商务 / 优雅
- 色系（12 套）：深蓝 / 森林绿 / 炭灰 / 藏青金 / 酒红金 / 石板蓝 / 青碧 / 梅紫 / 克莱因蓝 / 陶土橙 / 暖金 / 黑银
- 联系方式图标（电话/信封/地球/定位/链接/无）与字体字号
- 保存路径（可改），可浏览选择

输入时右侧实时刷新预览；点「保存 PNG」按 1050×600 分辨率写出图片；「打开目录」定位到保存位置。

> 前置：GUI 依赖 Tkinter（Windows 安装 Python 勾选 tcl/tk）与 Pillow。本机默认 `python` 为 3.13 且不含 Tkinter，故 `run_gui.bat` 优先使用 Python 3.12（已装 Pillow）。

## 二、AKO Agent Card（CLI）

### 环境要求

- Python >= 3.9
- PyYAML >= 6.0

### 安装

```bash
python -m pip install -r requirements.txt
```

### 快速开始

```bash
# 使用默认配置，生成 AKO_agent_card.yaml
python src/core/main.py

# 显式指定配置与输出路径
python src/core/main.py --config config/AKO_card_generator_config.yaml --output AKO_agent_card.yaml

# 指定日志级别
python src/core/main.py --log-level DEBUG
```

生成结果默认写入当前工作目录下的 `AKO_agent_card.yaml`；`--output` 可覆盖配置中的 `output.path`。

### 配置格式

```yaml
agent:
  id: "AKO_card_generator"          # 必填
  name: "Ako Card Generator"        # 必填
  version: "1.0.0"                  # 必填
  author: "AKO_studio"              # 必填
  created_date: "2026-07-30"        # 必填
  status: "active"                  # 必填
  description: "..."                # 必填
  capabilities: []                  # 可选，列表
  dependencies: []                  # 可选，列表
  interfaces: {}                    # 可选，映射
  health_probe: {}                  # 可选，映射
  registry: {}                      # 可选，映射
  tags: []                          # 可选，列表
  log_level: "INFO"                 # 可选，CLI --log-level 优先

output:
  path: "AKO_agent_card.yaml"       # 可选，默认 AKO_agent_card.yaml
```

必填字段为空或类型不符时，程序报错并以退出码 1 结束，不会写出半成品文件。

## 测试

```bash
python -m unittest discover -s tests -v
```

## 文件结构

```
config/AKO_card_generator_config.yaml   Agent Card 配置输入
src/core/card_generator.py              配置加载、校验、卡片生成、原子写入
src/core/form_config.py                 表单 <-> 配置转换（CLI 辅助，可单测）
src/core/main.py                        CLI 入口
src/gui/card_gui.py                     简洁名片 GUI（Tkinter）
src/gui/card_render.py                  名片绘制（Pillow，模板 + 色系）
run_gui.bat                             双击启动名片 GUI
tests/test_core.py                      core 单元测试
tests/test_form_config.py               表单转换单元测试
tests/test_card_render.py               名片绘制单元测试
AKO_agent_card.yaml                     Agent Card 生成产物
AKO_business_card.png                   名片默认保存产物
```

---
> Author: AKO_studio
