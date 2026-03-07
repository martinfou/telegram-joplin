# Feature Request: FR-033 - Flashcard Practice from Notes

**Status**: 📝 Revision
**Priority**: 🟠 High
**Story Points**: 8
**Created**: 2026-03-05
**Updated**: 2026-03-06
**Assigned Sprint**: Backlog (Sprint 13 candidate)

## Description

A science-backed flashcard practice system that turns your Joplin notes into memory-building sessions. **AI automates deck creation**: you tag notes with `#flashcard` or `#practice`, and the AI builds flashcards from them—on a schedule or on demand. Practice what you want to remember—definitions, concepts, decisions, quotes—using **active recall** and **spaced repetition**. Designed to be fun, low-pressure, and highly effective. Your Second Brain becomes not just a capture system but a practice gym for your mind.

## Philosophy Alignment

This feature extends the project's information organization philosophy:

| Principle | How Flashcard Supports It |
|-----------|---------------------------|
| **PARA structure** | Filter practice by folder (Projects, Areas, Resources). Practice what matters *now*. |
| **Second Brain value** | Knowledge compounds only when retrieved. Flashcards turn capture into recall. |
| **Low friction** | Practice in Telegram—where you already are. No app switching. |
| **Organized, discoverable** | Tag notes with `#flashcard` or `#practice` to include in sessions. |
| **GTD + Learning** | Resources and Areas contain reference material worth remembering. |

## Science Foundation

### 1. Spaced Repetition (Ebbinghaus, 1885)

Memory fades over time. Reviewing *just before* you forget strengthens the memory more than cramming. Intervals should increase: 1 day → 6 days → 2 weeks → 1 month, etc.

**Implementation**: SM-2 algorithm (or simplified variant) for scheduling. Each card has an *easiness factor* and *interval*. Correct answers lengthen the interval; incorrect answers shorten it.

### 2. Active Recall / Retrieval Practice (Testing Effect)

The act of *retrieving* information from memory strengthens memory more than passive re-reading. Research shows 57%+ of classroom experiments demonstrate medium-to-large benefits from retrieval practice.

**Implementation**: Show question first. User must recall before seeing answer. No peeking.

### 3. Desirable Difficulty

Slight struggle during retrieval improves long-term retention. Don't make it trivial—but don't make it punishing either.

**Implementation**: Vary question types (recall, recognition, application). Allow "hard" vs "easy" self-rating to tune scheduling.

## User Story

As a user with notes I want to remember—concepts, decisions, quotes, facts—
I want to practice them as flashcards in Telegram using spaced repetition,
so that I strengthen my memory without it feeling like homework.

## Acceptance Criteria

### Core Flow

- [ ] `/flashcard` starts a practice session (default: 5–10 cards, or until queue empty)
- [ ] `/flashcard N` starts a session with up to N cards
- [ ] Cards show **question first**; user taps "Show answer" or sends a message to reveal
- [ ] After revealing, user rates: **Easy** | **Good** | **Hard** | **Again** (or simplified: 👍 / 👎)
- [ ] Session ends with a brief, encouraging summary (e.g., "🎯 7/8 today. Nice work!")
- [ ] `/flashcard_done` or "stop" / "done" ends session early

### AI Automation & Deck Building

- [ ] **Scheduled extraction**: AI runs on a schedule (e.g., nightly) to extract cards from all tagged notes
- [ ] **Explicit build**: `/flashcard build` triggers immediate extraction from tagged notes
- [ ] **Re-extraction**: When tagged notes are edited, re-extract during the next scheduled run (not immediately)
- [ ] Notes tagged with `#flashcard` or `#practice` are included in the pool
- [ ] **Separate decks**: Support deck-per-tag (e.g., `#flashcard-math`, `#flashcard-spanish`) for focused practice
- [ ] **Review before use**: User reviews AI-generated cards before they enter the deck (approve, edit, skip)
- [ ] **Card formats**: Q&A pairs, cloze deletion (fill-in-blank), and other formats as appropriate per note content
- [ ] **Conversational selection**: User can say "add these 3 notes to my deck" in chat (AI resolves note references)
- [ ] **Feedback on bad cards**: Skip, edit, or regenerate options when AI produces poor cards

### Card Source & Creation

- [ ] Cards are **extracted from Joplin notes** via LLM (1–5 cards per note; format varies by content)
- [ ] `/flashcard from <note title>` — generate cards from a specific note (bypasses tag requirement)
- [ ] `/flashcard folder <path>` — include notes from a folder in extraction (alternative to tags)
- [ ] `/flashcard add "Q" | "A"` — add a manual card (stored in Joplin or local DB)
- [ ] Cards link back to source note (for "open in Joplin" or context)

### Filtering (PARA-Aware)

- [ ] `/flashcard tag <tag>` — practice only cards from notes with that tag (deck selection)
- [ ] `/flashcard folder <path>` — practice only cards from notes in that folder (e.g. `Resources/Learning`)
- [ ] Default: all `#flashcard` / `#practice` notes across PARA structure

### Spaced Repetition

- [ ] Cards use SM-2–style scheduling (interval, easiness factor)
- [ ] "Again" → show again in same session, reschedule for 1 day
- [ ] "Hard" → shorter interval
- [ ] "Good" → standard interval increase
- [ ] "Easy" → longer interval
- [ ] New cards introduced gradually (e.g. 3–5 new per session)

### Fun & Tone

- [ ] Playful, encouraging messages (e.g., "🧠 Brain gains!", "You got this!")
- [ ] Optional streak tracking ("3-day practice streak 🔥")
- [ ] No guilt if user skips—light nudge only
- [ ] Session length kept short (3–5 min default)

### Stats & Discovery

- [ ] `/flashcard stats` — cards due, mastered, streak, session history
- [ ] `/flashcard list` — show which notes have cards, how many
- [ ] `/flashcard help` — quick usage guide

## Business Value

**Second Brain ROI**: Notes are valuable only when you can retrieve them. Flashcards turn passive capture into active practice. Users who practice their notes will:
- Remember key decisions and concepts when they matter
- Feel their note-taking pays off
- Stay engaged with their knowledge base

**Differentiation**: Most flashcard apps are generic. This one uses *your* notes—your decisions, your learnings, your Second Brain—as the source. Personalized and contextual.

## Technical Requirements

### 1. Architecture Overview

**Deck Building (Scheduled or Explicit)**

```
Schedule / User: /flashcard build
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│ 1. Fetch tagged notes (#flashcard, #practice, deck tags) │
│    Detect edited notes (updated_time) for re-extraction  │
└─────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│ 2. LLM extracts cards (Q&A, cloze) → pending_review     │
│    User runs /flashcard review → approve/edit/skip       │
└─────────────────────────────────────────────────────────┘
```

**Practice Session**

```
User: /flashcard
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│ 1. Load due cards (SM-2 schedule) + new active cards     │
│    Filter by deck tag/folder if specified                │
└─────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│ 2. For each card: show question → user reveals → rate   │
│    Update interval, next_review_date, easiness           │
└─────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Session summary + optional streak update              │
└─────────────────────────────────────────────────────────┘
```

### 2. Card Extraction (LLM)

**Triggers**: (1) Scheduled job (e.g., nightly), (2) `/flashcard build`, (3) `/flashcard from <note>`, (4) conversational "add these notes to my deck"

**Re-extraction**: During scheduled runs, detect edited tagged notes (e.g., via `updated_time`) and re-extract. Replace existing cards from that note.

```python
EXTRACT_CARDS_PROMPT = """Extract 1-5 flashcards from this note.
Use the format that fits best for each item:
- Q&A: {"type": "qa", "question": "...", "answer": "..."}
- Cloze: {"type": "cloze", "text": "... {{c1::blank}} ...", "hint": "optional"}
Focus on: definitions, key facts, decisions, quotes, concepts worth remembering.
Keep questions short (< 100 chars). Answers 1-3 sentences."""
```

- Store extracted cards in local DB with `note_id`, `type`, `question`/`answer` or `text`/`hint`
- **Review queue**: New cards enter a "pending review" state; user approves/edits/skips before they join the deck

### 3. Data Model

```python
class Flashcard(BaseModel):
    id: str
    user_id: int
    note_id: str
    deck_tag: str  # e.g. "flashcard", "flashcard-math" — for separate decks
    card_type: str  # "qa" | "cloze" | ...
    question: str  # or cloze text
    answer: str    # or hint (for cloze)
    status: str   # "pending_review" | "active"
    created_at: datetime

class CardReview(BaseModel):
    id: str
    card_id: str
    user_id: int
    rating: str  # "again" | "hard" | "good" | "easy"
    interval_days: float
    easiness_factor: float
    next_review: date
    reviewed_at: datetime
```

### 4. Database Schema (SQLite)

```sql
CREATE TABLE flashcards (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    note_id TEXT NOT NULL,
    deck_tag TEXT NOT NULL,
    card_type TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    status TEXT DEFAULT 'pending_review',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES telegram_users(user_id)
);

CREATE TABLE flashcard_review_queue (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    card_id TEXT NOT NULL,
    FOREIGN KEY (card_id) REFERENCES flashcards(id)
);

CREATE TABLE card_reviews (
    id TEXT PRIMARY KEY,
    card_id TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    rating TEXT NOT NULL,
    interval_days REAL NOT NULL,
    easiness_factor REAL NOT NULL,
    next_review DATE NOT NULL,
    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (card_id) REFERENCES flashcards(id)
);

CREATE TABLE flashcard_sessions (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cards_shown INTEGER DEFAULT 0,
    cards_correct INTEGER DEFAULT 0,
    ended_at TIMESTAMP
);

CREATE INDEX idx_reviews_next ON card_reviews(user_id, next_review);
CREATE INDEX idx_cards_user ON flashcards(user_id);
CREATE INDEX idx_cards_deck ON flashcards(user_id, deck_tag);
CREATE INDEX idx_cards_status ON flashcards(user_id, status);
```

### 5. SM-2 Scheduling (Simplified)

```python
def schedule_card(rating: str, interval: float, ef: float) -> tuple[float, float]:
    """Returns (new_interval_days, new_ef)."""
    if rating == "again":
        return (1.0, max(1.3, ef - 0.2))
    if rating == "hard":
        return (interval * 1.2, max(1.3, ef - 0.15))
    if rating == "good":
        return (interval * ef, ef)
    if rating == "easy":
        return (interval * ef * 1.3, min(2.5, ef + 0.15))
```

### 6. Session Flow (Telegram)

```
User: /flashcard

Bot: 🧠 Flashcard time! You have 12 cards due today.
     [Start Session] [5 cards] [10 cards]

User: [clicks Start Session]

Bot: 📌 Card 1/5
     Q: What is the main benefit of spaced repetition?
     [Show answer]

User: [clicks Show answer]

Bot: A: Reviewing just before you forget strengthens memory
     more than cramming. Intervals increase over time.
     [Again] [Hard] [Good] [Easy]

User: [clicks Good]

Bot: 📌 Card 2/5
     Q: ...
```

### 7. Commands Summary

| Command | Description |
|---------|-------------|
| `/flashcard` | Start session (default length) |
| `/flashcard N` | Start session with up to N cards |
| `/flashcard build` | Trigger AI extraction from all tagged notes (immediate) |
| `/flashcard tag <tag>` | Filter by tag (deck selection) |
| `/flashcard folder <path>` | Filter by folder |
| `/flashcard from <note>` | Generate cards from specific note |
| `/flashcard add "Q" \| "A"` | Add manual card |
| `/flashcard review` | Review pending AI-generated cards (approve/edit/skip) |
| `/flashcard stats` | Due count, streak, history |
| `/flashcard list` | Notes with cards |
| `/flashcard help` | Usage guide |
| `/flashcard_done` | End session early |

## Implementation

### Key Files to Create

| File | Purpose |
|------|---------|
| `src/flashcard_service.py` | Card CRUD, SM-2 scheduling, session logic, deck management |
| `src/flashcard_scheduler.py` | Scheduled extraction job (e.g., nightly; time configurable per user) |
| `src/handlers/flashcard.py` | Command handlers, inline keyboards, review queue UI |
| `src/prompts/flashcard_extractor.txt` | LLM prompt for multi-format extraction |
| `tests/test_flashcard.py` | Unit tests |

### Key Files to Modify

| File | Changes |
|------|---------|
| `src/handlers/__init__.py` | Register flashcard handlers |
| `src/joplin_client.py` | Fetch notes by tag, by folder |
| `src/llm_orchestrator.py` | Add `extract_flashcards_from_note()`, conversational "add notes to deck" |
| Database migrations | Create flashcard tables, review queue |

### Inline Keyboard (python-telegram-bot)

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def build_card_keyboard(phase: str) -> InlineKeyboardMarkup:
    if phase == "question":
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("👀 Show answer", callback_data="fc_show")
        ]])
    if phase == "answer":
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 Again", callback_data="fc_again"),
            InlineKeyboardButton("😓 Hard", callback_data="fc_hard"),
            InlineKeyboardButton("👍 Good", callback_data="fc_good"),
            InlineKeyboardButton("😊 Easy", callback_data="fc_easy"),
        ]])
```

## Testing

### Unit Tests

- [ ] SM-2 scheduling (each rating path)
- [ ] Card extraction from sample note (Q&A, cloze formats)
- [ ] Due card selection (respects next_review)
- [ ] Session state (start, next card, end)
- [ ] Filter by deck tag/folder
- [ ] Scheduled extraction (edited notes re-extracted)
- [ ] Review queue (pending → approve/edit/skip → active)

### Manual Testing Scenarios

| Action | Expected |
|--------|----------|
| Tag note with #flashcard, run `/flashcard build` | Cards extracted, enter pending review |
| `/flashcard review` | Shows pending cards; approve/edit/skip each |
| Scheduled run (nightly) | Extracts from tagged notes; re-extracts edited notes |
| "Add these 3 notes to my deck" (chat) | AI resolves notes, extracts cards |
| `/flashcard` with 5 due | 5 cards shown, ratings update schedule |
| `/flashcard stats` | Shows due count, streak |
| `/flashcard_done` mid-session | Session ends, progress saved |

## Dependencies

- FR-005: Joplin REST API Client (fetch notes by tag/folder)
- FR-006: LLM Integration (card extraction)
- FR-007: Conversation State Management (session state)
- FR-016: PARA structure (folder filtering)

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| LLM extracts poor Q&A pairs | Review queue: approve/edit/skip before deck; regenerate option |
| Too many cards overwhelming | Cap new cards per session, default 5 |
| User forgets to practice | Optional daily reminder (like habits) |
| Cards go stale when note changes | Re-extract during scheduled run (detect via `updated_time`) |
| Review queue backlog | Notify user when new cards await review; batch review UI |

## Future Enhancements

- [ ] Image cards (from note attachments)
- [ ] "Leitner box" visual for progress
- [ ] Export/import Anki deck
- [ ] Integration with FR-032 (habit) — "practice flashcards" as a habit
- [ ] Weekly flashcard stats in FR-015 (weekly report)

## Notes

- **Fun but effective**: Use emoji, short encouraging phrases. No long lectures.
- **Respect PARA**: Users organize by Projects/Areas/Resources. Let them practice what's relevant.
- **Lightweight**: 3–5 min sessions. No commitment to "daily 30 min."
- **Science-first**: SM-2 is proven. Don't over-engineer—simple intervals beat complex heuristics for MVP.

## Reference Documents

- Ebbinghaus, H. (1885). *Memory: A Contribution to Experimental Psychology*
- SuperMemo SM-2 Algorithm: https://www.supermemo.com/en/archives1990-2015/english/ol/sm2
- Testing effect / retrieval practice: Roediger & Karpicke (2006), *Psychological Science*
- PARA Method: https://fortelabs.com/blog/para/
- FR-016: Joplin Database Reorganization (folder structure)
- FR-032: Habit Tracking (optional integration)

## History

- 2026-03-05 - Feature request created
- 2026-03-06 - Revision: AI-automated deck building; scheduled + explicit build; separate decks; review queue; multi-format cards; conversational selection; skip/edit/regenerate feedback
