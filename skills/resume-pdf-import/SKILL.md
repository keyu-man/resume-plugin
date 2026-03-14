---
name: resume-pdf-import
description: Use when converting resume PDFs with arbitrary layouts into this repo's standardized DOCX output. The skill extracts native PDF text plus OCR text into markdown, maps the markdown into template/data_template.json using template/data_demo.json as guidance, normalizes template/data.json, and runs `openclaw resume parse` to render the final DOCX.
---

# Resume PDF Import

## Overview

This skill standardizes a loose resume PDF into the repo's fixed DOCX template. It is for end-to-end conversion work where the source PDF may contain selectable text, scanned text inside images, or mixed layouts that need OCR before the structured data can be filled.

## Workflow

1. Work from the repository root so the template and CLI paths below resolve as written.
2. Extract the PDF into markdown with native PDF text plus OCR text.
3. Fill `template/data.json` from the markdown, following the schema in `template/data_template.json` and the style in `template/data_demo.json`.
4. Normalize the candidate JSON so arrays, keys, and indexes are consistent.
5. Run `openclaw resume parse` to render the final DOCX.

## Step 1: Extract PDF Text To Markdown

Install the extraction dependencies if they are missing:

```bash
python3 -m pip install -r skills/resume-pdf-import/scripts/requirements.txt
```

Run the extractor:

```bash
python3 skills/resume-pdf-import/scripts/extract_pdf_resume.py \
  input/resume.pdf \
  --output output/resume.md \
  --pages-dir output/resume-pages
```

Notes:

- The markdown includes per-page native text, per-page OCR text, and a deduplicated `Combined Content` section.
- `--pages-dir` is recommended. It gives you page PNGs for manual spot checks when OCR misses image text or the layout is unusual.
- If OCR dependencies are unavailable, the extractor falls back to native PDF text only. In that case, install the requirements and rerun before filling `data.json`.

## Step 2: Draft `template/data.json`

Load these files:

- `output/resume.md`
- `template/data_template.json`
- `template/data_demo.json`
- `skills/resume-pdf-import/references/data-mapping.md`

Rules:

- Keep the JSON keys exactly aligned with `template/data_template.json`.
- Fill only facts that are supported by the markdown or by direct inspection of exported page images.
- Leave uncertain or missing scalar values as `""`.
- Leave missing list sections as `[]`.
- Preserve the source wording where possible instead of rewriting aggressively.

## Step 3: Normalize The Candidate JSON

After drafting the JSON, run:

```bash
python3 skills/resume-pdf-import/scripts/normalize_resume_data.py \
  template/data.json
```

This script:

- removes empty placeholder rows
- keeps only the template keys
- rewrites `index` fields sequentially for bullet-style arrays
- preserves the original item order

If the output still looks wrong, fix the candidate JSON and run the normalizer again.

## Step 4: Render The Final DOCX

Run the plugin CLI:

```bash
openclaw resume parse \
  --template template/template.docx \
  --data template/data.json \
  --output output/result.docx
```

Return the output path and explicitly call out any fields you had to leave blank.

## Failure Handling

- If the PDF is image-heavy or OCR quality is poor, inspect `output/<name>-pages/page-*.png` before filling `data.json`.
- If the markdown order is noisy because of columns or tables, reconstruct the logical resume order manually before mapping into JSON.
- If the source mixes responsibilities and achievements in one bullet list, use the split guidance in `references/data-mapping.md`. Do not invent quantified outcomes.
