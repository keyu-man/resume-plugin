# Data Mapping Rules

Use this reference when converting the extracted markdown into `template/data.json`.

## Source Files

- Schema shape: `../../template/data_template.json`
- Output style example: `../../template/data_demo.json`

## Rules

1. Use only facts supported by the extracted markdown or by direct visual inspection of exported page images.
2. Do not invent employers, schools, dates, titles, contact details, achievements, or skill bullets.
3. Keep missing scalar fields as `""`.
4. Keep missing list sections as `[]`.
5. Preserve the source language. If the PDF is Chinese, keep Chinese text in `description`, `company`, `project_name`, and similar fields.
6. `name_py` can be filled from an explicit English name in the PDF. If the source only contains a Chinese name, transliterating it to tone-free title-case pinyin is acceptable.
7. Do not derive time-sensitive fields unless the source states them directly. In particular, prefer leaving `age` and `work_year` blank instead of computing them from dates.
8. Keep experience entries in the same order they appear in the source unless the PDF is clearly split into chronological sections already ordered newest-first.
9. For `skills`, `content`, and `achievement`, keep each bullet as a separate item and let the normalizer rewrite `index` values sequentially.
10. When a bullet mixes duties and outcomes, prefer this split:
   - `content`: responsibilities, tasks, scope, process work
   - `achievement`: results, impact, metrics, awards, successful deliveries
11. If a section has only duty-style bullets and no clear outcomes, keep the bullets under `content` and leave `achievement` empty.
12. Normalize obvious OCR mistakes only when the intended text is clear from context.

## Suggested Working Order

1. Read the extracted markdown.
2. Open `../../template/data_template.json`.
3. Open `../../template/data_demo.json`.
4. Draft the candidate JSON.
5. Run `../scripts/normalize_resume_data.py` on the candidate file before rendering.
