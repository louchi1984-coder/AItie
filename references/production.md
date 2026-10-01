# 自动定尺寸与打印排版

## 选定作品后执行

不要求用户填写宽高。skill 实际查看图案，以轮廓比例、文字和细节可读性确定内容密度（light/normal/detailed），必要时为此图设置最小长边 `min_long_edge_mm`。这属于代理的设计判断，不是用户必填项，也不能仅从像素推断文字可读性。

用户可指定纸张、数量或小/中/大偏好。未指定时使用 A4、10mm 页边距、5mm 间距；生成同款可行的小中大版本供选择。所有物理尺寸属于本次排版方案，可随用途调整。用户只要一种大小时不要自动额外输出三种。

## 脚本

依赖 Python 3、Pillow、reportlab，依赖清单在 `requirements.txt`。使用当前平台可执行的 Python；在 Codex 本地可用 load_workspace_dependencies 查 bundled Python。其他平台可用已有本地 Python 或代码执行环境，具体命令见 [跨平台使用](platforms.md)。缺少包时说明依赖，安装须遵循当前环境的授权规则。脚本不调用图片模型，不修图、不去光晕、不添加白边，不更改源文件。

`python scripts/layout_stickers.py sheet.json --output stickers.pdf`

清单示例（相对路径以清单目录为基准）：

```json
{
  "paper": "A4",
  "margin_mm": 10,
  "gap_mm": 5,
  "min_ppi": 300,
  "guides": false,
  "items": [
    {"id": "chosen-01", "path": "chosen.png", "density": "normal", "sizes": ["small", "medium", "large"], "copies": 1}
  ]
}
```

`copies` 是每个选中尺寸的份数。paper 支持 A4/A5/Letter。代理可设 `min_long_edge_mm` 或 `base_long_edge_mm` 覆盖自动估计，不向用户索要数字。脚本保留源画布比例，包括透明边距；定尺寸前检查边距是否合理，不能将大空白画布当作贴纸实体尺寸。记录的宽高为图像画布尺寸。

自动长边基准：light 65mm、normal 80mm、detailed 95mm；小中大系数 0.75/1/1.25。按最低可读长边、纸张可用范围和源像素对应 PPI 限制，不能满足时停止并说明。被限制成相同大小时合并尺寸标签和份数，记录原因，不伪装成不同尺寸。

输出 PDF 与同名 `.layout.json`，记录尺寸、份数、位置、PPI、合并提示。PDF 默认无辅助线，页脚标有 20mm 校准线与“Print at 100% / Actual size”。不要使用“适合页面”缩放。`guides: true` 只画图像矩形范围的浅灰虚线，方便手工分割，不是异形裁切路径。

## 检查与交付

重新渲染 PDF 并查看每页，确认完整、间距足够、文字可读；同时检查布局 JSON 的页界、数量与 PPI。家用可打印 PDF 不等于商用刀模生产包。示范用未清稿样图时明确说明，排版不能掩盖残留像素。

供应商制作另按其模板处理出血、安全区、颜色空间、白墨和真正闭合的异形矢量刀线；不硬编码某厂规格。材料选择按用途和供应商信息处理，透明 PNG 不等于透明膜材。未打样不宣称耐水耐磨或黏附效果。
