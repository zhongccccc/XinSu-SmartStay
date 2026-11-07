#!/bin/bash
echo "=== PDF 工具 ==="
for t in pdftoppm pdfimages mutool gs convert magick qpdf; do
  p=$(command -v "$t" 2>/dev/null)
  printf '  %-10s %s\n' "$t" "${p:--}"
done
echo
echo "=== python 库 ==="
python3 - <<'PY'
for m in ("fitz", "pypdf", "PyPDF2", "pdfminer", "PIL"):
    try:
        __import__(m)
        print("  有", m)
    except Exception:
        pass
PY
echo
echo "=== 能不能装 poppler ==="
apt-get --version >/dev/null 2>&1 && echo "  有 apt" || echo "  无 apt"
ping -c1 -W1 8.8.8.8 >/dev/null 2>&1 && echo "  外网可达" || echo "  外网不可达"
