---
name: firefox-librewoolf-tuning
description: "Tune Firefox/LibreWolf speed on Windows by editing user.js."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [firefox, librewoolf, betterfox, user.js, performance, gpu, webrender]
---

# Firefox / LibreWolf Performance Tuning (Windows)

Ускорение Firefox-семейства (LibreWolf) на Windows. Профиль пользователя — портативный, лежит НЕ в %APPDATA%, а в `C:/Users/Administrator/Desktop/MPRFL/` (папка на рабочем столе). Главный инструмент — `user.js` внутри профиля.

## Когда использовать

- Пользователь жалуется: «Chrome быстрый, а Firefox/LibreWolf тяжело открывает страницы»
- Нужно включить/настроить GPU-рендер, кэш, спекулятивную загрузку

## Золотое правило: править user.js, а НЕ about:config

LibreWolf (Betterfox) перечитывает `user.js` при каждом запуске и ПЕРЕЗАПИСЫВАЕТ им настройки. Любая правка в about:config или prefs.js исчезнет при рестарте. Поэтому:
1. Все изменения писать в `user.js`
2. Свои правки — отдельным блоком в конце файла (секция «MY OVERRIDES» у Betterfox), чтобы легко откатывалось
3. `user.js` значения побеждают `prefs.js` — не нужно удалять конфликтующие строки из prefs.js

## Диагностика: что искать в prefs.js (grep-паттерны)

```bash
grep -iE "gfx|webrender|layers|media.hardware|privacy.sanitize|cache.disk|network.dns|network.predictor|speculative|javascript.options.mem|preXulSkeletonUI" prefs.js
```

Типичные убийцы скорости (Betterfox ставит приватность выше скорости):
- `browser.cache.disk.enable = false` — каждая страница грузится с нуля при каждом визите
- `privacy.sanitize.pending` с `itemsToClear: ["cache", ...]` — кэш стирается при каждом закрытии браузера (включение disk cache без отключения этого бессмысленно)
- `network.dns.disablePrefetch = true`, `network.predictor.enabled = false`, `network.prefetch-next = false`, `network.http.speculative-parallel-limit = 0` — отключена вся спекулятивная сеть: каждая навигация ждёт полный DNS+TCP цикл
- `javascript.options.mem.high_water_mark = "30"` (дефолт 128) — GC срабатывает слишком часто, паузы на тяжёлых страницах
- `browser.startup.preXulSkeletonUI = false` — медленный старт окна

## Проверенные оверрайды (добавлять блоком в user.js)

```js
// === PERFORMANCE OVERRIDES ===
user_pref("browser.cache.disk.enable", true);
user_pref("browser.cache.disk.capacity", 1048576);      // 1 GB
user_pref("browser.cache.disk.smart_size.enabled", true);
user_pref("network.dns.disablePrefetch", false);
user_pref("network.predictor.enabled", true);
user_pref("network.predictor.enable-prefetch", true);
user_pref("network.prefetch-next", true);
user_pref("network.http.speculative-parallel-limit", 6);
user_pref("browser.urlbar.speculativeConnect.enabled", true);
user_pref("browser.places.speculativeConnect.enabled", true);
user_pref("browser.startup.preXulSkeletonUI", true);
user_pref("javascript.options.mem.high_water_mark", 128);
user_pref("privacy.sanitize.sanitizeOnShutdown", false);
user_pref("privacy.clearOnShutdown.cache", false);
user_pref("privacy.clearOnShutdown_v2.cache", false);
// Под 32+ ядра: больше контент-процессов (дефолт капает на 8)
user_pref("dom.ipc.processCount", 16);
// Реже писать сессию на диск, ленивое восстановление вкладок
user_pref("browser.sessionstore.interval", 60000);
user_pref("browser.sessionstore.restore_on_demand", true);
user_pref("browser.sessionstore.restore_tabs_lazily", true);
// Рендер текста и картинок
user_pref("gfx.font_rendering.directwrite.enabled", true);
user_pref("image.downscale-during-decode.enabled", true);
```

## GPU: НЕ форсить force-enabled флаги

Если в prefs.js кто-то вручную добавил `gfx.webrender.compositor.force-enabled = true`, `layers.gpu-process.force-enabled = true`, `media.hardware-video-decoding.force-enabled = true` — они ЛОМАЮТ fallback: при сбое драйвера Firefox зависает вместо перехода на софтверный рендер. На современном GPU (Intel Arc с актуальным драйвером) WebRender D3D11 включается автоматически. Перекрыть в user.js:
```js
user_pref("gfx.webrender.compositor.force-enabled", false);
user_pref("layers.gpu-process.force-enabled", false);
user_pref("gfx.canvas.accelerated.force-enabled", false);
user_pref("media.hardware-video-decoding.force-enabled", false);
user_pref("gfx.webgpu.force-enabled", false);
user_pref("gfx.webgpu.ignore-blocklist", false);
```
Достаточно `gfx.webrender.all = true` + `layers.gpu-process.enabled = true` (не force) из Betterfox — автоопределение само решит.

## Порядок действий

1. Прочитать `user.js` и `prefs.js` профиля (путь — папка профиля, НЕ стандартный %APPDATA%)
2. Продиагностировать по grep-паттернам выше
3. Добавить блок оверрайдов в КОНЕЦ user.js (после Betterfox-секций, в «MY OVERRIDES»)
4. Сказать пользователю ПОЛНОСТЬЮ закрыть браузер и запустить заново — user.js применяется при старте
5. Если браузер сейчас открыт — НЕ убивать процесс без спроса; правки применятся при следующем рестарте
6. Проверка: `about:support` → Graphics → `Compositing: WebRender (D3D11)`; `about:config` → `browser.cache.disk.enable` = true

## Pitfalls

- Первый запуск после включения кэша медленнее — кэш наполняется; это нормально, не откатывать
- `browser.cache.disk.capacity` бесполезна, пока `disk.enable = false` — проверять оба
- Включение disk cache без отключения sanitize-on-shutdown не даёт эффекта — кэш стирается при выходе
- «Device or resource busy» при mv папки профиля на Windows — cp + rm вместо mv
- Betterfox-файл начинается с комментария «изменения в about:config перезапишутся» — это буквально правда, не игнорировать
