# User Story: US-051 - /bookmark Command to Save URLs to Joplin

**Status**: ✅ Completed
**Priority**: 🟡 Medium
**Story Points**: 5
**Created**: 2026-03-08
**Updated**: 2026-03-08
**Assigned Sprint**: Sprint 17

## Description

Add a `/bookmark <url>` command that saves a URL to Joplin as a note with full metadata, AI-generated tags, and an explicit `bookmark` tag. The command leverages existing URL enrichment (title, description, content type) and LLM tag generation, then stores the result in Joplin. This provides a quick, one-command way to save links for later reference without going through the full note-creation flow.

## User Story

As a user who encounters useful links throughout the day,
I want to run `/bookmark <url>` and have it saved to Joplin with metadata and tags,
so that I can quickly capture references without losing context or spending time on manual filing.

## Acceptance Criteria

### Core

- [ ] `/bookmark <url>` saves URL to Joplin as a note
- [ ] Uses existing URL enrichment (`fetch_url_context`) for title, description, extracted text
- [ ] AI generates content-appropriate tags (reuses existing tag logic from note creation)
- [ ] Note always includes the `bookmark` tag
- [ ] Success message: "✅ Bookmarked: {title}" with link to note
- [ ] `/bookmark` or `/bookmark invalid` shows usage: "Usage: /bookmark <url>"

### Optional

- [ ] `/bm <url>` or `/bm` as alias
- [ ] Optional inline tags: `/bookmark <url> #tag1 #tag2`
- [ ] Optional note: `/bookmark <url> my note here`
- [ ] Optional folder: save to `Resources/Bookmarks/` (or configurable)
- [ ] Duplicate URL detection: warn if URL already bookmarked, offer to add note or skip

### Error Handling

- [ ] Invalid or missing URL: show usage
- [ ] URL fetch fails: save with URL only, minimal metadata, note "Enrichment failed"
- [ ] Joplin unavailable: show error

## Business Value

- **Low friction**: One command instead of pasting URL into message flow
- **Consistency**: Every bookmark gets the same structure (PARA-aligned, tagged)
- **Discoverability**: `bookmark` tag enables filtering: `/find #bookmark` or search
- **Reuse**: Leverages existing URL enrichment and LLM—no new infrastructure

## Technical Requirements

### 1. Note Format

```markdown
# {title from URL or "Untitled Bookmark"}

**URL**: {url}
**Saved**: {date}
**Source**: {domain}

## Summary
{description or extracted_text snippet}

---
*Saved via /bookmark*
```

### 2. Tags

- **Required**: `bookmark`
- **AI-generated**: Same logic as note creation (content type, topic, domain)
- **User-provided**: If `/bookmark <url> #tag1 #tag2` supported

### 3. Folder

- Default: `Resources/Bookmarks/` (create if missing)
- Or: Inbox (simplest) with `bookmark` tag for filtering
- Configurable via env or user preference (future)

### 4. Implementation Flow

```
/bookmark <url>
       │
       ▼
┌──────────────────────┐
│ Validate URL         │
└──────────────────────┘
       │
       ▼
┌──────────────────────┐
│ fetch_url_context    │ (existing)
└──────────────────────┘
       │
       ▼
┌──────────────────────┐
│ LLM: generate tags   │ (from content, title, domain)
│ + append "bookmark"  │
└──────────────────────┘
       │
       ▼
┌──────────────────────┐
│ Create Joplin note   │
│ in Resources/Bookmarks│
└──────────────────────┘
       │
       ▼
┌──────────────────────┐
│ Confirm to user      │
└──────────────────────┘
```

### 5. Commands

| Command | Description |
|---------|-------------|
| `/bookmark <url>` | Save URL to Joplin with metadata and tags |
| `/bm <url>` | Shortcut for /bookmark |
| `/bookmark <url> #tag1 #tag2` | Save with additional user tags |
| `/bookmark <url> optional note` | Save with user-provided context |

### 6. Key Files

| File | Purpose |
|------|---------|
| `src/handlers/core.py` | Command handler (implemented in core, not a separate file) |
| `src/url_enrichment.py` | Reuse `fetch_url_context` |
| `src/llm_orchestrator.py` | Reuse tag generation or add lightweight variant |
| `src/joplin_client.py` | `create_note`, `get_or_create_folder_by_path` |

### 7. Duplicate Detection (Optional)

- Before creating, search Joplin for notes with same URL in body
- If found: "This URL is already bookmarked. Add a note? Reply with text or /cancel"

## Dependencies

- US-005: Joplin REST API Client ✅
- URL enrichment (existing in `url_enrichment.py`) ✅
- LLM for tag generation (existing) ✅

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| URL fetch timeout/fail | Save with URL only, minimal note |
| Paywall/login content | Same as existing URL handling—partial metadata |
| Duplicate bookmarks | Optional: search before create, warn user |
| Tag generation cost | Reuse existing; or use rule-based tags (domain, content_type) only |

## What Could Go Wrong & How to Fix It

### URL & Fetch Failures

| Failure | What happens | Fix |
|---------|--------------|-----|
| **Timeout** | Enrichment hangs, user waits | Set strict timeout (e.g. 12s); on timeout, save URL-only note with "Enrichment timed out" |
| **403 / 401** | Site blocks bot | Save URL + title from `<title>` if parseable; otherwise URL only. Tag `bookmark/partial` |
| **Cloudflare / challenge** | Security check blocks fetch | Same as 403; existing `_is_challenge_page` in url_enrichment skips screenshot |
| **Redirect to different domain** | Phishing, tracking redirect | Existing `_check_domain_mismatch`; if suspicious, save with warning, skip screenshot |
| **Malformed URL** | User sends `not a url` or `javascript:` | Validate URL scheme (http/https only); reject with "Usage: /bookmark <valid url>" |
| **Very long URL** | Some URLs are 2k+ chars | Truncate in note; store full URL in a field. Joplin handles long content |
| **PDF / video / binary** | Not HTML | Detect content-type; save URL + "Non-web page (PDF/video)" — no enrichment, minimal note |

### Joplin & Storage

| Failure | What happens | Fix |
|---------|--------------|-----|
| **Joplin API down** | Create note fails | Show "Joplin unavailable. Try again later." Don't lose URL — could queue for retry (future) |
| **Folder missing** | Resources/Bookmarks doesn't exist | `get_or_create_folder_by_path` — create on first use |
| **Sync conflict** | User edits note in Joplin while bot writes | Joplin handles; last write wins. Avoid editing same note from bot repeatedly |
| **10k+ bookmarks** | Search/duplicate check slow | Index by URL in logging DB (optional); or limit duplicate search to last N days |
| **Note too large** | Full-text archive hits Joplin limit | Truncate body (e.g. 100k chars); store "…truncated" marker |

### LLM & Tags

| Failure | What happens | Fix |
|---------|--------------|-----|
| **LLM timeout** | Tag generation hangs | Fallback: rule-based tags (domain, `bookmark`, content_type from enrichment) |
| **LLM parse error** | Invalid JSON / schema | Same fallback; never block save. Log for debugging |
| **LLM rate limit** | Provider throttles | Retry with backoff; or skip tags, save with `bookmark` only |
| **Empty tags** | LLM returns nothing | Always have `bookmark`; add `bookmark/domain-{domain}` as fallback |

### UX & Confusion

| Failure | What happens | Fix |
|---------|--------------|-----|
| **User doesn't know where it went** | "Did it work?" | Success message: "✅ Bookmarked: {title}\n📁 Resources/Bookmarks\n🔗 Open in Joplin" (optional `joplin://` deep link when available) |
| **User bookmarks same URL twice** | Duplicates | Duplicate detection; "Already bookmarked. Add note? Reply or /cancel" |
| **User sends URL in wrong format** | `/bookmark https://x.com yada` | Parse: first token = URL, rest = optional note. Validate URL first |
| **Forwarded message with multiple URLs** | Ambiguous | Take first URL only; or "Found 3 URLs. Bookmark which? 1 / 2 / 3 / all" |

### Security & Privacy

| Failure | What happens | Fix |
|---------|--------------|-----|
| **Malicious URL** | Phishing, drive-by | Validate scheme; optional: block known-bad domains (configurable list) |
| **URL leaks to third party** | Enrichment sends URL to external service | Document: URL goes to fetch + LLM. For sensitive links, offer "save without enrichment" |
| **Private / localhost URL** | User bookmarks `http://localhost:3000` | Allow (user's choice) but enrichment may fail — handle gracefully |

### Edge Cases

| Failure | What happens | Fix |
|---------|--------------|-----|
| **Unicode in URL** | `https://例え.jp/path` | URL-encode for fetch; store as-is in note. Handle IDN domains |
| **Rate limit (user)** | User bookmarks 50 in 1 min | Optional: throttle (e.g. 10/min), queue rest, or just allow (Joplin is local) |
| **Very long page** | 500k word article | Truncate extracted text (e.g. 20k chars); summary from first portion |
| **Login wall** | NYT, Medium paywall | Save with title + "Login may be required" — same as existing URL handling |

## World-Class Enhancements

What would make this feature best-in-class (Pocket, Raindrop, Pinboard level):

### Capture & Context

- **"Why am I saving this?"** — Optional prompt: "Why is this useful? (or skip)" — stores as first line of note. Creates retrieval context; "I saved this for the API examples" beats a bare URL.
- **Project linkage** — If project sync enabled: "Add to project? 1. Website Redesign 2. Skip" — bookmark lives in project References folder.
- **Instant confirmation with preview** — Thumbnail + title + domain in success message (reuse URL screenshot if available).

### Preservation & Link Rot

- **Archive full content** — Save reader-view or extracted text to note body (not just metadata). Link rot kills URLs; the note becomes the source of truth.
- **Broken link detection** — Periodic job: check bookmarks, tag `bookmark/broken` or `bookmark/archived` when unreachable.
- **Archive.org fallback** — On save, optionally store `https://web.archive.org/save/{url}` or link to existing archive.

### Discovery & Resurfacing

- **Full-text search** — Joplin already indexes note body; ensure bookmark notes have enough content for `/find` and `/ask` to work.
- **Related bookmarks** — On save: "You have 3 other bookmarks from github.com" — link to them in the note or in the reply.
- **Weekly digest** — "You saved 12 bookmarks this week. 5 unread. Top domains: GitHub (4), HN (3)."
- **Smart reminders** — "Remind me about this in 7 days" — creates a task or scheduled note.

### AI & Intelligence

- **AI summary + key takeaways** — Not just title/description: 3–5 bullet points, main argument, and "why it matters."
- **AI-suggested tags** — Already planned; extend to `bookmark/topic` (e.g. `bookmark/python`, `bookmark/productivity`).
- **Estimated read time** — From content length; show in note and in `/bookmarks` list.
- **Duplicate + similar** — "You already bookmarked a similar article: [title]. Add anyway?"

### Workflow Integration

- **One-tap to read-later** — "Also add to reading queue? Yes / No" — bridges bookmark (reference) and read-later (consumption).
- **Highlights & annotations** — When reading in Joplin, support inline highlights; sync back to bookmark note.
- **Export** — `/bookmark export` — JSON, HTML, or Markdown for backup or migration.

### Friction & Delight

- **Share-to-bookmark** — Mobile share sheet → Telegram → bot bookmarks it (user shares URL to bot).
- **Zero-tap from Telegram** — Forward a message with a link; bot detects URL and offers "Bookmark? /bookmark {url}".
- **Beautiful note template** — Clean, scannable layout: title, source, date, read time, summary, key points, tags, link.

### Pretty Cool Ideas

- **Serendipity mode** — `/bookmark random` — surface a random old bookmark you haven't touched in 6+ months. Rediscover forgotten gems.
- **Time capsule** — "On this day: 3 bookmarks you saved 1 year ago" — daily nostalgia in report or on demand.
- **Bookmark chains** — "This article references [X]. You bookmarked that in 2023." — show connections between saved links.
- **"Read this next"** — AI suggests which bookmark to read based on time of day, recent activity, or mood.
- **Bookmark → task** — "Create a task from this?" — e.g. "Implement the API from this article" — links bookmark note to Google Task.
- **Deduping by content** — Same article, different URL (Medium, Substack, etc.) — detect and merge or warn.
- **Bookmark stats** — "234 bookmarks. Top: programming (89), design (34). Longest read: 47 min."
- **Anti-hoarding nudge** — "47 unread bookmarks. Purge old ones?" — list by age, bulk archive.
- **Quick rating** — After save: "How useful? 1–5" — feeds into "read this next" and prioritization.
- **Bookmark bundles** — Save multiple URLs as one note: "Research: URL1, URL2, URL3" — for topic clusters.
- **Scheduled resurface** — "Random bookmark every Monday" — injected into daily report or as a standalone message.
- **Bookmark from screenshot** — OCR a photo of a URL, extract and bookmark.
- **Export to flashcard** — "Turn this article into flashcards" — links to existing flashcard feature.

## Future Enhancements

- [ ] `/bookmarks` or `/bookmark list` — show recent bookmarks
- [ ] Bookmark folders by domain (e.g. `Resources/Bookmarks/github.com/`)
- [ ] Archive old bookmarks (move to Archive after N days unread)
- [ ] Export bookmarks (JSON, HTML)
- [ ] Integration with read-later: bookmark = add to reading queue
- [ ] Screenshot attachment (reuse URL screenshot if enabled)

## Notes

- Differs from `/readlater`: bookmark is for reference/save; readlater is for consumption queue
- Both can coexist: user might bookmark for reference and also add to reading queue
- Consider `bookmark` as a top-level tag for easy filtering in Joplin

## History

- 2026-03-08 - Feature request created
- 2026-03-08 - Added World-Class Enhancements section (capture context, preservation, discovery, AI, workflow, friction)
- 2026-03-08 - Added Pretty Cool Ideas (serendipity, time capsule, chains, read-next, task link, voice, stats, etc.)
- 2026-03-08 - Added "What Could Go Wrong & How to Fix It" (URL, Joplin, LLM, UX, security, edge cases)
