#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable


def load_fitz():
  try:
    import fitz  # type: ignore
  except ImportError as exc:  # pragma: no cover - import guard
    raise SystemExit(
      "PyMuPDF is required. Install dependencies with "
      "`python3 -m pip install -r skills/resume-pdf-import/scripts/requirements.txt`."
    ) from exc
  return fitz


def load_ocr_engine(skip_ocr: bool):
  if skip_ocr:
    return None

  try:
    import numpy as np  # type: ignore
    from rapidocr_onnxruntime import RapidOCR  # type: ignore
  except ImportError:
    return None

  return {"numpy": np, "engine": RapidOCR()}


def clean_lines(lines: Iterable[str]) -> list[str]:
  cleaned: list[str] = []
  seen: set[str] = set()

  for raw_line in lines:
    line = " ".join(raw_line.replace("\u3000", " ").split())
    if is_noise_line(line):
      continue
    if line in seen:
      continue
    seen.add(line)
    cleaned.append(line)

  return cleaned


def is_noise_line(line: str) -> bool:
  if not line:
    return True

  if re.fullmatch(r"[\W_]+", line):
    return True

  if re.fullmatch(r"[A-Za-z0-9+/=_-]{15,}", line):
    return True

  if len(line) <= 2 and not re.search(r"[\u4e00-\u9fff0-9]", line):
    return True

  return False


def block_lines(page) -> list[str]:
  blocks = page.get_text("blocks", sort=True)
  lines: list[str] = []

  for block in blocks:
    text = block[4] if len(block) > 4 else ""
    lines.extend(text.splitlines())

  return clean_lines(lines)


def pixmap_to_ndarray(np_module, pix) -> "object":
  array = np_module.frombuffer(pix.samples, dtype=np_module.uint8)
  array = array.reshape((pix.height, pix.width, pix.n))

  if pix.alpha and pix.n == 4:
    return array[:, :, :3]

  return array


def ocr_lines(ocr_bundle, pix) -> list[str]:
  if ocr_bundle is None:
    return []

  image = pixmap_to_ndarray(ocr_bundle["numpy"], pix)
  result, _ = ocr_bundle["engine"](image)

  if not result:
    return []

  return clean_lines(item[1] for item in result if len(item) >= 2)


def render_markdown(
  pdf_path: Path,
  page_sections: list[dict[str, object]],
  combined_lines: list[str],
  ocr_enabled: bool,
) -> str:
  lines = [
    "# Resume PDF Extraction",
    "",
    f"- source_pdf: `{pdf_path}`",
    f"- page_count: {len(page_sections)}",
    f"- ocr_enabled: {'yes' if ocr_enabled else 'no'}",
    "",
    "## How To Use",
    "",
    "- Prefer the `Combined Content` section when filling `data.json`.",
    "- If any field looks missing or ambiguous, inspect the per-page sections.",
    "- If OCR is disabled or weak, review the exported page images manually.",
    "",
  ]

  for section in page_sections:
    page_number = section["page_number"]
    native_lines = section["native_lines"]
    ocr_lines_list = section["ocr_lines"]
    merged_lines = section["merged_lines"]
    image_path = section.get("image_path")

    lines.extend(
      [
        f"## Page {page_number}",
        "",
      ]
    )

    if image_path:
      lines.extend([f"- page_image: `{image_path}`", ""])

    lines.extend(["### Native PDF Text", ""])
    if native_lines:
      lines.extend(f"- {item}" for item in native_lines)
    else:
      lines.append("- (no native text extracted)")
    lines.append("")

    lines.extend(["### OCR Text", ""])
    if ocr_lines_list:
      lines.extend(f"- {item}" for item in ocr_lines_list)
    else:
      lines.append("- (no OCR text extracted)")
    lines.append("")

    lines.extend(["### Combined Page Content", ""])
    if merged_lines:
      lines.extend(f"- {item}" for item in merged_lines)
    else:
      lines.append("- (no page content extracted)")
    lines.append("")

  lines.extend(["## Combined Content", ""])
  if combined_lines:
    lines.extend(f"- {item}" for item in combined_lines)
  else:
    lines.append("- (no text extracted from the PDF)")
  lines.append("")

  return "\n".join(lines)


def main() -> int:
  parser = argparse.ArgumentParser(
    description="Extract native PDF text and OCR text into a markdown file.",
  )
  parser.add_argument("pdf_path", help="Path to the source PDF file")
  parser.add_argument(
    "-o",
    "--output",
    required=True,
    help="Path to the output markdown file",
  )
  parser.add_argument(
    "--pages-dir",
    help="Optional directory for rendered page PNG files",
  )
  parser.add_argument(
    "--dpi",
    type=int,
    default=216,
    help="Rasterization DPI used for OCR and page image export (default: 216)",
  )
  parser.add_argument(
    "--skip-ocr",
    action="store_true",
    help="Skip OCR and extract only native PDF text",
  )
  args = parser.parse_args()

  pdf_path = Path(args.pdf_path).expanduser().resolve()
  output_path = Path(args.output).expanduser().resolve()
  pages_dir = (
    Path(args.pages_dir).expanduser().resolve() if args.pages_dir else None
  )

  if not pdf_path.is_file():
    raise SystemExit(f"PDF not found: {pdf_path}")

  fitz = load_fitz()
  ocr_bundle = load_ocr_engine(args.skip_ocr)
  ocr_enabled = ocr_bundle is not None

  if not args.skip_ocr and not ocr_enabled:
    print(
      "OCR dependencies are unavailable, continuing with native PDF text only.",
      file=sys.stderr,
    )

  if pages_dir:
    pages_dir.mkdir(parents=True, exist_ok=True)
  output_path.parent.mkdir(parents=True, exist_ok=True)

  zoom = args.dpi / 72
  matrix = fitz.Matrix(zoom, zoom)
  page_sections: list[dict[str, object]] = []
  combined_lines: list[str] = []
  combined_seen: set[str] = set()

  with fitz.open(pdf_path) as document:
    for page_index, page in enumerate(document):
      page_number = page_index + 1
      native_lines = block_lines(page)
      pix = page.get_pixmap(matrix=matrix, alpha=False)
      image_path = None

      if pages_dir:
        image_path = pages_dir / f"page-{page_number}.png"
        pix.save(image_path)

      page_ocr_lines = ocr_lines(ocr_bundle, pix)
      merged_lines = clean_lines([*native_lines, *page_ocr_lines])

      for line in merged_lines:
        if line in combined_seen:
          continue
        combined_seen.add(line)
        combined_lines.append(line)

      page_sections.append(
        {
          "page_number": page_number,
          "native_lines": native_lines,
          "ocr_lines": page_ocr_lines,
          "merged_lines": merged_lines,
          "image_path": str(image_path) if image_path else None,
        }
      )

  markdown = render_markdown(pdf_path, page_sections, combined_lines, ocr_enabled)
  output_path.write_text(markdown, encoding="utf-8")
  print(output_path)
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
