# User Story: US-057 - Parse health data from Garmin, FatSecret, and Arboleaf

[← Back to Product Backlog](../product-backlog.md)

**Status**: ⏳ In Progress (Sprint 21 stretch)
**Priority**: 🟡 Medium
**Story Points**: 8
**Created**: 2026-03-10
**Updated**: 2026-04-06 (goals + weekly Joplin note)
**Assigned Sprint**: Sprint 21

---

## Summary

Create a **world-class “health capture + summary” feature** that lets users send their Garmin / FatSecret / Arboleaf health data (via paste, screenshots, or exports) and get a clean daily/weekly summary in Telegram, with **always-on storage in a dedicated database** and **automatic weekly notes in Joplin**.

Key principle: **don’t block on vendor APIs**. Start with robust parsing of user-provided data, then optionally add direct API connectors later.

---

## User Story

As a health-conscious user,
I want to send my fitness, nutrition, and body metrics from Garmin, FatSecret, and Arboleaf to the bot and get a unified daily/weekly view,
so that I can track my health consistently without juggling 3 apps.

---

## UX / Commands (MVP)

### 1) Capture

- `/health_import` — guided import wizard (recommended)
  - supports: text paste, file upload, screenshots
  - auto-detect source; if uncertain, asks which source
  - shows a parse preview and asks to confirm save (with an option to “always auto-confirm” later)
- `/health_import <source>` — explicit source override: `garmin|fatsecret|arboleaf`
- `/health_import_quick <text>` — quick parse from a single message (no wizard)

### 2) Review

- `/health_today` — summary for the current day (user timezone)
- `/health_week` — last 7 days rollup (trends + highlights)
- `/health_last` — last captured datapoint per source (sanity check)

### 3) Goals (world-class but small)

- `/health_goal <metric> <value>` — examples:
  - `/health_goal steps 10000`
  - `/health_goal protein_g 160`
  - `/health_goal weight_kg 78`
- `/health_goals` — show goals + adherence (weekly)

### 4) Joplin notes (automatic weekly)

- When imports occur, the bot creates/updates a **weekly** Joplin note under:
  - `01 - Areas / 💪 Health & Fitness / Weekly Health`
- Title format: `YYYY-Www - Health Summary` (e.g. `2026-W12 - Health Summary`)
- Week boundaries: **Monday–Sunday** in the user’s configured timezone

---

## Inputs Supported (MVP)

### Garmin

Supported user inputs:
- **Screenshot OCR** of:
  - daily steps, distance, active calories
  - sleep duration + score (if available)
  - resting HR / avg HR (if available)
- **Copy/paste** from Garmin daily summary screens (freeform text)
- **Export files**: Garmin Connect **Activities.csv** (activity feed)

### FatSecret

Supported user inputs:
- **CSV export** (primary) — capture **full food item list** (per-item entries), not just daily totals
- Copy/paste daily summary text (fallback)
- Screenshot OCR (fallback)

### Arboleaf

Supported user inputs:
- Export CSV (primary)
- Screenshot OCR of weigh-in results (fallback)

---

## Output Format (Telegram)

### Daily summary example

- Header includes date (user timezone) and sources included
- Clear sections with missing-data handling

Example:

**📈 Health — 2026-03-19**

**🏃 Activity (Garmin)**
- Steps: 8,412
- Distance: 6.1 km
- Active calories: 410

**😴 Sleep (Garmin)**
- Duration: 7h 12m
- Sleep score: 78

**🍽️ Nutrition (FatSecret)**
- Calories: 2,140
- Protein / Carbs / Fat: 155g / 210g / 62g

**⚖️ Body (Arboleaf)**
- Weight: 78.4 kg
- Body fat: 16.8%

### Weekly summary example

- Trends (up/down) and highlights (best sleep, highest protein day, weight trend)
- Avoid over-medicalizing: factual, neutral tone

Example:

**📈 Health Week — 11–17 Mar 2026**

**🏃 Activity** — 4 workouts, 28.2 km total, ~1,840 kcal  
**🍽️ Nutrition** — Avg 2,100 kcal, 152g protein; top: Chicken stir-fry, Oats  
**⚖️ Body** — Weight 78.4 → 78.1 kg (−0.3)  
**🎯 Goals** — Steps: 5/7 days ≥ 10k; Protein: 6/7 days ≥ 160g  
**💡 Insights** — [Short AI-generated summary when enabled]

---

## Data Model (canonical)

Store parsed data as a normalized dict with:

- `date` (YYYY-MM-DD, in user timezone)
- `source` ∈ {`garmin`, `fatsecret`, `arboleaf`}
- `metrics` (numbers with units standardized; store normalized e.g. kg, km, kcal; display in same units for MVP, preference later)
- `raw_rows` (original row/items as JSON for audit/debug; always stored)
- `confidence` per metric (0–1)

Additionally store:
- `row_hash` (row-level dedupe; normalized row → hash)
- `import_id` linking rows to an import event (file/message)
- `import_source_hint` (filename/headers used for detection)

### Standardized metrics (MVP)

- Activity:
  - `steps` (int)
  - `distance_km` (float)
  - `active_calories_kcal` (int)
- Sleep:
  - `sleep_duration_min` (int)
  - `sleep_score` (int, optional)
- Heart:
  - `resting_hr_bpm` (int, optional)
  - `avg_hr_bpm` (int, optional)
- Nutrition:
  - `calories_kcal` (int)
  - `protein_g` (int)
  - `carbs_g` (int)
  - `fat_g` (int)
- Body comp:
  - `weight_kg` (float)
  - `bmi` (float, optional)
  - `body_fat_pct` (float, optional)
  - `muscle_mass_kg` (float, optional)

---

## Privacy, Safety, and Consent

- Default behavior is **local-only processing** with the bot’s configured providers (no third-party sharing beyond what is already configured).
- **No medical advice**. Summaries are descriptive and avoid diagnosis/prescription language.
- Weekly Joplin notes should avoid dumping raw rows by default; raw rows live in DB and can be exported on request.
- Users can delete stored health data:
  - `/health_delete_day YYYY-MM-DD`
  - `/health_delete_all confirm`

---

## Acceptance Criteria (Implementation-Ready)

### AC-1: Smart import + preview + confirm

- [ ] `/health_import` accepts a CSV upload or pasted message, auto-detects source (or asks), parses rows, and shows a preview:
  - “Detected: Garmin Activities.csv” (or chosen source)
  - “Parsed: X rows, covering Y day(s)”
  - Preview shows 3 sample items (activity/food/weigh-in)
- [ ] User can Confirm / Cancel.

### AC-2: Multi-source merge by date

- [ ] If user imports Garmin + FatSecret + Arboleaf for the same day, `/health_today` shows one merged view with source attribution.
- [ ] Missing sections are shown as “(not provided)” without errors.

### AC-3: OCR-supported inputs

- [ ] The import flow supports image inputs (same OCR pipeline used elsewhere) and produces the same canonical schema.

### AC-4: Weekly summary

- [ ] `/health_week` aggregates the last 7 days (user timezone) and shows:
  - activity: workouts count, total active calories, total time, avg HR where available
  - nutrition: calories avg, macros avg, top food items (by calories)
  - body: weight trend (and body fat trend if present)
  - goals: adherence per configured goal

### AC-5: Database storage (always-on) + row-level dedupe

- [ ] Every parsed item is stored in a **new dedicated SQLite DB** (not logs/state DB).
- [ ] Raw rows/items are always stored as JSON for audit/debug.
- [ ] Row-level dedupe: “same row” = identical normalized row content (stable JSON: sorted keys, trimmed values, normalized numbers). Hash the normalized row; re-importing the same CSV does not duplicate rows.

### AC-6: Weekly Joplin note auto-create + merge behavior

- [ ] On import confirm, the bot creates/updates the weekly note under:
  - `01 - Areas / 💪 Health & Fitness / Weekly Health` (create folder path if missing).
- [ ] Weekly note title is `YYYY-Www - Health Summary` (ISO week with Monday start, in user timezone).
- [ ] If the note exists:
  - additive changes (new days/items) auto-merge
  - overwrites trigger a prompt: Replace values / Keep existing / Create v2 note
- [ ] Note format is idempotent via section markers (updates replace correct sections).

### AC-7: Trust layer (confidence + anomaly flags + diffs)

- [ ] Each metric/item has a confidence score.
- [ ] Obvious anomalies are flagged in weekly summary (neutral wording), and never silently overwrite existing weekly note values.
- [ ] When overwriting, the user sees a diff (“Old vs New”) for the affected day/metric/item.

### AC-8: Insights (AI) + consented all-notes context

- [ ] Weekly summary includes a short “Insights” section by default.
- [ ] Before using Joplin notes as context for insights (beyond health DB + weekly health notes), the bot **must** prompt: “Use `01 - Areas` notes for context? yes/no”.
  - If user says **yes**: allow reading notes under the `01 - Areas` notebook tree (and all descendants) only.
  - If user says **no**: use only health DB + current (and optionally past) weekly health notes.
- [ ] Insights may use all metrics + food items + activity titles; no medical advice language.

### AC-9: Error handling

- [ ] If parsing fails, user gets a concise message and an example of what to upload/paste.
- [ ] When one message/file contains multiple sources (or multiple files in one flow), if one source fails to parse, the others are still processed and reported separately.

### AC-10: Performance

- [ ] Typical import of a CSV with up to 500 rows completes in < 10s locally (excluding external APIs).

---

## Implementation Notes (LLM-friendly)

### Parsing approach (recommended)

- Use a **two-pass strategy**:
  1) deterministic extraction via regex + unit normalization
  2) fallback to LLM “structured extraction” if regex confidence is low

### Output contract for LLM extraction

LLM must return JSON:

```json
{
  "date": "YYYY-MM-DD",
  "source": "garmin|fatsecret|arboleaf",
  "metrics": { "steps": 8412, "weight_kg": 78.4 },
  "confidence": { "steps": 0.92, "weight_kg": 0.88 }
}
```

### World-class feature add-ons (post-MVP)

- **Personalized coaching insights (opt-in)**:
  - gentle trend detection (“Sleep is trending down 3 days in a row”)
  - correlation hints (“Higher protein days correlate with better satiety notes”)
- **Data connectors (optional)**:
  - Garmin / FatSecret API auth flows (only after MVP proves value)

*Note: Goal tracking (`/health_goal`, `/health_goals`, adherence in weekly report) is **in scope for MVP**; see UX and AC-4.*

### Deterministic parsing rules (must-have)

- Numbers may contain thousands separators: `"1,402"` → `1402`
- Missing values may be `"--"` → `null`
- Durations:
  - `Time` may be `HH:MM:SS` or `HH:MM:SS.s` (parse to seconds)
- Dates:
  - Garmin `Date` includes timestamp `YYYY-MM-DD HH:MM:SS` (interpret as user timezone unless CSV indicates otherwise)
- Row-level dedupe:
  - normalize row to stable JSON (sorted keys, trim whitespace, normalize numeric strings), then hash

### Test fixtures (required)

- Add sample files under `tests/fixtures/health/`:
  - `garmin_activities.csv` (match Garmin Connect Activities.csv column structure)
  - `fatsecret_export.csv`
  - `arboleaf_export.csv`
- Tests must assert:
  - correct row counts
  - correct parsing of commas/`--`/durations
  - stable hashing/dedup on re-import
  - weekly note merge behavior prompts only on overwrite

---

## Technical References

- Handlers:
  - `src/handlers/core.py` (register commands, routing)
  - Prefer new module: `src/handlers/health.py` for all health commands
- OCR pipeline:
  - `src/handlers/photo.py` (image to text)
- Joplin saving:
  - `src/joplin_client.py`
- Tests:
  - `tests/test_health_import.py` (new)

---

## Dependencies

- OCR capability (already present)
- Joplin client (already present)
- Optional: Gemini key (only if using LLM fallback parsing or generating insights)

---

## Resolved / Decided

- **Insights context (Joplin scope)**: Instead of “all Joplin notes”, the maximum scope is the `01 - Areas` notebook tree (and all descendants). Bot asks each time before using this context; if user says no → use only health DB + current (and past) weekly health notes. (Reflected in AC-8.)
- **Attachments (MVP)**: Do **not** store original CSV/files in Joplin for MVP. Store only row hashes + raw row JSON in DB. Optional later: attach original file as Joplin resource for audit.

## Open Questions (to answer before implementation)

- [ ] Display units: store normalized (kg, km, kcal). For MVP, display in same units; add user preference (e.g. lb, mi) in a later story?

---

## History

- 2026-03-10 - Created
- 2026-03-19 - Rewritten into implementation-ready “world-class” spec (CSV-first, always-on DB, weekly notes, trust + goals + insights)
- 2026-03-19 - Review: goals fixed as MVP; weekly example, FatSecret full items, AC-5/6/8/9 clarified; open questions resolved; display units + fixtures + tech refs tightened
- 2026-04-06 - **Partial delivery** on `main`: import + summaries + DB + fixtures; **`/health_goal`** / **`/health_goals`** and rolling 7-day adherence on **`/health_week`**; **weekly Joplin note** after import (`YYYY-Www - Health Summary` under `01 - Areas / 💪 Health & Fitness / Weekly Health`, ISO Mon–Sun rollups + goals). Still open: preview/confirm wizard, OCR path, AI insights (AC-8), trust/diff UX (AC-7).
