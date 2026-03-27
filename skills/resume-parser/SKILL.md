---
name: resume-pdf-import
description: 当你需要把任意排版的简历 PDF 统一转换为本仓库的标准 DOCX 输出时使用。本技能会提取 PDF 中可选中文本 + 图片内文字（OCR）到 Markdown，再将 Markdown 映射到 template/data_template.json（参考 template/data_demo.json 的风格），规范化 template/data.json，最后运行 `openclaw resume parse` 渲染最终 DOCX。
---

# 简历 PDF 导入（Resume PDF Import）

## 概述

本技能用于把「格式松散/排版不固定」的简历 PDF 标准化为仓库内固定的 DOCX 模板。
适用于端到端转换：源 PDF 可能包含可选中文本、图片扫描文字，或混合排版（需要 OCR 才能把信息补全到结构化数据中）。

## 工作流

1. 在仓库根目录执行，确保下方模板路径与 CLI 路径按文档所写可直接解析。
2. 把 PDF 提取为 Markdown：包含原生 PDF 文本 + OCR 文本。
3. 根据 Markdown 填充 `template/data.json`，遵循 `template/data_template.json` 的字段结构，并参考 `template/data_demo.json` 的写作风格。
4. 规范化候选 JSON，确保数组、键名、以及 index 序号一致。
5. 运行 `openclaw resume parse` 渲染最终 DOCX。

## 第 1 步：提取 PDF 文本到 Markdown

如果依赖缺失，先安装提取所需依赖：

```bash
python3 -m pip install -r skills/resume-pdf-import/scripts/requirements.txt
```

运行提取器：

```bash
python3 skills/resume-pdf-import/scripts/extract_pdf_resume.py \
  input/resume.pdf \
  --output output/resume.md \
  --pages-dir output/resume-pages
```

备注：

- Markdown 会包含：逐页原生文本、逐页 OCR 文本、以及一个去重后的 `Combined Content` 汇总区。
- 推荐使用 `--pages-dir`：它会导出每页 PNG，方便你在 OCR 漏识别或版式特殊时做人工抽查。
- 如果 OCR 依赖不可用，提取器会退化为「仅原生 PDF 文本」。此时请安装依赖后重新运行，再开始填 `data.json`。

## 第 2 步：起草 `template/data.json`

请同时打开这些文件对照：

- `output/resume.md`
- `template/data_template.json`
- `template/data_demo.json`
- `skills/resume-pdf-import/references/data-mapping.md`

规则：

- JSON key 必须与 `template/data_template.json` **完全一致**。
- 只填写能从 Markdown 或导出的页面图片中**明确确认**的事实。
- 不确定或缺失的标量值用 `""`。
- 缺失的列表段落用 `[]`。
- 尽量保留原文表达，不要过度“润色改写”。

## 第 3 步：规范化候选 JSON

起草完成后执行：

```bash
python3 skills/resume-pdf-import/scripts/normalize_resume_data.py \
  template/data.json
```

该脚本会：

- 删除空的占位行
- 仅保留模板字段
- 将 bullet 风格数组的 `index` 字段重写为连续递增
- 保持原有条目顺序

如果输出仍不正确，修正候选 JSON 后再次运行规范化脚本。

## 第 4 步：渲染最终 DOCX

运行插件 CLI：

```bash
openclaw resume parse \
  --template template/template.docx \
  --data template/data.json \
  --output output/result.docx
```

完成后请返回输出路径，并明确指出哪些字段因为信息缺失只能留空。

## 失败处理

- 如果 PDF 图片占比高或 OCR 质量差，请先查看 `output/<name>-pages/page-*.png`，再填写 `data.json`。
- 如果因为分栏/表格导致 Markdown 顺序混乱，请先手工重建简历的逻辑顺序，再映射到 JSON。
- 如果源简历把“职责”和“成果”混在同一组 bullet 列表里，请按 `references/data-mapping.md` 的拆分建议处理；不要凭空编造量化结果。
