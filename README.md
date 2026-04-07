# Intelligent Joplin Librarian

[![CI](https://github.com/martinfou/telegram-joplin/actions/workflows/ci.yml/badge.svg)](https://github.com/martinfou/telegram-joplin/actions/workflows/ci.yml) [🔄 Force Deploy](https://github.com/martinfou/telegram-joplin/actions/workflows/ci.yml)

**Stop carrying everything in your head.** This Telegram bot combines two of the most powerful productivity systems ever created — **Getting Things Done (GTD)** and the **Second Brain (PARA)** — into a single, frictionless interface you already use every day: your phone.

Send a message. The AI figures out the rest.

<p align="center">
  <img src="docs/images/gtd-second-brain-workflow.png" alt="GTD + Second Brain: The Unified Productivity Workflow" width="600">
</p>

---

## The Problem

You have ideas in your head, tasks on sticky notes, articles bookmarked and forgotten, meeting notes scattered across apps, and a vague sense that you're forgetting something important.

**You don't have a memory problem. You have a system problem.**

Your brain is for *having* ideas, not *holding* them. But most tools force you to decide: *Where does this go? What folder? What tag? Is this a task or a note?* So you end up dumping everything in one place — or worse, nowhere at all.

## The Solution: GTD + Second Brain, on Autopilot

This bot brings together two proven methodologies and lets AI handle the organizing:

| System | What it does | Tool | The question it answers |
|--------|-------------|------|------------------------|
| **GTD** (Getting Things Done) | Manages your *actions* | Google Tasks | "What should I do next?" |
| **Second Brain** (PARA) | Manages your *knowledge* | Joplin | "What do I know about this?" |

**GTD** keeps you moving — every project has a concrete next action, nothing falls through the cracks.

**Second Brain** keeps you thinking — every idea, reference, and insight is captured, organized, and findable when you need it.

Together, they mean you never lose a thought *and* you always know what to do next.

---

## How It Works

Open Telegram. Send a message. That's it.

**You say:** *"Meeting with Sarah — she wants to move the launch to March 15, I need to update the timeline and tell the design team"*

**The bot creates:**
- A **Joplin note** in your Projects folder with the meeting details, key decisions, and context
- A **Google Task**: "Update launch timeline to March 15"
- A **Google Task**: "Tell design team about new launch date"

Tags applied automatically. Folder chosen by AI. Action items extracted and ready to check off.

### More examples

| You send | What happens |
|----------|-------------|
| *"I need to renew my passport before June"* | Google Task created with deadline |
| *A URL to an interesting article* | Joplin note with summary, key points, and tags |
| *"Recipe: Mike's BBQ rub — 2 tbsp paprika, 1 tbsp brown sugar..."* | Note in Resources/🍽️ Recipe with recipe tag |
| *"Idea: what if the app could track habits too"* | Note captured in Inbox for later processing |
| `/braindump` | Guided 15-minute GTD mind-sweep that empties your brain into organized notes and tasks |
| `/task Call mom about Sunday dinner` | Single Google Task — no note needed |

---

## The CODE Workflow: From Information to Knowledge

The bot follows the **CODE** method from Building a Second Brain:

### Capture

Send anything to the bot — thoughts, URLs, meeting notes, recipes, ideas, book highlights. Don't worry about where it goes. Just capture it.

### Organize

AI automatically files your notes using the **PARA** method:

- **Projects** — Goals with deadlines (Launch website, Learn guitar, Plan vacation)
- **Areas** — Ongoing responsibilities (Health, Finance, Career, Family)
- **Resources** — Reference material (Book notes, recipes, how-tos, cheat sheets)
- **Archive** — Completed or inactive items

No manual filing. No decision fatigue. The AI reads your note and puts it where it belongs.

### Distill

The `/reorg_enrich` command adds AI-generated metadata to your notes — summaries, key takeaways, priority levels, and suggested tags. Your future self finds things faster.

### Express

Your organized knowledge feeds into action. The `/report_daily` aggregates your highest-priority items from both Joplin and Google Tasks into a single morning briefing. You always know what matters today.

---

## What You Can Do

### Brain Dump When You're Overwhelmed

Run `/braindump` and the bot becomes a GTD coach. It asks targeted questions to pull every open loop out of your head — that nagging errand, the email you keep putting off, the idea you had in the shower.

At the end, you get a clean summary note in Joplin and concrete tasks in Google Tasks. Your head is empty. Your system has everything.

### Never Lose a Reference Again

Paste a URL and the bot fetches the article, extracts the key content, detects if it's a recipe, generates a summary, and files it in the right folder with smart tags. Months later, you'll actually find it.

### Morning Priorities in 10 Seconds

The daily report pulls together your high-priority Joplin notes, upcoming Google Tasks, and pending items into one message. No app-hopping. No wondering what you forgot.

### Stoic Journaling

`/stoic morning` guides you through intention-setting. `/stoic evening` walks you through reflection. The bot saves your journal entries as structured notes — building a practice without friction.

### Reorganize Your Entire Knowledge Base

Already have hundreds of notes in Joplin? The `/reorg_init` command creates a PARA folder structure, and the AI classifies and migrates your existing notes into it. Years of accumulated notes, organized in minutes.

---

## Why This Combination Works

Most productivity tools solve *one* problem. A to-do app doesn't help you remember what you learned. A note-taking app doesn't tell you what to do next. You end up switching between apps, duplicating information, and losing context.

This bot is different:

- **One input** — Telegram messages, the same app you already use
- **Two systems** — GTD for actions, Second Brain for knowledge
- **Zero organizing** — AI handles folders, tags, and task extraction
- **Always available** — your phone is always with you; capture happens in the moment

The result: **you think less about your system and more about your life.**

---

## Getting Started

### What You Need

- A Telegram account
- [Joplin](https://joplinapp.org/) (free, open-source note-taking app)
- An AI provider API key (DeepSeek recommended — fast and affordable)
- Optionally: a Google account for Google Tasks integration

### Quick Setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) (one-time), then:

```bash
git clone <repository-url>
cd telegram-joplin
cp .env.example .env    # add your API keys
./setup.sh              # creates .venv via uv sync, installs dependencies
source .venv/bin/activate
python main.py          # bot is live
```

You can also run the bot without activating the venv: `uv run python main.py`.

Or with Docker:

```bash
cp .env.example .env    # add your API keys
docker-compose up -d
```

### Cloud Deployment (Fly.io)

The bot runs on Fly.io with **zero cost when idle** — the machine sleeps between messages and wakes in ~10 seconds when you text the bot. See [deployment guide](docs/for-users/README.md) for details.

### Google Tasks (Optional)

Enable Google Tasks integration to get automatic task extraction:

1. Create a Google Cloud project with the Tasks API enabled
2. Add OAuth credentials to your `.env`
3. Run `/authorize_google_tasks` in the bot

**Project sync** (optional): Map Joplin project folders to parent tasks in Google Tasks. Tasks created for a project appear as subtasks under the parent. Enable with `/tasks_toggle_project_sync`; see [Project Sync](docs/for-users/project-sync.md) for details.

---

## Documentation

| Audience | Guide |
|----------|-------|
| **Users** | [User Guide](docs/for-users/README.md) — setup, configuration, daily usage, [project sync](docs/for-users/project-sync.md) |
| **GTD + Second Brain** | [Complete Workflow Guide](docs/for-users/gtd-second-brain-workflow.md) — when to create a task vs a note, project walkthroughs, weekly reviews |
| **PARA Decisions** | [Where Things Go](docs/para-where-to-put.md) — Projects vs Areas vs Resources vs Archive |
| **Developers** | [Developer Guide](docs/for-developers/README.md) — architecture, codebase, contributing |
| **Business Analysts** | [BA Guide](docs/for-business-analyst/README.md) — features, roadmap, requirements |

---

## Built With

- **Python dependencies** — [uv](https://docs.astral.sh/uv/) with `pyproject.toml` + `uv.lock` (run `./setup.sh` or `uv sync --all-groups`)
- **Telegram Bot API** via [python-telegram-bot](https://python-telegram-bot.org/)
- **Joplin** via Web Clipper API — your notes stay local and private
- **Google Tasks API** — OAuth 2.0 integration
- **AI/LLM** — OpenAI, DeepSeek, or Ollama (local, no cloud needed)
- **Fly.io** — zero-cost serverless deployment

---

*"Your mind is for having ideas, not holding them."* — David Allen, Getting Things Done
