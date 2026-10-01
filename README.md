# AItie

将旅行照片重组为纪念贴纸，支持画风探索和选定图案的实际尺寸 PDF 排版。

组图默认制作统一画风的一套系列。画风可以选预设、自行描述或从上传的参考图提取；不支持生图的 agent 直接按枚提供完整 prompt。也支持独立提取参考图风格。

- 组图流程：`references/series.md`
- 风格提取：`references/style-extraction.md`
- 技能入口：`SKILL.md`
- 跨平台使用：`references/platforms.md`
- 非 Codex 画风要求：`references/non-codex-styles.md`（22 种名称转为具体视觉要求）
- 画风图鉴：`assets/style-selector/index.html`（在浏览器打开，保留整个 assets 目录）
- 打印说明：`references/production.md`
- 打印脚本：`scripts/layout_stickers.py`
- Python 依赖：`requirements.txt`

生成图片需要支持参考照片的生图工具。打印需要 Python 3、Pillow 和 reportlab。没有相应能力时可按跨平台说明获取提示词或排版清单，再在有能力的环境完成。

`agents/openai.yaml` 为 Codex 元数据；核心制作流程和脚本可单独使用。其他平台尚未完成实际兼容测试。
