# Immunoglobulin Reaction Report

A patient-facing adverse reaction report form for **home therapy patients on IVIG or SCIG**.
Completed reports go to the **Immunology Specialist Nurses / Immunology Consultant**,
Clinical Immunology, Royal Free London.

**Live at <https://immunoglobulin-reaction-report.vercel.app/>** — deployed from `dist/` on every push to `main`.

> ### ⚠️ Status: draft — not approved for clinical use
>
> The clinical content of this form has **not been signed off** by the Immunology
> consultants or specialist nurses. The escalation thresholds, red-flag lists and
> symptom sets were drafted from general immunoglobulin safety knowledge and must be
> reviewed against local policy before any patient receives this form.
> See [`docs/OUTSTANDING.md`](docs/OUTSTANDING.md) for the full list of open items.

## What this is

The same questionnaire in two formats, built from one set of questions:

| Format | File | Use |
|---|---|---|
| Fillable PDF | `dist/immunoglobulin-reaction-report.pdf` | 6 pages, 88 AcroForm fields. Patients type into it, save, and email it back — or print and fill it in by hand. |
| Interactive web form | `dist/index.html` | Single self-contained file. Better on a phone: autosaves as you type, reviews your answers, then emails or prints them. |

Both carry a QR code pointing at the hosted web form, so a printed sheet leads a
patient to the phone version.

### How the form is structured

1. **Triage first.** Page one splits emergencies into two tiers — a red *call 999*
   box (anaphylaxis and thrombotic signs) and an amber *contact the team today* box
   (aseptic meningitis, haemolysis, renal signs). Contact details appear before any
   question, and again in the footer of every page.
2. **Batch traceability.** The batch/lot number has its own highlighted box, since
   immunoglobulin is a plasma-derived product and tracing the exact vial is the point
   of the report.
3. **Infusion context.** New batch, recent brand switch, infusion rate, pre-medication,
   and intercurrent illness — the things a nurse would otherwise have to ring and ask.
4. **Reaction detail.** Onset banded relative to the infusion (during / 1h / 6h / 24h /
   3 days / later), symptoms split into whole-body and infusion-site, plus a same-day
   red-flag set. In the web version, ticking a red flag raises a live "ring today" alert.

No patient data is transmitted anywhere by the form itself. Web answers stay in the
browser (`localStorage`) and leave only when the patient sends them from their own
email client.

## Contact details baked into the form

- **Immunology Specialist Nurses:** 020 7794 0500, ext. 32232 or 32233
- **Team mailbox:** rf-tr.clinicalimmunology@nhs.net

These appear in `src/build_pdf.py` (constants `TEL`, `TEL_SHORT`, `EMAIL`) and in
`src/form.html`. Change them in both places, then rebuild.

## Rebuilding

Requires Python 3.9+.

```bash
pip install -r src/src/requirements.txt   build deps (kept out of the repo root so the
                 host does not mistake this for a Python web app)
python src/make_qr.py      # writes the QR into dist/ and verifies it decodes
python src/build_pdf.py    # builds the 6-page fillable PDF into dist/
```

`make_qr.py` must run first — `build_pdf.py` embeds `dist/qr-questionnaire.png`.

The web form is authored directly as `src/form.html`. To produce the standalone
deliverable, wrap it in an HTML shell:

```bash
{ printf '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n</head>\n<body>\n'; cat src/form.html; printf '\n</body>\n</html>\n'; } > dist/index.html
```

### Changing where the QR points

The QR currently encodes a hosted copy of the web form. If the form moves to a Royal
Free domain — which is the likely outcome of information-governance review — edit
`FORM_URL` in `src/make_qr.py` **and** `QR_URL_TEXT` in `src/build_pdf.py` (the
human-readable fallback printed beside the code), then re-run both scripts.

**The QR target must open without a sign-in.** A scanned link cannot prompt for a
login, so a private or access-controlled URL produces a dead QR for every patient.

## Layout

```
src/
  build_pdf.py   two-pass AcroForm PDF generator (page count needs pass one)
  make_qr.py     QR generator, with a decode check
  form.html      source of the interactive web form
dist/            built deliverables — PDF, index.html (the hosted form), QR variants
docs/
  OUTSTANDING.md open clinical, governance and accessibility items
```

## Notes for whoever edits this next

- **Every PDF form field uses Helvetica.** Introducing a second base font (Courier for
  batch numbers was the tempting one) makes ReportLab emit a duplicate `/Font` key in
  the AcroForm resource dictionary, which strict PDF readers reject.
- **Radio buttons are drawn, not styled.** ReportLab's own radio appearance uses a
  shadowed-circle dingbat that looks broken at print size, so the circle is drawn on
  the page and a borderless widget sits on top.
- **The PDF builds twice.** The first pass only counts pages so the footer can print a
  real "Page N of M".
- `qlabel(..., keep=N)` reserves vertical space for the answers that follow, so a
  question never gets orphaned at the foot of a page. Adjust `keep` if you add options.
