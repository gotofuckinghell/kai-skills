---
name: skill-registry-lookup
description: "Use when fetching full skill texts from skill registries."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, clawhub, skills-sh, lobehub, github, registry]
---

# Skill Registry Lookup (полные тексты скиллов из реестров)

Как получить ПОЛНЫЙ текст SKILL.md из реестров скиллов, когда `hermes skills inspect <id>` показывает только превью (~50 строк) и `--json` не поддерживается.

## ClawHub API (полный текст)

```python
import urllib.request, json
req = urllib.request.Request(f'https://clawhub.com/api/v1/skills/{slug}', headers={'User-Agent':'Mozilla/5.0'})
d = json.loads(urllib.request.urlopen(req, timeout=15).read())
s = d.get('skill', d)
text = s['description']   # ПОЛНЫЙ SKILL.md, а не превью
```

- 404 → slug не существует; 409 Conflict → slug неоднозначен (несколько скиллов с этим именем) — взять точное имя из `hermes skills search`
- Поля: slug, displayName, summary, description (полный текст!), topics, tags, stats
- Работает для большинства clawhub-скиллов; lobehub-агенты — см. ниже

## skills.sh → GitHub напрямую

Скиллы skills.sh индексируются из GitHub-репозиториев. Идентификатор вида `skills-sh/<owner>/<repo>/<skill>`:

```python
# 1. Сначала структура репозитория через GitHub contents API (БЕЗ токена)
req = urllib.request.Request(f'https://api.github.com/repos/{owner}/{repo}/contents/', headers={'User-Agent':'Mozilla/5.0'})
items = json.loads(urllib.request.urlopen(req, timeout=20).read())
# 2. Потом raw по найденному пути
url = f'https://raw.githubusercontent.com/{owner}/{repo}/main/skills/{skill}/SKILL.md'
```

- **НЕ угадывать пути вслепую** — сначала contents API, потом raw (угадывание сжигает токены на 404)
- GitHub search/code API требует токен (401) — contents API работает без аутентификации
- Справочные файлы скилла тоже качаются: `references/*.md` из той же директории

## LobeHub: агенты ≠ скиллы

- `lobehub/business-email` в хабе — это **агент** (system prompt), а не скилл с командами
- Агенты: `lobehub/lobe-chat-agents` → `src/<name>.zh-CN.json`, промпт в `config.systemRole`, мета в `meta`
- Репозиторий `lobehub/skills` (`lobehub/<name>/skill.md`) — CLI-скиллы LobeHub Cloud, часто НЕ то, что обещает заголовок в хабе
- **Заголовки в хабе могут обманывать: lobehub/business-email вёл на LobeHub CLI, а не на бизнес-почту. Всегда проверять фактическое содержимое!**

## Проверенные идентификаторы (email-скиллы, сентябрь 2026)

| Идентификатор | Источник | Что это |
|---|---|---|
| `professional-email-writer` | ClawHub | Формальный/полуформальный/дружеский тон, 6 типов писем |
| `email-writer-assistant` | ClawHub | Универсальная структура + сценарии тона |
| `ai-email-assistant` | ClawHub | Спам-аудит, CAN-SPAM/GDPR/CASL (нужен EVOLINK_API_KEY) |
| `skills-sh/coreyhaines31/marketingskills/cold-email` | GitHub | Холодные продажи B2B + 5 справочников (benchmarks, follow-up-sequences, frameworks, personalization, subject-lines) |
| `lobehub/business-email` (агент) | lobe-chat-agents | Двуязычная переписка EN/中文 (systemRole) |

## Рабочий процесс поиска скилла

1. `hermes skills search "<тема>"` → список с идентификаторами
2. `hermes skills inspect <id>` → превью для оценки
3. Для полного текста: ClawHub API / GitHub contents+raw (выше)
4. Скачать в файл, показать пользователю, предложить установку `hermes skills install <id>`
5. Если заголовок и содержимое расходятся — сообщить об этом пользователю, найти настоящий исходник
