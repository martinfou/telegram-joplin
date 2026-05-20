# BMAD Sprint — Telegram Joplin Bot

> Sprint initial — 2026-05-20
> Martin Fournier — Product Owner

---

## 🎯 Objectif du Sprint

Bot Telegram qui combine GTD + Second Brain. L'utilisateur envoie un message,
l'IA décide si c'est une tâche (Google Tasks) ou une note (Joplin).

## 🌐 Questions de Scope (Bmad)

### Q1 — État actuel

- a) **Fonctionnel en production** (Fly.io) — on itère et améliore
- b) En développement — besoin de le finir
- c) Projet mort — besoin de le relancer

### Q2 — Priorité immédiate

- a) **Stabilité** — Tests, CI/CD, monitoring
- b) Features — Nouvelles capacités (habitudes, flashcards, etc.)
- c) Infrastructure — Config locale, Makefile, ports

### Q3 — Stack

- a) **Python/uv** (déjà en place)
- b) Migration vers autre chose

---

## 🎯 Décisions (répondues)

Pas de questions — on part sur ce qui existe. Le projet est fonctionnel en prod.

## 📋 Plan Initial

| # | Tâche | Effort |
|---|---|---|
| 1 | Créer `.env` avec les tokens (DeepSeek, Telegram, Joplin) | 10 min |
| 2 | Ajouter `make tg` au Makefile root (déjà fait) | ✅ |
| 3 | Vérifier que l'install et les tests passent | 30 min |
| 4 | Configurer une instance locale de Joplin Web Clipper | 15 min |

## 🔧 Bmad Agents

Les agents Bmad sont installés dans `.agents/` :
- `bmad-agent-pm` — Gestion de produit
- `bmad-agent-dev` — Développement
- `bmad-agent-analyst` — Analyse
- `bmad-agent-architect` — Architecture
- etc.
