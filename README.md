# 🌸 Hanasuki (花好き): The Self-Evolving Academic AI Butler

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-red.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Target: AAAI 2026](https://img.shields.io/badge/Research-AAAI%202026-blueviolet.svg)](https://aaai.org/Conferences/AAAI-26/)
[![Hardware: Optimized for 8GB VRAM](https://img.shields.io/badge/Hardware-RTX%205060%20Optimized-green.svg)](#)

> **“不仅仅是对话，更是逻辑的自我进化与知识坍塌的对抗。”**
>
> **Hanasuki** 是一个基于微内核架构的模块化智能管家系统。她致力于探索在**消费级硬件（RTX 5060 8GB）**环境下，如何通过算法架构升级，赋予本地小参数模型（<10B）超越其规模限制的逻辑严谨性与深度科研能力捏。

---

## 🏗️ 核心技术架构：HERO-A+

Hanasuki 的进化由 **HERO-A+ (Hierarchical Evolution & Reliability-Oriented RAG - Advanced)** 架构驱动，旨在彻底解决模型“科研偷懒”与“工具调用幻觉”捏。



### 1. 逻辑图谱双层索引 (LightRAG Implementation)
不同于传统的扁平 RAG，Hanasuki 将知识沉淀为**双层结构**：
* **微观事实层 (Local)**：捕捉实体间的精确三元组关联。
* **宏观综述层 (Global)**：利用社区发现算法自动生成领域知识综述，赋予模型“全局视野”，防止在处理复杂课题时断章取义捏。

### 2. 置信度驱动的犹豫机制 (Relign Protocol)
集成可靠性对齐技术。当模型发现搜索参数不确定或信息缺失时，不再编造，而是触发 **`clarify`** 动作，主动向内核寻求反馈，从而物理性消灭工具调用幻觉。

### 3. 自适应上下文逻辑锚定 (ACLA)
针对显存受限环境的记忆优化算法。系统根据逻辑图谱计算历史片段的锚定分数 $S_{anchor}$，确保核心论据永远驻留上下文：
$$S_{anchor} = \alpha \cdot \text{Recency} + \beta \cdot \text{GraphCentrality}$$

### 4. 显存节流与推理加速
* **KV Cache 4-bit 量化**：将 16k 上下文的显存占用压缩至 1GB 左右。
* **目标驱动路由**：自研模式下根据任务动机（代码/逻辑/搜索）动态分配计算权重捏。

---

## 📂 模块化结构 (Repository Structure)

```bash
Hanasuki/
├── core/                # 驱动内核 (推理引擎、记忆中枢、重排算法)
├── modules/             # 具身化插件 (Purify浏览器、Darwin代码沙箱等)
├── ui/                  # 基于 PyQt6 的磨砂玻璃感交互界面
├── data/                # 向量库与逻辑图谱持久化存储
├── workspace/           # 物理隔离的代码演化实验区
└── config.yaml          # 全局动力参数配置文件
