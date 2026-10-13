# 生成前契约

编译任何提示词之前，在任务目录写 `visual-contract.yaml`。它是本次配图的唯一事实源：
后续提示词元数据、批量清单都必须与它一致。

## 字段

```yaml
version: 1
mode: full            # cover | full | prompts
platform: wechat
brief:
  core_claim: ""      # 一句话核心主张，来自终稿
  reader: ""          # 目标读者
  first_sight: ""     # 第一眼应该读到的主题
  second_sight: ""    # 第二眼的冲突、洞察或隐喻
  entities: []        # 3-5 个具体实体
  emotion: ""         # 主情绪
  verified_data: []   # 允许被画面引用的真实数据（仅 short-exact 文字可用）
palette_policy: slate-amber   # 默认；用户另有指定从其指定
assets:
  - id: cover
    role: 封面
    aspect_ratio: "2.35:1"
    style: ""         # 风格库编号
    archetype: ""     # 封面结构编号
    text_policy: textless     # textless | short-exact
    exact_text: ""            # short-exact 时逐字填写，必须来自文章或用户
    output: cover.jpg
  - id: figure-1
    role: ""          # 这张图解决读者什么问题
    section: ""       # 插入的章节/位置
    aspect_ratio: "16:9"
    style: ""
    archetype: ""     # 正文配图类型
    text_policy: textless
    exact_text: ""
    output: figure-1-{slug}.jpg
budget:
  max_images: 4
  max_cost: null
```

## 阻断规则（命中即"契约失败"，不得生成）

1. **比例**：资产比例与平台基线（封面 2.35:1、内文 16:9）或用户明确指定值不一致；
   一个用户指定的比例被改成跨平台通用比例。
2. **文字**：用户要求可见文字，但资产写成 `textless`、保留干净标题区或任何无字降级；
   `exact_text` 没有逐字出现在文章或用户原话里；中文超过 8 个汉字。
3. **风格**：风格编号不在风格库中；同一篇出现两种互不相关的视觉语言（内文简化表达
   不算）。
4. **信息**：把文章没有的数字、标签、实体写进契约；要求画面复刻真实文件、公章、签名
   或真实品牌标识。
5. **预算**：资产数量超过 `max_images`；按 `estimated_cost_per_image` 估算的费用超过
   `max_cost`。

## 约束优先级

1. 用户本轮明确指定的比例、文字、风格、构图、禁止项
2. 用户提供的原始视觉提示词
3. 用户提供的参考图与文章
4. 本模块的默认规则（slate-amber、风格库等）
5. 助手对缺失信息的推断

下层只能补缺失信息，不能覆盖上层硬约束。用户给了完整提示词时，原文保存到
`source-prompt.md`，其中"必须出现/只能出现/不要出现"等表述一律按硬约束处理。

## 参考图处理

| 用途 | 提取内容 |
|---|---|
| direct | 主体身份、必须复现的构图 |
| style | 线条、材质、光线、空间规则 |
| palette | 颜色关系与占比 |

参考图只提供高层方向，禁止默认压缩成"一个物体 + 无字背景"，也不得据此覆盖文章内容
约束。引用路径只有在文件真实存在时才写入契约。
