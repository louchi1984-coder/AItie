# 跨平台使用与工具适配

## 加载技能

支持文件夹式 Skill 的工具：按该工具的安装方式加载整个 `aitie` 目录，入口为 `SKILL.md`，同时保留 references、assets、scripts 和 requirements.txt。`agents/openai.yaml` 是 Codex 的界面元数据，其他工具可以忽略。不同工具的发现路径和安装规则以其文档为准，不承诺自动加载。

不支持 Skill 的工具：把 `SKILL.md` 作为任务说明，并按其中的链接提供相关参考文件。需要图片样例时提供实际图片；只上传 Markdown 不会自动提供整个目录。无法访问文件或看图时明确说明，不能猜照片内容。

## 图片生成

优先使用当前平台的原生生图工具，确认它能接收参考照片。工具名称和参数按当前平台文档填写，不照抄 Codex 的调用名。每种独立画风分别生成，保存实际提示词、生成结果和使用的工具名称。

画风通道按当前 agent 平台区分：预设画风在 Codex 使用简短名称；非 Codex（或环境不明）读取 [具体画风要求](non-codex-styles.md)，将所选名称转成可观察的造型、线条、色彩和构图要求。不支持生图时也将该具体要求填入完整 prompt，直接交付。用户自写描述和参考图提取结果在所有平台保留具体要求，见 [风格提取](style-extraction.md)。组图按 [系列流程](series.md) 共用风格并逐枚交付。

- 支持参考图和透明背景：传入原照片，要求完整单枚图案、外围透明，并检查输出是否真实带有透明通道。
- 支持参考图但不支持透明背景：告知限制，先交付实际背景的预览；若用户需要透明打印图，再使用当前可用的抠图工具并检查边缘，不把白底图片标成透明 PNG。
- 只有文字生图、不支持参考图：说明不能直接依据照片保留人物特征，待用户接受这一限制或选择支持参考图的工具后生成。
- 没有生图工具：直接交付可复制的完整生图 prompt，注明原照片须作为参考图上传。按已选元素方案和画风填入公共框架；用户尚未选择元素安排时，遵循主流程先完成方案选择。多画风请求每种分别给一份完整 prompt，不只给变量或画风名称。不再询问是否切换工具，不自动调用外部服务或要求配置密钥；明确尚未生成图案，不用程序绘制占位图代替。

用户指定外部服务时遵守当前平台的授权规则；缺少能力不等于授权切换到付费 API、上传私人照片到新服务或安装工具。需要密钥时让用户在本地配置，不要求把密钥贴进对话。

## 查看画风样例

图鉴为 `assets/style-selector/index.html`，图片保持相对路径。可用当前平台的文件预览或允许的浏览器打开；也可让用户双击 HTML，或在对话中展示样例图片。网页安全策略阻止访问时提供文件或图片，不绕过限制。只有确认实际显示成功才说已打开。

## 保存与打印

保存到用户指定位置或当前工作区，链接使用当前平台支持的格式，不硬编码 Codex 的目录。打印脚本只需要已选图片和排版清单，不调用生图服务。

在终端进入 `aitie` 目录后运行以下命令；Windows 可将 `python3` 换为可用的 `python` 或 `py -3`。安装依赖前遵循当前环境授权规则，优先使用已有依赖：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/layout_stickers.py /path/to/sheet.json --output /path/to/stickers.pdf
```

Windows 虚拟环境对应命令为：

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe scripts/layout_stickers.py C:\path\sheet.json --output C:\path\stickers.pdf
```

清单字段和尺寸规则见 [打印与制作](production.md)。相对图片路径以清单所在目录为基准。没有 Python 执行能力时提供已填好的清单和命令，说明 PDF 尚未生成。

用当前平台可用的 PDF 渲染器或阅读器检查每页；有 Poppler 时可运行 `pdftoppm -png stickers.pdf preview`。如果只能检查结构、不能查看渲染结果，明确排版视觉检查尚未完成。真实打印仍需选择 100%／实际大小。

## 验证边界

跨平台说明不是兼容认证。报告当前环境实际完成的生图、文件保存、脚本执行和渲染检查；未经测试的平台只标为使用指引，不宣称已兼容。
