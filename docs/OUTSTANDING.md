# Outstanding items

Open questions and gaps, as of the initial commit. Nothing here is resolved.

## Blocking — must be settled before any patient receives this form

### 1. Clinical sign-off
The clinical content has not been reviewed by the Immunology consultants or specialist
nurses. It was drafted from general immunoglobulin safety knowledge, not from local
policy. Specific decisions needed:

- **Is the 999 / same-day split right?** Thrombotic signs (chest pain, one-sided
  weakness, limb swelling) are currently in the 999 box; haemolysis, aseptic meningitis
  and renal signs are in the same-day box.
- **Should "fever with rigors" be 999 rather than same-day?** Rigors during or after an
  infusion may indicate sepsis in an immunodeficient patient.
- **Should the anaphylaxis box tell patients to use an adrenaline auto-injector** if
  they are prescribed one? It currently does not mention it.
- **Does the red-flag list match the local escalation SOP?**

- **The shortened form no longer captures structured symptom checklists.** Questions 3
  to 5 were removed, so nurses now rely on the patient's free-text description of the
  reaction.
- **The shortened form no longer performs red-flag screening.** The page-one 999 and
  "contact the team today" boxes are now the only escalation guidance in the form.

### 2. The QR target must be publicly reachable
The QR encodes a hosted copy of the web form. A scanned link cannot prompt for a
sign-in, so the target must open for anyone. If the page is private or access
controlled, every patient scan fails. Verify by opening the URL while signed out.

### 3. Information governance
- The form is currently hosted on a third-party domain (`claude.ai`). Whether that is
  acceptable for a patient-facing NHS form is an IG decision. Hosting on a Royal Free
  domain is the cleaner answer — see the README for how to repoint the QR.
- No **privacy notice**: patients are not told what happens to their data, how long it
  is kept, or the legal basis for processing it. This is special-category health data
  under UK GDPR.
- A **DPIA** may be required. Note in mitigation that the form transmits nothing itself:
  web answers stay in the browser's `localStorage` and leave only via the patient's own
  email client.
- **Shared devices.** Answers persist in the browser until cleared. There is a "clear my
  answers" button, but it is opt-in.
- **Email is not secure by default.** A patient emailing identifiable health data to an
  nhs.net mailbox is common practice, but should be acknowledged rather than assumed.

### 4. No delivery assurance
The design depends on the patient successfully sending an email. There is no receipt,
no audit trail, and no way to know a report was written but never sent. For adverse
reaction reporting this is a governance gap. Closing it means a real submission backend
(a form posting to a monitored mailbox or database) rather than `mailto:`.

### 5. Yellow Card and haemovigilance
Immunoglobulin is a plasma-derived medicine. Reactions should feed the MHRA **Yellow
Card** scheme, and serious ones may require **SHOT / SABRE** reporting. The form does
not mention this, does not say who performs it, and does not capture patient consent to
report onward. Decide who owns the step and whether it should be stated on the form.

### 6. No version control block
Clinical documents normally carry a version number, author, approval date and review
date. The form carries none, so a returned copy cannot be traced to a version. Supply
the four values and they can be added to the footer.

## Should fix before wide release

- **Reading age.** NHS patient information targets roughly age 11. Several terms exceed
  that: *rigors*, *hyaluronidase*, *facilitated SCIG*, and the haemolysis phrasing.
  A plain-English pass, ideally with a patient panel, is warranted.
- **Accessibility not formally tested.** The web form is built to be keyboard and
  screen-reader friendly, but has not been tested with JAWS, NVDA or VoiceOver, nor
  formally audited against **WCAG 2.2 AA**, which NHS digital services must meet.
- **No translations and no easy-read version.** Consider the equality duty for the
  patient cohort.
- **Two artifacts to keep in sync.** The PDF and the web form hold the same questions in
  separate files and can drift. Decide which is canonical.
- **Print fresh, do not photocopy.** The QR survives distance, poor focus and dim
  lighting, but degrades on heavily reproduced copies.

## Confirmed

- **UK / NHS context** — confirmed by the Royal Free contact details (`rf-tr` prefix,
  020 7794 0500). The form uses 999, A&E, NHS 111, NHS number and British spellings.
