# nocodevit/skills

Skills for [Claude Code](https://claude.com/claude-code). Written and tested with Claude Code; other agents that read `SKILL.md` may work but are untested.

[中文说明](#中文说明)

## Skills

| Skill | What it makes |
|---|---|
| [`guide-video`](skills/guide-video/SKILL.md) | A step-by-step tutorial video (onboarding, API integration, setup walkthroughs) from a list of steps and real screenshots. Each step is a page; a cursor clicks through it with highlights, zooms, typed input and self-typing code with terminal output. Tapping the next step's number in the corner expands the next page out of the button. |
| [`product-film`](skills/product-film/SKILL.md) | A short beat-synced product film (launch video, feature promo): big-type title cards, cursor-driven UI demos redrawn from the product's design, a particle burst on the music's lift, and a sphere of dots that explodes and lands as the logo before the tagline. |

## Install

As individual skills:

```bash
npx skills add nocodevit/skills                  # all
npx skills add nocodevit/skills -s product-film  # one
```

Or as a Claude Code plugin (skills are then namespaced, e.g. `/nocodevit:product-film`):

```bash
claude plugin marketplace add nocodevit/skills
claude plugin install nocodevit@nocodevit
```

## Requirements

- Node.js 18+ (Playwright is installed per video project)
- FFmpeg
- Python 3 with NumPy (sound effects)

## How it works

A video is a single HTML file in which every frame is a pure function of time: `window.seek(t)` draws second `t` exactly, with no CSS transitions, timers or carried state. Playwright steps through time and screenshots each frame, FFmpeg encodes them (60 fps with motion blur from blended sub-frames), and a small NumPy synth adds clicks, typing and transition sounds at the exact frames they belong to.

For `guide-video` you describe the steps and Claude works from real screenshots; for `product-film` you pick the music and Claude cuts the film to its beat grid. Either way Claude writes the page, checks still frames and renders.

## License

MIT

---

## 中文说明

给 Claude Code 用的 skills,以 Claude Code 为准编写和测试;其他读取 `SKILL.md` 的工具也许能用,但未经测试。

### Skills

| Skill | 用途 |
|---|---|
| [`guide-video`](skills/guide-video/SKILL.md) | 分步教程视频(上手指南、API 接入、配置流程)。给出步骤和真实截图,每一步一页:光标点击、高亮框、局部放大、输入文字、代码自动敲出并在终端运行。点击右下角的下一步数字,新页面从按钮处圆形扩散展开。 |
| [`product-film`](skills/product-film/SKILL.md) | 卡点的产品宣传短片(发布视频、功能介绍):大字标题卡、按产品设计重绘的界面演示(光标操作)、音乐高潮处的粒子爆发,结尾粒子球炸开后聚成 logo,再出 tagline。 |

### 安装

```bash
npx skills add nocodevit/skills
```

或作为 Claude Code 插件安装(调用时带前缀,如 `/nocodevit:product-film`):

```bash
claude plugin marketplace add nocodevit/skills
claude plugin install nocodevit@nocodevit
```

### 依赖

Node.js 18+、FFmpeg、Python 3 + NumPy。

### 原理

整支视频是一个 HTML 文件,每一帧都是时间的纯函数:`window.seek(t)` 精确画出第 `t` 秒,不用 CSS 过渡、定时器或帧间状态。Playwright 逐帧截图,FFmpeg 编码(60fps,子帧混合出运动模糊),NumPy 合成的点击、打字、转场音效精确落在对应帧上。
