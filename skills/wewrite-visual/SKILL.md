---
name: wewrite-visual
description: |
  WeWrite 视觉模块：为公众号文章生成封面和必要的内文配图，或只交付提示词。触发词：
  封面图、公众号配图、给文章配图、换封面。通用绘图和 logo 设计不触发。
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
---

# wewrite-visual — 封面与配图

## 定位与边界

- AI 成图是**虚构画面**，只承担阅读停顿、情绪烘托和视觉钩子，**不是事实证据**；文章的事实支撑来自 verified 信源。
- 画面里的数字、标签、文件样式一律视为"布景"：除 `short-exact` 中逐字来自文章的短文字外，不允许可读的具体数据，不伪造真实文件的红头、公章、签名，不出现真实品牌标识。
- 本模块只做 AI 生图路线；检索真实照片、确定性 HTML 渲染图表目前都不在范围内。

## 前置

用户指定文章时使用该文件；否则 `wewrite run show`，读取当前任务的 `artifacts.article`、
`artifacts.illustrated_article`、`artifacts.image_prompts`、`artifacts.images_manifest`、
`visual`、`flags` 和任务目录。已完成的文章也可以直接配图，不要恢复或新建写作任务。

有任务时运行 `wewrite run step visual in_progress`。用户直接给了任务外文章时独立执行，
不写任务状态；提示词和图片放进文章同目录的 `<文件名>-assets/`，带图副本写成
`<文件名>-illustrated.md`。

根据本轮原话确定模式并用 `wewrite run update` 记录：只要封面用 `cover`，封面和必要内文图
用 `full`，只要提示词用 `prompts`。不要沿用写作模式猜测用户想生图。`prompts` 或
`skip_image_gen=true` 时仍要完成提示词，但不调用付费图片服务。

## 工作流

### 1. 提取视觉简报

从终稿提取：3-5 个具体实体、一句话核心主张、读者第一眼主题与第二眼洞察、主情绪、
可被画面引用的真实数据清单。账号调性以 style.yaml 为准。

### 2. 建立生成前契约（硬闸门）

在任务目录写 `visual-contract.yaml`，锁定模式、每项资产的比例/风格/结构/文字策略、
色板策略和预算。字段与阻断规则见：

```text
读取: {skill_dir}/references/requirements-contract.md
```

契约与文章、用户硬约束冲突时状态只能是"契约失败"，禁止进入下一步，禁止用"模型容易错字
""统一风格"等理由静默改变比例、文字或风格。

### 3. 选型

- 从风格库选 **1 种主风格**（封面），正文配图用同一风格的简化表达：
  `{skill_dir}/references/style-library.md`
- 封面选 **1 种结构**，正文配图按信息功能选类型与密度：
  `{skill_dir}/references/archetypes.md`
- 系列一致性（默认 70% 稳定、30% 变化，slate-amber 为默认色板）：
  `{skill_dir}/references/visual-dna.md`

### 4. 编译提示词

任何生图调用前，按 8 段式编译器为每项资产写完整提示词，保存到
`artifacts.image_prompts`；禁止把临时行内提示词直接交给生图工具，禁止未解析占位符。

```text
读取: {skill_dir}/references/prompt-compiler.md
```

提示词正文用英文撰写；需要画面出现中文时，只允许 `short-exact`（≤8 个汉字、逐字来自
文章或用户指定），并在英文提示词中逐字引用。批量清单写到 `artifacts.images_manifest`。

文件命名沿用：封面 `cover.jpg`，内文图 `figure-N-{slug}.jpg`。

### 5. 生成

数量必须不超过任务的 `visual.max_images`。调用时同时传入数量和费用上限：

```bash
wewrite image-gen --manifest {run_dir}/images.json --max-images {max_images} --max-cost {max_cost}
```

`max_cost` 为空时省略该参数。预算预检不通过就减少内文图，不能绕过上限。多张优先批量
并发，每批最多四张。图片服务失败时保留完整提示词并继续流程。

### 6. 质检（不检查实际图片，不许声称通过）

按质量门槛逐张检查：以正常尺寸和约 25% 缩略图尺寸各查一次，12 项 rubric 打分，硬失败
项命中即判失败。

```text
读取: {skill_dir}/references/quality-gates.md
```

文字缺失/错误、裁切错误或构图失败：新建提示词版本和新文件名，只重试失败项一次；禁止
用程序化涂抹修补生成图。已通过的资产不重复生成。

### 7. 组装带图副本

`full` 模式先复制原始正文到 `artifacts.illustrated_article`，再把采用的内文图插到副本
相应段落；封面不插入正文。任何模式都不得覆盖原始正文。

### 8. 封存

更新 `images.cover`、`images.figures`，再执行：

```bash
wewrite run step visual completed
```

只有提示词时同样标 completed，并明确说明未产生费用、没有实际图片。

## 快速速查

```text
读取: {skill_dir}/references/visual-guide.md
```
