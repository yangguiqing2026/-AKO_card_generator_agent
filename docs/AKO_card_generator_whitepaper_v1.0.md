---
agent_id: "AKO_card_generator"
name: "Ako Card Generator"
version: "1.0.0"
author: "AKO_studio"
date: "2026-07-30"
status: "active"
tags:
  - "design"
  - "document"
---

# Ako Card Generator 白皮书 v1.0.0

> **Agent ID**: AKO_card_generator  
> **版本**: v1.0.0  
> **作者**: AKO_studio  
> **日期**: 2026-07-30  
> **状态**: active

---

## 一、概述

### 1.1 定位
Ako Card Generator Agent for AKO fleet。以配置文件为输入，生成结构统一、可供 AKO fleet 注册与检索的 Agent Card（YAML）。

### 1.2 状态说明
> 核心生成能力已实现：配置加载、必填字段校验、Agent Card YAML 生成与原子落盘。HTTP 服务尚未提供，`health_probe` 仅作为声明字段写入卡片。

---

## 二、功能

- 从 `config/AKO_card_generator_config.yaml` 读取 Agent 元数据。
- 校验 `agent.id / name / version / author / created_date / status / description` 必填且非空。
- 校验列表型与映射型字段的类型，避免生成结构错误的卡片。
- 输出带 AKO 头注释的确定性 YAML，字段顺序稳定，便于版本比对。
- CLI 支持 `--config`、`--output`、`--log-level` 覆盖。

---

## 三、运行

```bash
python -m pip install -r requirements.txt
python src/core/main.py --config config/AKO_card_generator_config.yaml
python -m unittest discover -s tests -v
```

输出文件默认写入 `AKO_agent_card.yaml`。

---

## 四、版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-07-30 | 实验版本；后续补齐配置驱动生成、校验与测试 |

---
> 作者：AKO_studio
