# 🌸 Hanasuki (花好き) AI Kernel - Beta 1.1

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-GPL%20v3-red)
![Architecture](https://img.shields.io/badge/Architecture-HERO--A%2B-purple)
![Status](https://img.shields.io/badge/Status-Beta%201.1-orange)

> **"不仅仅是对话，而是关于具身逻辑的自我演化。"**
>
> Hanasuki Beta 1.1 是一个基于 **HERO-A+** 架构的模块化智能管家。她专为受限硬件（如 **RTX 5060 8GB**）优化，通过 **ACLA 上下文锚定** 与 **LightRAG 双层逻辑图谱**，在本地端构建起一套具备“自研、自省、演化”能力的认知闭环捏。

---

## 🏗️ 核心架构 (HERO-A+ Architecture)

Hanasuki 采用高度解耦的微内核设计，在 Beta 1.1 中全面实装了 **HERO-A+** 协议：

* **ACLA (Adaptive Contextual Logic Anchoring)**: 动态计算上下文权重捏。通过公式 $S_{anchor} = 0.4 \cdot Recency + 0.6 \cdot \frac{Weight}{Threshold}$ 物理锁定核心逻辑节点，防止关键科研信息在长对话中丢失。
* **Relign Protocol (犹豫机制)**: 强制执行“不确定性拦截”。模型在工具参数模糊时会自动触发 `clarify` 指令，拒绝产生学术幻觉捏。
* **具身演化实验室**: 集成 `darwin_coder` 与 `python_executor`。支持在独立沙箱中编写、验证并持久化演化逻辑，实现真正的“逻辑自增长”捏。

---

## 🧠 双轨记忆系统 (Dual-Track Memory)

为了在 8GB 显存下实现类人的长期记忆，我们构建了以下系统：

### 1. 感性语义记忆 (Vector-RAG)
* **引擎**: [LanceDB](https://lancedb.com/)
* **优化**: 强制模型运行于 CPU，通过 Cosine Similarity 检索语义片段，不占用推理显存捏。

### 2. 理性逻辑图谱 (LightRAG)
* **引擎**: [NetworkX](https://networkx.org/)
* **创新**: 实装 **Local + Global** 双层索引。自动聚类知识簇并生成高层摘要，解决 8B 模型“不见森林”的局限性捏。

---

## ⚙️ 硬件适配与显存优化 (VRAM Guard)

针对 **RTX 5060 (8GB)** 优化的显存管理方案：

| 显存容量 | 推荐 Profile | KV Cache 量化 | 优化策略 |
| :--- | :--- | :--- | :--- |
| **6GB** | Normal (2k) | Q4_K | 强制混合计算，限制 GPU 层数捏 |
| **8GB** | **Learning (16k)** | **Q4_K (Active)** | **全显存加速，激活 ACLA 锚定逻辑** |
| **12GB+** | Turbo (32k) | Q8_0 | 极致推理体验，支持 14B+ 模型捏 |

---

## 🚀 快速开始 (Quick Start)

### 1. 安装环境
```bash
pip install -r requirements.txt
playwright install chromium  # 激活学术搜索模块捏