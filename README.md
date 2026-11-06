# 阅读（Legado）书源索引

> 个人整理，只做链接汇总。`sources/` 下有两份筛过的小说书源，字段照抄上游，只删不改。

**最后核验 2026-11-05** ｜ 4 组来源，主入口 22 条 / 163 KB ｜ 小说书源 267 + 714 条

**目录**：[关于阅读（Legado）App 本身](#关于阅读legadoapp-本身) · [第三方版本](#第三方版本) · [怎么导入](#怎么导入) · [小说书源](#小说书源) · [书源来源](#书源来源) · [大灰狼](#大灰狼原仓库已失效自担风险) · [TTS 语音](#tts-语音) · [安全提示](#安全提示) · [常见问题](#常见问题) · [免责声明与许可](#免责声明与许可)

## 关于阅读（Legado）App 本身

原仓库 `gedoor/legado` 已在 2026 年清空：代码、发行版、标签全删，只留一份公告。作者称项目涉及侵权、已承担相应法律责任，并劝停止传播。

本页不提供安装包，下面只列各分支自己的发布页。这些包都是重新签名的，装之前先看「装之前要知道的三件事」。

## 第三方版本

官方停了之后，这些分支还在更新。按自己的情况挑一个就行，不用全看。

**这些包由各自作者负责**，本页只列地址，不为安全性、可用性背书。

<details>
<summary>展开：7 个版本对照表、装之前要知道的三件事</summary>

| 版本 | 平台 | 最近更新 | 适合谁 |
|---|---|---|---|
| [legado-with-MD3](https://github.com/HapeLee/legado-with-MD3/releases) | Android | 3.26.23 / 2026-11-04 | 想试新界面，又不想动原版数据的人 |
| [LegadoTeam](https://github.com/LegadoTeam/legado/releases) | Android | 2026-11-02 | 只想继续用原来那个样子 |
| [legado-Harmony](https://github.com/mgz0227/legado-Harmony) | 鸿蒙 | V1.0.6.218 / 2026-10-26 | 鸿蒙设备，没有第二个选择 |
| [Legado-Tauri](https://github.com/LegadoTeam/Legado-Tauri-Release) | Win / macOS / Linux | 持续 | 想在电脑上看 |
| [legado-E（Sigma）](https://github.com/Luoyacheng/legado-E/releases) | Android | 停在 2026-08-01 | 想试另一条路线，能接受三个月没更新 |
| [legadoT](https://github.com/skybbk1001/legadoT/releases) | Android | 2026-10-28 | 需要书架定时自动更新 |
| [huajideshutiao](https://github.com/huajideshutiao/legado/releases) | Android / 多平台开发中 | 2026-11-02 | 关注跨平台进展，不当主力用 |

**MD3 那个怎么选包**：`core` 是基础包，云端 OCR 能用；`comic` 内置本地 OCR 和擦字，体积大不少。手机基本都拿 `arm64-v8a`，除非设备很老。

**装之前要知道的三件事**

1. **多数分支沿用 `io.legado.app` 这个包名**，签名不同，覆盖安装会失败，只能先卸载。书源、书架、阅读进度会一起没——换之前先在旧版里导出备份。
2. **MD3 是例外**，包名是 `io.legato.kazusa`，可以和原版并存。装上去用几天不合适就删，原版数据一点没动。想稳妥试，就走这条。
3. **没法验证包和源码是不是一回事**。这些仓库都开源，但你装的那个 APK 是不是它编出来的，除非自己编译，否则无从核对。所以只从上面这些仓库的 Releases 拿，别用来路不明的网盘包。

</details>

如果你已经在用某个版本，下面的书源照样能导，导入方式和数据格式都没变。

## 怎么导入

**网络导入（复制 + 粘贴）**：打开 App → 右下角 **我的** → **书源管理** → 右上角 **⋮** → **网络导入** → 把[小说书源](#小说书源)里的地址粘进输入框 → 确定。

**点链接直接导入是不支持的。** 阅读 App 本身认 `legado://import/...` 这类唤起链接，但 GitHub 会把 README 里 `legado://` 开头的链接整个剥掉，页面上只剩一段点不动的文字。所以本页给的全是 https 地址，得复制一次再粘进去。多两步，但不会失效。

复制方法：代码块右上角有个复制按钮，点一下整条地址就进剪贴板；手机上也可以长按选中复制。

**二维码导入**：同一位置选 **二维码导入**，扫描分享页上的码，省去在手机上输长地址。

- 可以反复导入，App 会自己合并去重，不会越导越多
- 默认设置够用。批量更新一半失败、或者搜索老弹验证，多半是某一个源的问题，禁掉那个就行
- 唯一值得调的是 `其他设置` 里的**预下载**（`1~5`）。更新和搜索线程数别压低，压低了搜索会慢到不可用

## 小说书源

上面几份书单都混着漫画、听书、影视、音乐。下面两份只留小说，并且做了一轮清洗，规则都在 `scripts/build_sources.py` 里：

1. **类型**：`bookSourceType` 必须是 `0`（文本）。1 听书、2 图片、3 文件、4 视频一律不要。
2. **分组**：`bookSourceGroup` 必须含「小说」。只看类型不够——YCK 那 459 条里有 50 条是文本类型的漫画站、影视站。
3. **地址规范化**：去掉 `bookSourceUrl` 尾部的作者标记，如 `##@遇知`、`#妍希`、`已整理`。
4. **剔除废条目**：地址不是网址（写成书名、表情符号的）、没有域名、搜索和发现规则都为空的，整条丢掉。
5. **去重**：按「地址 + 名字」，同一站点挂多个书源是常态，名字不同的都留着。
6. **校验**：生成的 JSON 再逐条检查一遍类型、分组、地址、重复情况，任何一条不合格就中止，不会写出半成品。

除地址尾部标记外，其余字段原样保留，`bookSourceComment` 里的作者说明也都在。

两份各自独立：想全要就导两次，只缺一类就只导对应那份。

### 一键导入页

仓库里的 `import/` 就是一键导入页，三份 HTML：

| 页面 | 内容 |
|---|---|
| `import/index.html` | 两份书源都列，按钮各管各的 |
| `import/yck-novel.html` | 只有 YCK 那一份 |
| `import/yiove-novel.html` | 只有 Yiove 那一份 |

页面上的按钮是 `legado://import/bookSource?src=...`，点了会直接唤起「阅读」并开始导入。三个页面互不共用，想单独分享其中一份就给对应的那个。

需要说明两点：微信、QQ 的内置浏览器会拦这种唤起链接，得点右上角「在浏览器打开」；页面必须能通过 http 打开，本地双击 `file://` 有时唤不起来，托管到任意静态空间都行。

### YCK 书单 1067（墨辰整理系列 7.1）· 267 条

复制这一条，粘到 App 的网络导入里：

```
https://raw.githubusercontent.com/liufuyou/read/main/sources/yck-novel.json
```

raw 直连打不开时换这个，内容一样：

```
https://cdn.jsdelivr.net/gh/liufuyou/read@main/sources/yck-novel.json
```

### Yiove 星辰整理书源合集 · 714 条

复制这一条，粘到 App 的网络导入里：

```
https://raw.githubusercontent.com/liufuyou/read/main/sources/yiove-novel.json
```

raw 直连打不开时换这个，内容一样：

```
https://cdn.jsdelivr.net/gh/liufuyou/read@main/sources/yiove-novel.json
```

两份合起来去重后 888 条，单份 3 MB 左右，导入要等十几秒，不是卡住了。

> 上游书单更新后，跑 `python scripts/build_sources.py`：重新抓取、清洗、校验，同时更新 `sources/manifest.json` 和三份导入页。
> 只想确认已提交的文件没坏，跑 `python scripts/build_sources.py --check`，不联网。

## 书源来源

| 来源 | 内容 | 规模 | 说明 |
|---|---|---|---|
| [XIU2/Yuedu](#xiu2-书源) | 书源 | 22 条 / 163 KB | 条数最少，导入最快 |
| [Yiove](#yiove-书源仓库) | 书源仓库 | 合集 970 条 | 站点形式，自己挑；也有现成合集 |
| [YckCeo](#yckceo源仓库) | 书源站 | 站方称 5000+ | 域名常换，另有一个发布页；书单 1067 有 459 条 |
| [大灰狼](#大灰狼原仓库已失效自担风险) | 书源 / 净化规则 | 规则 26 条；书源约 2,973 条 | 原仓库已被 GitHub 屏蔽，风险自担 |

### XIU2 书源

分享页（二维码、本地下载都在这）：<https://yuedu.xiu2.xyz>

网络导入地址，任选一个能打开的，内容完全一致：

```text
https://bitbucket.org/xiu2/yuedu/raw/master/shuyuan
https://jsd.onmicrosoft.cn/gh/XIU2/Yuedu/shuyuan
https://cdn.jsdmirror.com/gh/XIU2/Yuedu/shuyuan
https://ghfast.top/https://raw.githubusercontent.com/XIU2/Yuedu/master/shuyuan
https://gh.catmak.name/https://raw.githubusercontent.com/XIU2/Yuedu/master/shuyuan
https://cdn.gh-proxy.org/https://raw.githubusercontent.com/XIU2/Yuedu/master/shuyuan
```

作者 [XIU2/Yuedu](https://github.com/XIU2/Yuedu)（GPL-3.0）。2026-11-05 实测 6 个地址全通、大小一致。

- 后 3 条是第三方加速代理，代理方能看到你请求了什么.
- 22 条里有 3 条是 `http://`，Android 9 起会因明文流量限制失败
- 有几条作者自己标了「搜索暂不可用」「人机验证」，不是你网络的问题

### Yiove 书源仓库

<https://shuyuan.yiove.com/>

站里的[星辰整理书源合集](https://shuyuan.yiove.com/book-source-collection/f3f55c6e-723b-4055-b254-124c9d88c5cb)收得比较全，970 条，里面八成是小说。上面已经筛好一份。

### YckCeo「源仓库」

内容站：<https://www.yck2026.fun/>

书源、漫画源、TVbox 接口都在这，站方自己写的是 5000+ 书源。

发布页：<https://yckceo.vip/> —— 换域名时从这里找回入口。**收藏发布页，别收藏具体地址**，地址会变，发布页不会。

## 大灰狼（原仓库已失效，自担风险）

原仓库 `shidahuilang/shuyuan` 在 2026-03-10 被 GitHub 以违反服务条款为由屏蔽，原来两个 raw 链接现在都是 404。网上流传的旧地址别再用了。

作者另开了备份仓：<https://github.com/shidahuilang/shuyuan-bak>（GPL-3.0）。

**净化规则**（30 KB / 26 条，导入很快，建议先试这个）：

```text
https://raw.githubusercontent.com/shidahuilang/shuyuan-bak/main/jinghua.json
```

**说明文档**：

```text
https://github.com/shidahuilang/shuyuan-bak/blob/main/doc.md
```

**完整书源包**（16.1 MB / 约 2,973 条）：

<details>
<summary>展开看地址（导入要等几分钟，且成功率不高，先读下面的说明）</summary>

```text
https://raw.githubusercontent.com/shidahuilang/shuyuan-bak/main/good.json
```

这个包里有 10,301 处 `http://` 地址，Android 9 以上会直接失败；低端机上导入和搜索都会明显变慢。

原仓库是因 ToS 被屏蔽的。求稳就用 XIU2 那 22 条。

</details>

> 备份仓里还放了安装包之类的文件，本索引只用其中的书源和规则。安装包一律不要装——来源不明，也不需要。

## TTS 语音

<https://tts.228088.xyz>

第三方的微软「朗读」转发服务（基于 `yy4382/ms-ra-forwarder`），跟书源没关系，只是经常一起用。

## 安全提示

- 书源能调用 JS 和 Java，不是纯文本，只导信得过的
- 别在书源里填账号、支付、身份信息
- 优先用本页实测过的 HTTPS 地址，来路不明的短链和网盘包不要导

## 常见问题

**导入后搜不到书 / 一直弹人机验证？**
多半是那条源本身的问题：对方站点加了验证，或者上游还没跟上改版。换一条源，或者等上游更新。XIU2 那 22 条里作者自己就标了几条「搜索暂不可用」。

**网络导入失败？**
换上面另一个镜像地址；确认地址以 `https://` 开头；部分网络环境需要自备代理。二维码导入失败时，改用分享页下载文件再本地导入。

**导入很慢 / 卡住？**
大包（16 MB 那种）在手机上确实要等。XIU2 那份只有 163 KB，几乎瞬间完成。

**重复导入会不会越来越多？**
不会，App 会合并去重。

**地址会变吗？**
会。书源放在上游仓库，作者改了分支或换了域名，这里就得跟着改。所以请收藏本页，别收藏某个具体地址。

## 免责声明与许可

- 本仓库只整理公开链接。`sources/` 下两份是上游书单的子集，字段原样照抄，只做了筛选和去重。
- 书源的版权归各作者：XIU2/Yuedu（GPL-3.0）、shidahuilang/shuyuan-bak（GPL-3.0）；墨辰整理系列、星辰整理合集的版权归各自的整理者。
- 本仓库的文字内容按 CC BY-SA 4.0 发布，见 [LICENSE](LICENSE)。
- 请遵守所在地法律法规，仅供个人学习使用。

---

最后核验：2026-11-05。发现链接失效，欢迎开 Issue。

<a href="https://star-history.com/#liufuyou/read&Date"><img src="https://api.star-history.com/svg?repos=liufuyou/read&type=Date&legend=top-left" alt="star history" width="620"></a>
