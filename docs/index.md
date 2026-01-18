# 📚 文档索引

> **EdgeTTSdemo 实时语音助手系统 - 文档中心**
>
> 本索引提供项目所有文档的快速访问入口。文档按类型和用途组织，方便查找和使用。

---

## 📋 根目录文档

### [AUDIO_SETUP.md](./AUDIO_SETUP.md)

Orange Pi AI Pro 音频配置完全指南。详细说明如何配置录音设备（麦克风）和播放设备（耳机），包括 ALSA 配置、音量设置、设备测试和常见问题排查。这是实时语音助手系统的基础配置文档。

### [brownfield-architecture.md](./brownfield-architecture.md)

Brownfield 架构文档（v1.1），记录项目的真实状态。**Phase 1 已完成更新**：包含关键文件列表、技术栈分析（LLM、TTS、音频设备已验证）、项目结构说明、技术债务清单、已知问题、集成点、开发设置和故障排查指南。包含 Phase 1 完成后的性能数据和下一步行动指南。

### [implementation-plan.md](./implementation-plan.md)

详细实施计划，提供从头开始重建实时语音助手系统的分步指南。包含 5 个 Phase 的详细任务分解，每个任务都有具体的执行步骤、验收标准和故障处理建议。这是项目实施的操作手册。

### [prd.md](./prd.md)

产品需求文档（PRD），定义项目目标、范围和验收标准。包含当前状态分析、核心功能需求（6 个 Epic）、实施路线图（5 个 Phase）、技术架构、性能指标和风险分析。这是项目的需求规格说明。

### [REALTIME_ASSISTANT.md](./REALTIME_ASSISTANT.md)

实时语音助手系统设计方案。详细描述系统架构、核心模块（VAD、ASR、LLM、TTS）、技术选型、性能指标、使用指南和开发路线图。这是系统的技术设计文档。

---

## 📖 Stories

用户故事文档，描述具体的功能需求和实施细节。

### [1.1-audio-device-setup.md](./stories/1.1-audio-device-setup.md)

Story 1.1: 音频设备配置和测试。**状态：Done** ✅ Epic 1（基础设施）的第一个故事，定义音频设备配置的验收标准、技术细节、测试要点、实施步骤和常见问题。包含 4 大类验收标准（共 16 个检查点全部完成）和 8 个详细实施步骤。完成日期：2026-01-18。

---

## 🔍 QA (质量保证)

质量保证相关文档，包括测试报告和质量门控。

### Gates (质量门控)

质量门控文件，记录每个 Story 的质量评审结果。

#### [1.1-audio-device-setup.yml](./qa/gates/1.1-audio-device-setup.yml)

Story 1.1 的质量门控文件。**当前状态：PASS** ✅ 所有验收标准已通过，音频设备配置和测试完成。录音和播放功能正常，音质清晰无杂音。评审人：Quinn，更新时间：2026-01-18 16:45。

---

## 📂 文档组织说明

### 文档类型

- **根目录文档**：核心技术文档，包括架构、设计、配置和实施计划
- **Stories**：用户故事，描述具体的功能需求和实施细节
- **QA**：质量保证文档，包括测试报告和质量门控

### 文档关系

```
prd.md (需求)
    ↓
brownfield-architecture.md (现状分析)
    ↓
implementation-plan.md (实施计划)
    ↓
stories/*.md (具体任务)
    ↓
qa/gates/*.yml (质量门控)
```

### 推荐阅读顺序

**新手入门：**
1. `prd.md` - 了解项目目标和范围
2. `brownfield-architecture.md` - 了解项目现状
3. `AUDIO_SETUP.md` - 配置音频设备（第一步）
4. `implementation-plan.md` - 开始实施

**开发者：**
1. `brownfield-architecture.md` - 了解技术架构
2. `REALTIME_ASSISTANT.md` - 了解系统设计
3. `stories/1.1-audio-device-setup.md` - 开始第一个任务
4. `implementation-plan.md` - 参考详细步骤

**项目管理：**
1. `prd.md` - 了解需求和验收标准
2. `implementation-plan.md` - 了解实施计划
3. `qa/gates/*.yml` - 跟踪质量状态

---

## 🔗 快速链接

### 核心文档
- [PRD](./prd.md) - 产品需求文档
- [架构文档](./brownfield-architecture.md) - 项目现状分析
- [实施计划](./implementation-plan.md) - 详细实施步骤

### 配置指南
- [音频配置](./AUDIO_SETUP.md) - 音频设备配置教程
- [系统设计](./REALTIME_ASSISTANT.md) - 系统架构设计

### 任务跟踪
- [Story 1.1](./stories/1.1-audio-device-setup.md) - 音频设备配置任务
- [质量门控](./qa/gates/1.1-audio-device-setup.yml) - Story 1.1 质量状态

---

## 📊 文档统计

- **总文档数**：7 个 Markdown 文档 + 1 个 YAML 文件
- **根目录文档**：6 个（包括索引）
- **Stories**：1 个（已完成）
- **质量门控**：1 个（PASS）

### 项目进度

- ✅ **Phase 1 完成**：音频设备、LLM、TTS 已验证
- 🔲 **Phase 2 待开始**：ASR 集成
- 📊 **完成率**：Story 1/N 完成

---

## 🔄 文档维护

### 更新频率
- **PRD**：需求变更时更新
- **架构文档**：技术栈或结构变化时更新
- **实施计划**：每个 Phase 完成后更新
- **Stories**：任务状态变化时更新
- **质量门控**：评审完成后更新

### 维护责任
- **文档创建者**：哈雷酱（傲娇大小姐工程师）
- **最后更新**：2026-01-18
- **索引版本**：v1.0.0

---

**索引创建者：** 哈雷酱（傲娇大小姐工程师）
**创建日期：** 2026-01-18
**最后更新：** 2026-01-18 16:50
**索引版本：** v1.1 - Phase 1 完成后更新

---

## 💡 使用提示

1. **查找文档**：使用浏览器的搜索功能（Ctrl+F）快速定位
2. **导航**：点击文档标题直接跳转到对应文件
3. **更新索引**：添加新文档后，运行 `/index-docs` 命令更新索引
4. **报告问题**：发现链接失效或描述不准确，请及时反馈

哼，本小姐创建的索引可是非常专业和详细的！(￣▽￣)ノ
