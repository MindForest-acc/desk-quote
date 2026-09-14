# 案头 DeskQuote

一张常驻 macOS 桌面的宣纸卡片，随机显示《孙子兵法》《庄子》《墨子》《王阳明心学》《毛泽东选集》里的句子，每条都配原文出处与白话释义。

五本书各有自己的纸色、字体和闲章——不看书名也知道是谁在说话。

![预览](previews/sheet-note.png)

## 安装

```bash
./build.sh && open 案头.app
```

需要 macOS 14+ 与 Xcode 命令行工具。构建产物 1.7 MB，纯 Swift，无第三方依赖。

首次打开若被 Gatekeeper 拦（ad-hoc 签名），在「系统设置 → 隐私与安全性」里放行一次即可。

## 用法

卡片常驻桌面，菜单栏有一个 `❝` 图标。

| 操作 | 行为 |
|---|---|
| 单击卡片 | 换下一句 |
| 拖动卡片 | 移动位置（自动记忆） |
| ⌥ 单击 | 收起 / 展开释义 |
| ⌃⌥Space | 全局换一句（不需要辅助功能授权） |
| 点菜单栏图标 | 完整菜单 |

菜单里可调：**书目**（五本可任意组合）、**轮换间隔**（15 分钟 ~ 2 小时 / 不自动换，默认 45 分钟）、**排版**（自动 / 横排 / 竖排）、**外观**（跟随系统 / 浅色 / 深色）、**卡片宽度**、**窗口层级**（悬浮最上层 / 贴在桌面上）、收藏与只看收藏、开机自启。

**关于横排与竖排**：默认「自动」——短句走竖排（古籍本来的样子，断句处即分栏，因此竖排不带标点），长句走横排。这个变化是刻意的，它让卡片不容易退化成壁纸的一部分。想要统一版式，菜单 → 排版 → 横排 / 竖排。

## 语料

224 条，`Resources/corpus.json`。只收能定位到原书的句子。

语料由模型知识写出，再逐条与维基文库公有领域底本做去标点全文比对，篇目归属以底本为准。**178/224 条通过原文 + 篇目校验**；其余 46 条（44 条毛选 + 2 条王阳明《年谱》）没有可检索的公有领域底本，在 JSON 里 `verified` 为 `null`，文本与出处**未经原书核对**。

校验抓到的问题、裁决过程和见证本清单见 [docs/product-design-2026-09-14.md](docs/product-design-2026-09-14.md) 第七节。

重跑校验：

```bash
python3 -m venv venv && ./venv/bin/pip install zhconv
./venv/bin/python scripts/fetch_sources.py && ./venv/bin/python scripts/verify2.py Resources/corpus.json
```

## 开发

```bash
./scripts/preview.sh ./previews   # 离屏渲染各书各排版的卡片 PNG，不需要录屏授权
```

自测（语料完整性、竖排切分、抽样器均匀性与间隔上界）随 `scripts/SelfTest.swift` 编译运行。

## 结构

```
Sources/        Quote 语料模型与竖排切分 · Theme 五套纸墨 · Shuffler 无放回洗牌
                CardView 卡片 · CardWindow 无边框浮窗 · AppDelegate 菜单与快捷键
Resources/      corpus.json 语料 · AppIcon.icns
scripts/        preview.sh 离屏渲染 · SelfTest.swift 自测 · fetch_sources.py / verify2.py 校验管线
docs/           产品与设计说明
```
