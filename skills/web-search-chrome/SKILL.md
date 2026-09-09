---
name: web-search-chrome
description: "Use when searching the web via local Chrome."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [web, search, browser, chrome, cloudflare, ublock]
---

# Web Search via Local Chrome (Multi-Engine)

Поиск в интернете через локальный портативный Chrome с uBlock Origin Lite. Три поисковика: Brave, DuckDuckGo, Яндекс. Разнообразие запросов + паузы для обхода Cloudflare и антибот-защиты.

## Запуск Chrome (обязательно перед поиском)

Chrome должен быть запущен с remote debugging, иначе browser_exec падает с `chrome-not-running`:

```bash
# путь: C:/Users/Administrator/Desktop/chrome-win/chrome.exe
# флаги:
chrome.exe --remote-debugging-port=9222 \
  --user-data-dir="C:/Users/Administrator/Desktop/chrome-win/profile-search" \
  --load-extension="C:/Users/Administrator/Desktop/chrome-win/extensions/ublock-lite"
```

Проверка: `curl -s http://127.0.0.1:9222/json/version` — должен вернуть JSON с Browser.

Если Chrome уже запущен без `--load-extension` — перезапустить (uBO Lite не подхватится на лету).

## URL шаблоны поисковиков

| Движок | Шаблон | Примечание |
|--------|--------|------------|
| Brave | `https://search.brave.com/search?q={query}` | Выдача рендерится JS; парсить `body.innerText` (селекторы a.snippet-title устарели) |
| DuckDuckGo | `https://duckduckgo.com/?q={query}` | Результаты в `article` / `[data-testid="result-title-a"]` |
| Яндекс | `https://yandex.com/search/?text={query}` | Почти всегда капча; лечится паузой 12 сек + перезагрузка |

## Протокол поиска

### 0. Языковая стратегия (по данным W3Techs, сентябрь 2026)

Доля контента в интернете по языкам:

| # | Язык | Доля | Роль |
|---|------|------|------|
| 1 | English | 49.5% | ОСНОВНОЙ |
| 2 | Spanish | 6.0% | ОСНОВНОЙ |
| 3 | German | 5.9% | fallback |
| 4 | Japanese | 4.9% | fallback |
| 5 | French | 4.5% | fallback |
| 6 | Portuguese | 4.1% | fallback |
| 7 | Russian | 3.4% | ОСНОВНОЙ |
| 8 | Italian | 2.8% | fallback |
| 9 | Dutch | 2.2% | fallback |
| 10 | Polish | 1.8% | fallback |

Три основных языка поиска: **русский, английский, испанский**. Каждый запрос гонять минимум на этих трёх (варианты A/B/C). Остальные 7 языков (de, ja, fr, pt, it, nl, pl) — только если на трёх основных ничего не нашлось.

Порядок fallback-перебора: de → fr → pt → it → nl → pl → ja (ja — сложный из-за иероглифов, в конце).

### 1. Разнообразие запросов (обязательно)

Для одного инфопоиска строить 2-3 варианта запроса и гонять по РАЗНЫМ движкам:

- вариант A: прямой запрос пользователя (основной язык темы)
- вариант B: перефразировка, синонимы (en)
- вариант C: перевод на другой основной язык (ru/es)

Пример для "DDR5 OC calculator":
- A: `DDR5 overclocking calculator` (Brave, en)
- B: `DDR5 OC timing calculator tool` (DuckDuckGo, en)
- C: `калькулятор разгона DDR5` (Яндекс, ru)
- если пусто: `calculadora overclocking DDR5` (Brave, es)
- если пусто: `DDR5 Übertaktungsrechner` (DDG, de)

Правила: не повторять одинаковый запрос на двух движках подряд; при пустых результатах менять формулировку, а не движок; язык — следующий в очереди после формулировки.

### 2. Паузы (обход Cloudflare / антибота)

- между запросами: минимум 2-4 сек (`time.sleep`)
- между движками: 5-8 сек
- при Cloudflare challenge (заголовок `Just a moment...`, `cf-chl-`, 403): подождать 10-15 сек и перезагрузить; не долбить повторными запросами
- максимум 3 попытки на один URL, потом сменить движок
- Яндекс SmartCaptcha: `time.sleep(12)` + `goto_url(текущий URL)` + `wait_for_load()` — проверено, пропускает (результаты приходят)

### 2a. Кириллица в browser_exec

browser_exec падает с `UnicodeDecodeError` если в коде есть кириллица. Запросы на русском предварительно кодировать percent-encode (urllib.parse.quote вне кода, или готовый %D0%...):
```python
q = '%D0%BA%D0%B0%D0%BB%D1%8C%D0%BA%D1%83%D0%BB%D1%8F%D1%82%D0%BE%D1%80'  # 'калькулятор'
goto_url('https://yandex.com/search/?text=' + q)
```

### 3. Извлечение результатов

DuckDuckGo (надёжный парсер):
```python
res = js('''(() => {
  const items = [...document.querySelectorAll('article, [data-testid="result"]')];
  return items.slice(0, 8).map(el => {
    const t = el.querySelector('[data-testid="result-title-a"], h2');
    const s = el.querySelector('[data-result="snippet"], .result__snippet');
    return {title: t ? t.innerText.trim() : '', snippet: s ? s.innerText.trim() : ''};
  }).filter(x => x.title);
})()''')
```

Brave: выдача рендерится JS, стабильных селекторов нет — использовать fallback `body.innerText` и искать URL/заголовки в тексте.

Яндекс: `li.serp-item` → `h2` + `div.TextContainer`; после капчи результаты в plain text.

Fallback-парсер (работает везде): `document.body.innerText.slice(0, 3000)` — взять начало текста страницы.

### 4. Обработка Cloudflare и блокировок

Признаки блокировки: заголовок страницы содержит "Just a moment" / "Attention Required" / капча; `body.innerText` короткий и без результатов; статус 403.

Действия по порядку:
1. `time.sleep(12)` + `goto_url(текущий URL)` + `wait_for_load()` — Cloudflare часто пропускает после паузы
2. Сменить движок (например Brave → Яндекс)
3. Сменить формулировку запроса
4. Если всё заблокировано — вернуть пользователю честный ответ, что поиск заблокирован, с примерами что пробовали

## Справочник операторов

Полные таблицы операторов для DDG, Brave, Яндекса и Google (проверено по официальным страницам справки) — в `references/search-operators.md`. Загружать при необходимости уточнить синтаксис.

## Проверка uBO Lite

Расширение должно быть включено (иначе сайты видят бота):
- service worker: `chrome-extension://ngfehifghhpedekeagoaigmegpdgdoon/js/background.js` в CDP `Target.getTargets`
- если его нет — перезапустить Chrome с `--load-extension` и включить developer mode на `chrome://extensions` (uBO Lite распакован, требует dev mode)

## Ограничения

- Яндекс может требовать капчу даже с паузами — не тратить более 2 попыток (SmartCaptcha на yandex.com, не путать с Cloudflare)
- DDG периодически рейтлимитит — при пустой выдаче переключиться на Brave
- Brave отдаёт контент в `body.innerText` — первые ~800 символов это AI-сводка по запросу, результаты ниже
- Кириллица в browser_exec — только percent-encode (см. 2a)
- Язык ja (японский) — кодировать percent-encode обязательно, иероглифы в коде не пройдут
- Не использовать для обхода логин-стен (это не задача скилла)
- Сессии browser_exec не разделяют cookies между собой — начинать поиск с `new_tab()`
