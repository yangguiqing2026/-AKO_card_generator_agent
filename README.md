# Ako Card Generator

> Author: AKO_studio
> Version: 1.0.0
> Date: 2026-07-30

配置驱动的 AKO Agent Card（YAML）生成工具。读取 `config/AKO_card_generator_config.yaml`，校验后生成可注册到 AKO fleet 的 Agent Card 文件。

## 环境要求

- Python >= 3.9
- PyYAML >= 6.0

## 安装

```bash
python -m pip install -r requirements.txt
```

## 快速开始

在项目根目录执行：

```bash
# 使用默认配置，生成 AKO_agent_card.yaml
python src/core/main.py

# 显式指定配置与输出路径
python src/core/main.py --config config/AKO_card_generator_config.yaml --output AKO_agent_card.yaml

# 指定日志级别
python src/core/main.py --log-level DEBUG
```

生成结果默认写入当前工作目录下的 `AKO_agent_card.yaml`；`--output` 可覆盖配置中的 `output.path`。

## 配置格式

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

必填字段为空或类型不符时，程序会报错并以退出码 1 结束，不会写出半成品文件。

## 测试

```bash
python -m unittest discover -s tests -v
```

## 文件结构

```
config/AKO_card_generator_config.yaml   配置输入
src/core/card_generator.py              配置加载、校验、卡片生成
src/core/main.py                        CLI 入口
tests/test_core.py                     单元测试
AKO_agent_card.yaml                    生成产物（本 Agent 的自描述卡）
```

---
> Author: AKO_studio
