# tender-writer V3 规划

本文档是 V3 开发期的路线图 + 进度看板。每完成一项,回来更新该项状态(待开始 → 进行中 → 已完成)。本文档自身在 V3 启动元提交里建立,V3 任何代码改动都不应早于本文档的 commit。

## V3 定位

v2 是"工具链可用,B 模式占位实现"的版本。V3 的核心命题:让 v2 的所有口径诚实,补齐 B 模式真实材料组装能力,把测试覆盖率从 1 提到 ≥10,确认所有"未来工作"标注的 TODO 兑现。

V3 不是新功能版本,是完成度版本。

## 与 v2.0.x 的关系

v2.0.0 / v2.0.1 已封板,v2.0.x 不再打补丁。所有 v2.0.x 期间登记但未做的内容(docs/v2_roadmap.md 候选 1/2/3 + 已知噪音警告)迁入本文档,作为 V3 任务项。docs/v2_roadmap.md 收尾,只保留指向本文档的指针。

## 任务清单(按优先级)

### V3-1 · B 模式 CuratedLocalAssetsProvider 真实实现

**状态**:待开始

**优先级**:🔴 必做(否则 B 模式名不副实)

**现状**:scripts/assets_provider.py 当前只有 PlaceholderAssetsProvider,所有 lookup 返回占位 AssetRef,resolve 产出占位 docx。scripts/b_mode_fill.py 三种 source_type(inline_template / asset_lookup / self_drafted)全部产出占位段落。assets_provider.py 注释里登记 CuratedLocalAssetsProvider 和 MCPExternalAssetsProvider 为未来工作,V3 兑现前者。

**做什么**:

- 新增 CuratedLocalAssetsProvider 类,实现 lookup 和 resolve
- 扫 assets/<bidding_entity>/_curated/<asset_type>/ 按命名约定查找真实材料文件
- 命名约定:<asset_type>_<标识>_<年份>.docx(如 资质证明_ISO9001_2025.docx)
- lookup 多命中时停下让用户选(对齐 CLAUDE.md 红线 6 模式)
- resolve 真实从 docx 提取段落、保留格式,不再用占位文字
- 处理 PDF asset(预转 docx 或用 pdf2docx)
- 在 manifest.yaml 增加 lookup_priority / year_filter 字段
- b_mode_fill.py 的三个 handle* 函数:有真实 asset 时去掉占位文字

**完成判定**:

- demo 重跑后,part_04 / part_08 的 assembled.docx 不再含"[此处插入 X 材料]"占位段落
- 多命中场景能交互停下让用户选
- 单元测试覆盖 lookup 边界(0 命中 / 1 命中 / 多命中 / 年份过滤)

**预估**:6-10 小时

**依赖**:V3-2(需要测试基础设施先就位)

### V3-2 · 测试覆盖从 1 → ≥10

**状态**:待开始

**优先级**:🔴 必做

**现状**:scripts/tests/test_budget_parsing.py 是仓库唯一测试,覆盖 1 个边界 case。9901 行代码无测试是 V3 进入生产前的硬阻塞。

**做什么**:

- test_parse_tender.py:5-10 个不同结构的招标文件 fixture,断言 extracted 字段
- test_compliance_check.py:fixture docx 测漏答 / 弱覆盖 / 字体安全
- test_check_cross_consistency.py:测 D+N 节点抽取、团队人数过滤、金额一致性
- test_v45_merge.py:测 build_merge_order 在不同 part 配置下的输出
- test_generate_outline.py:测 5 类 project_type 各跑一遍模板
- test_export_deliverables.py:测 build_deliverable_mapping 动态生成

**完成判定**:

- tests/ 下 ≥6 个新测试文件 + budget_parsing 共 ≥7 个,test case 总数 ≥10
- ./run_script.bat tests/run_all.py(新增)能一键跑全部
- 每个核心脚本(parse_tender / compliance_check / check_cross_consistency / v45_merge / generate_outline / export_deliverables)至少有一个 happy path 测试

**预估**:8-12 小时(主要时间在准备 fixture)

**依赖**:无(V3 第一项做)

### V3-3 · timing hook 精确耗时埋点

**状态**:待开始

**优先级**:🟡 高

**现状**:docs/v2_roadmap.md 候选 3 已登记。当前"X 分钟"是墙钟估算,误差 ±30 分钟。

**做什么**:

- 新增 scripts/_timing_hook.py 上下文管理器
- 各阶段脚本主入口包一层 with stage_timer("parse_tender"):
- 累积写到 output/_timing.json
- 新增 scripts/timing_report.py 生成 markdown 报表

**完成判定**:demo 重跑后 output/_timing.json 包含每阶段耗时,误差 < 1 秒

**预估**:3-4 小时

### V3-4 · 正文级缝合句检测

**状态**:待开始

**优先级**:🟡 高

**现状**:docs/v2_roadmap.md 候选 1。scripts/check_chapter.py L132-139 留有 TODO 注释。

**做什么**:

- 新增 check_content_keyword_stitching(text, matrix_rows) ≈40 行
- 滑窗算法:30 字窗口内出现 ≥4 个评分项关键词 → 缝合句嫌疑
- 标记到 chapter_check_report.md

**完成判定**:用一段已知缝合句的文本(类似 "审核质量控制措施风险管理制度工作程序标准方法")测,被正确标记

**预估**:2-3 小时

### V3-5 · compliance_check --section-only 开关

**状态**:待开始

**优先级**:🟡 顺手做

**现状**:docs/v2_roadmap.md 已知噪音警告第 1 条。对 tender_response.docx 跑会假阳性报封面/目录缺失。

**做什么**:

- 加 --section-only 开关
- 文件名含 tender_response 时自动启用 section_only,跳过封面/目录检查
- 文件名含 final_response 时全项检查

**完成判定**:demo 重跑 compliance_check projects/demo_cadre_training/output/tender_response.docx,不再报"missing 封面 keywords"

**预估**:1 小时

### V3-6 · 扫描版 PDF 自动 OCR

**状态**:待开始

**优先级**:🟢 中(FAQ Q4 已兜底)

**现状**:parse_tender.py::read_pdf 直接调 pdfplumber.extract_text(),扫描版 PDF 输出空文本,不报错也不提示。

**做什么**:

- read_pdf 检测:text 长度 / 页数 < 阈值(50 字/页)→ 判定扫描版
- 自动调用 ocrmypdf -l chi_sim input.pdf temp_ocr.pdf
- 失败时退到当前 FAQ Q4 文档化的手动流程,清晰报错
- requirements.txt 加 ocrmypdf 注释(不强加依赖,标注"扫描版 PDF 才需要")

**完成判定**:用一份扫描版 PDF fixture 跑 parse_tender,自动 OCR 后产出非空 raw_text

**预估**:3-4 小时(含 tesseract 中文包安装文档)

### V3-7 · Word 直切集成 c_mode_run 自动分流

**状态**:待开始

**优先级**:🟢 中

**现状**:scripts/c_mode_docx_passthrough.py 存在但 c_mode_run 没集成。

**做什么**:c_mode_run.py --all 内部判断 source 类型,docx 走 passthrough,不走 jinja。

**完成判定**:demo 跑 c_mode_run --all,日志区分"模板填充"和"docx 直切"两种路径

**预估**:1-2 小时

### V3-8 · docx 字体安全深度检查

**状态**:待开始

**优先级**:🟢 中

**现状**:v2 补丁 2 修过 WPS 字体 fallback(MS 明朝 / Courier 缺失),但 compliance_check::check_font_safety 只扫段落 run.font 字段,不查 docx 内嵌的 fontTable.xml。

**做什么**:解压 docx zip → 解析 word/fontTable.xml → 列出所有声明字体 → 对照白名单(宋体/黑体/仿宋/Times New Roman/Arial)

**完成判定**:用一份故意嵌入 MS 明朝字体的 fixture docx 测,被正确标记

**预估**:2-3 小时

### V3-9 · check_cross_consistency 扩充检查项

**状态**:待开始

**优先级**:🟢 低

**现状**:当前只有 3 项检查(D+N 节点 / 团队成本 / 金额数量级)。README 写"等自相矛盾类错误自动捕获"暗示有更多。

**做什么**:

- 项 4:同字段在不同章节的措辞一致性(如项目名、采购方名)
- 项 5:人名/职称在简历章节和组织架构图之间的一致性
- 项 6:引用编号正确性(章节交叉引用)

**完成判定**:每项有单元测试 + demo 重跑通过

**预估**:4-6 小时

### V3-10 · README + SKILL 阶段口径统一

**状态**:待开始

**优先级**:🟢 低(累积要做)

**现状**:docs/DESIGN.md 已经改成"主干 5 + 并列(4-B/4-C/6)",但 README L31 / L49 / L67 + SKILL.md description 字段 / L44 标题 还是单口径"五阶段"。

**做什么**:

- README 三处 + SKILL.md description 字段 + SKILL.md L44 标题改为"五阶段主干 + 并列阶段(4-B/4-C/6)"
- SKILL.md description 字段顺手砍 40+ 关键词堆砌的一半,让触发精度提高(参见 V3-12)

**完成判定**:全仓 grep "五阶段" 命中均与"主干 + 并列"语义匹配

**预估**:1 小时

### V3-11 · B 模式 README + SKILL 口径诚实化(V3-1 配套)

**状态**:待开始

**优先级**:🔴 必做

**现状**:README 核心能力第 5 条"非交互批量化:一键跑完所有 C/B 模式 Part,占位红字标记'待填'"措辞像 B 模式产出真实内容、只是未填字段标红。实际 v2 的 B 模式整段是占位。

**做什么**:

- 与 V3-1 同步落地。V3-1 完成后,README 改成"B 模式真实材料组装"
- 措辞从"非交互批量化"改为更精确的"B 模式材料组装:从 assets 库按 asset_type 命名约定查找真实材料,合并到 assembled.docx;无命中时产占位 + .pending_marker"

**完成判定**:与 V3-1 一致

**预估**:1 小时

**依赖**:V3-1

### V3-12 · SKILL.md description 字段精简

**状态**:待开始

**优先级**:🟢 低

**现状**:SKILL.md description 字段堆 40+ 触发关键词,可能导致 Claude Code 过触发(无关问题也被拉进来)。

**做什么**:

- 把"或提到 X / Y / Z 等关键词时触发"那段砍一半,只留核心 10 个最强相关词
- 在 V3 里观察实际触发体验,后续可继续微调

**完成判定**:V3 开发期间用真实场景测,无关问题不再触发本 skill

**预估**:1 小时

**依赖**:V3-10 顺带做更省事

## 不做项(显式记录)

- MCPExternalAssetsProvider:assets_provider.py 注释登记的另一个未来工作。需要外部材料库 + MCP 协议对接,V3 不做,留 V4
- changelog 补 v2.0.1 条目:用户确认不做(自用项目,git log 够)
- GitHub About 字段改口径:用户确认不做
- README Python badge 3.11→3.10:实际 3.11+ 也能跑,标 3.11 不是错

## 开发节奏

- 一次只做一个 V3-N 项,不并行
- 每完成一项,在本文档把状态从"进行中"改为"已完成",commit message 用 feat(v3-N) / test(v3-N) / fix(v3-N) / refactor(v3-N) / docs(v3-N) 格式
- 本地 commit 累积,中间不 push 远程
- 全部 12 项完成 + 自检全过后,一次 push + 打 v3.0.0 tag,届时 README / SKILL / changelog 一并对外更新
- V3 不打中间小版本(v3.0.0-rc1 / v3.0.0-rc2 之类),封板就 v3.0.0

### 审核节奏(分级审核协议)

V3 期间审核位审核频率按 commit 风险分级,不是每个 commit 都贴审:

- **低风险 commit**(自检通过即继续,不贴审)
  - 纯 fixture 数据文件添加(anchor 文件本身、变形 fixture 数据)
  - v3_planning.md 状态字段改动(待开始 → 进行中 / 进行中 → 已完成)
  - .gitkeep / 空目录骨架
  - 顶层 fixtures README.md 套用既定模板

- **中风险 commit**(必须贴审)
  - test_*.py 代码本身
  - 变形 fixture 生成器脚本(_generators/mutate_*.py)
  - tests/run_all.py 和 tests/README.md
  - fixture 目录级 README(anchor 来源声明、用途声明)

- **高风险 commit**(必须贴审,审核位严审)
  - 任何动到非测试文件的 commit(scripts/ 下源码、CLAUDE.md / README.md / SKILL.md)
  - V3-N 范围外的"顺手修"
  - v3_planning.md 内容字段改动(不止状态字段)
  - 新增 V3-N 项 / 拆分 V3-N 项

子单元批审协议:

- 每完成 V3-N 内的一个子单元(比如 "fixture 准备 + 对应 test 文件" = 一组 2-3 个 commit),把这一组的所有 git diff + commit message 一次性贴审
- 审核位审完反馈一次,不通过则定位到具体 commit revert
- 子单元划分由用户(规划位)和 Claude Code 协商确定,通常以"一个 test_*.py + 它的 fixture"为一个子单元

V3-N 启动和收尾的强制审核点:

- V3-N 启动:状态改"进行中"的 commit + V3-N 第一个子单元一起首次贴审,确保方向对
- V3-N 收尾:状态改"已完成"的 commit **必须**贴审通过后才执行,不允许 Claude Code 自行标"已完成"

## 推荐开发顺序

按依赖关系和成本递减:

1. V3-2 测试基础设施(无依赖,V3-1 的依赖项,先做)
2. V3-1 B 模式真实实现(依赖 V3-2)
3. V3-11 B 模式口径诚实化(配套 V3-1,做完 V3-1 立即做)
4. V3-5 compliance_check 分流(1 小时小活,顺手做)
5. V3-7 Word 直切集成(1-2 小时小活)
6. V3-3 timing hook(为后续优化提供量化基础)
7. V3-4 正文级缝合句检测
8. V3-8 docx 字体深度检查
9. V3-6 扫描版 PDF 自动 OCR
10. V3-9 check_cross_consistency 扩充
11. V3-10 README + SKILL 阶段口径统一
12. V3-12 SKILL.md description 精简

V3-10 和 V3-12 放最后,因为它们涉及 README/SKILL 文案,V3 全部功能完成后一次性对外发布更整洁。

## 与 v2.0.x 的边界

- v2.0.0 是首发,v2.0.1 是文档+小 bug 补丁,两者都不再变更
- V3 在 main 上线性推进(单人项目,不开分支)
- 每个 V3-N commit 独立可 revert,如果某项有问题就单独 revert 该 commit,不动其他项
- 本地 main 在 V3 期间会和 origin/main 渐行渐远,这是预期。用户已确认依靠每版本本地备份,不在远程做 WIP 推送

## 文档更新约定

- 每次 V3-N commit 同时更新本文档对应项的状态字段(待开始 → 进行中 → 已完成)
- 如果开发中发现项的预估或做法需要调整,直接改本文档(不开新文档)
- 全部完成后,本文档保留作为 V3 历史档案,V4 再新建 v4_planning.md
