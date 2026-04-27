# tender-writer-v2

![License](https://img.shields.io/badge/License-MIT-blue.svg) ![Python](https://img.shields.io/badge/Python-3.11%2B-blue) ![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey) ![AI](https://img.shields.io/badge/AI-Claude%20Code%20%7C%20Cline-orange)

> 把政府类项目技术标的首轮结构化拆解与初稿组装压缩到分钟级;正式投标仍需人工扩写、校核和审稿。

<!-- TODO: 30 秒 Demo 动图或截图位,待作者补 -->

---

## 快速开始

```bash
# 1. clone
git clone https://github.com/Hugin-Z/tender-writer-v2.git
cd tender-writer-v2

# 2. 装依赖(Windows 双击即可)
install.bat

# 3. 打开 VSCode + Claude Code,告诉它:
#    "请读 SKILL.md,开始处理 projects/demo_cadre_training 的标书编制"
```

示范项目位于 [projects/demo_cadre_training/](projects/demo_cadre_training/),Clone 下来即可跑通端到端。

---

## 核心能力

- **五阶段工作流**:招标文件解析 → 评分矩阵 → 提纲 → 分章节撰写 → 合规终审,每阶段可 review
- **评分矩阵追踪**:10 列 CSV 把每一分拆到应答章节,杜绝漏答
- **项目类型识别**:工程 / 平台 / 研究 / 规划 / 其他 5 类自动选 outline 模板
- **docx 渲染质量**:统一中文宋体、黑色标题、图占位区块、字号相对规则、空格自动清理
- **B 模式材料组装**:从 assets 库按 asset_type / 公司 id 查找真实材料(CuratedLocalAssetsProvider),合并到 assembled.docx;无命中时产占位 + `.pending_marker`,V45 合并器列入 `pending_manual_work.md`
- **C 模式非交互填充**:一键跑完所有 C 模式 Part,变量缺失时 filled.docx 写入"【待填:字段描述】"显式占位
- **跨章节一致性检查**:团队成本 vs 预算、承诺时间 vs 工期等自相矛盾类错误自动捕获
- **Claude Code 深度协作契约**:CLAUDE.md 定义 6 条硬红线,AI 行为可预期

---

## v2 相比 v1

v2 基于 v1.1 经过两轮迭代沉淀十项改进,核心变化:AI 输出规则常驻化(`references/ai_output_rules.md` R1-R10)、docx 渲染质量总攻、非交互化、项目类型识别。详见 [docs/v2_design_notes.md](docs/v2_design_notes.md) 和 [docs/changelog.md](docs/changelog.md)。

---

## 与 AI 工具的兼容性

- **Claude Code(推荐)**:项目级协作深度最优,读取 `SKILL.md` + `CLAUDE.md` 走完整五阶段;进阶用户建议读 [CLAUDE.md](CLAUDE.md) 了解工具链协作契约
- **Cline / Cursor / 通义灵码 / 等其他 AI IDE 插件**:能读 `SKILL.md` 即可工作,部分硬红线靠 `references/ai_output_rules.md` 兜底
- **纯对话 AI(ChatGPT / DeepSeek Web 等)**:把 SKILL.md 和当前阶段文件发给 AI,按阶段手工推进

---

## 典型应用场景

- 政府采购公开招标 / 竞争性磋商 / 竞争性谈判 技术标(25-500 万元规模)
- 事业单位 / 国有企业公开采购 技术响应文件
- 外部专业咨询 / 培训服务 / 工程咨询 等服务类项目投标

---

## 深度文档

| 文档 | 面向 |
|---|---|
| [SKILL.md](SKILL.md) | 五阶段工作流细节,AI 入口,必读 |
| [CLAUDE.md](CLAUDE.md) | Claude Code 协作契约,6 条硬红线 |
| [docs/v2_design_notes.md](docs/v2_design_notes.md) | 设计决策记录 |
| [docs/v2_roadmap.md](docs/v2_roadmap.md) | 未来路线图 |
| [docs/changelog.md](docs/changelog.md) | 版本变更日志 |
| [docs/FAQ.md](docs/FAQ.md) | 常见问题 |

---

## 许可证

[MIT](LICENSE) © 2026 Hugin-Z · 问题反馈:提 Issue
