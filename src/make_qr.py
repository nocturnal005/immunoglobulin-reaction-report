"""Generate the participant QR code for the online reaction report form.

Error correction level H (~30% of the code recoverable) so it still scans when
the printed form is creased, folded, or photocopied.

Run this before build_pdf.py -- the PDF embeds dist/qr-questionnaire.png.
If the form is ever rehosted (e.g. on a Royal Free domain), change FORM_URL
here, re-run this, then re-run build_pdf.py.
"""
from pathlib import Path

import segno

# The URL a patient reaches by scanning. Must be openable WITHOUT signing in --
# a scanned link cannot prompt for a login.
FORM_URL = "https://claude.ai/code/artifact/a4e2c535-41dc-4724-aeaa-5c377bccde39"

TEAL = "#0B6B70"
DIST = Path(__file__).resolve().parent.parent / "dist"


def main():
    DIST.mkdir(exist_ok=True)
    qr = segno.make(FORM_URL, error="h")

    # brand colour, for the form and screen use
    qr.save(DIST / "qr-questionnaire.png", scale=20, border=4, dark=TEAL, light="white")
    qr.save(DIST / "qr-questionnaire.svg", scale=20, border=4, dark=TEAL, light="white")
    # pure black, for mono photocopying and fax-grade reproduction
    qr.save(DIST / "qr-questionnaire-black.png", scale=20, border=4)

    print(f"QR version {qr.version}, error correction {qr.error.upper()}")
    print(f"encodes: {FORM_URL}")
    for name in ("qr-questionnaire.png", "qr-questionnaire.svg", "qr-questionnaire-black.png"):
        print(f"  wrote dist/{name}")

    verify()


def verify():
    """Decode the generated PNG back and confirm it round-trips to FORM_URL."""
    try:
        import cv2
    except ImportError:
        print("  (opencv-python not installed - skipping scan check)")
        return
    img = cv2.imread(str(DIST / "qr-questionnaire.png"))
    data, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
    if data == FORM_URL:
        print("  scan check: OK - decodes back to the exact URL")
    else:
        raise SystemExit(f"  scan check FAILED - decoded {data!r}")


if __name__ == "__main__":
    main()
