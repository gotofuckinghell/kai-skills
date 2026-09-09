---
name: firefox-librewolf-tuning
description: "Use when Firefox/LibreWolf is slow: user.js overrides."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [firefox, librewolf, betterfox, performance, gpu, webrender, cache, user.js]
---

# Firefox / LibreWolf Performance Tuning

Диагностика и ускорение Firefox-семейства (Firefox, LibreWolf, Betterfox-профили) когда страницы открываются тяжело, а Chrome с GPU-рендером летает.

## Главное правило: править user.js, а НЕ about:config

Betterfox/LibreWolf профили содержат `user.js`, который **перезаписывает about:config при каждом рестарте**. Правки в about:config пропадут. Править только `user.js`, в секции `MY OVERRIDES` (между `START: MY OVERRIDES` и `END: BETTERFOX`).

Профиль может лежать где угодно (напр. `Desktop/MPRFL`). Файлы: `user.js` (источник правок), `prefs.js` (текущее состояние, руками не трогать).

## Диагностика: что смотреть первым

```bash
# GPU-настройки и форс-флаги
# grep -iE "gfx|webrender|layers|hardware|accel|gpu" user.js prefs.js
# Очистка при shutdown (убивает кэш)
# grep -iE "sanitize|clearOnShutdown" prefs.js user.js
# Спекулятивная сеть (prefetch/predictor)
# grep -iE "prefetch|predictor|speculative" user.js
```

## 6 проверенных причин медленности + фиксы (все в MY OVERRIDES)

### 1. Дисковый кэш выключен (Betterfox DISK AVOIDANCE)
`browser.cache.disk.enable = false` — каждая страница грузится с нуля.
```js
user_pref("browser.cache.disk.enable", true);
user_pref("browser.cache.disk.capacity", 1048576);   // 1 GB
user_pref("browser.cache.disk.smart_size.enabled", true);
```

### 2. Кэш стирается при каждом закрытии (LibreWolf privacy)
`privacy.sanitize.pending` содержит `itemsToClear: ["cache", ...]` — кэш бесполезен, даже включённый.
```js
user_pref("privacy.sanitize.sanitizeOnShutdown", false);
user_pref("privacy.clearOnShutdown.cache", false);
user_pref("privacy.clearOnShutdown_v2.cache", false);
```

### 3. Спекулятивная сеть отключена (DNS prefetch, predictor, prefetch-next = 0)
Каждая навигация ждёт полный сетевой цикл.
```js
user_pref("network.dns.disablePrefetch", false);
user_pref("network.predictor.enabled", true);
user_pref("network.predictor.enable-prefetch", true);
user_pref("network.prefetch-next", true);
user_pref("network.http.speculative-parallel-limit", 6);
user_pref("browser.urlbar.speculativeConnect.enabled", true);
user_pref("browser.places.speculativeConnect.enabled", true);
```

### 4. JS GC water mark занижен (30 МБ вместо 128)
Сборщик мусора срабатывает слишком часто → паузы на тяжёлых страницах.
```js
user_pref("javascript.options.mem.high_water_mark", 128);
```

### 5. Скелетон-UI отключён → медленный старт окна
```js
user_pref("browser.startup.preXulSkeletonUI", true);
```

### 6. Форс-флаги GPU ломают fallback
`gfx.webrender.compositor.force-enabled`, `layers.gpu-process.force-enabled`, `gfx.canvas.accelerated.force-enabled`, `media.hardware-video-decoding.force-enabled`, `gfx.webgpu.force-enabled` — при сбое драйвера браузер зависает вместо перехода на софтверный рендер. На современном GPU (Intel Arc, NVIDIA, AMD) WebRender включится сам — форс не нужен.
```js
user_pref("gfx.webrender.compositor.force-enabled", false);
user_pref("layers.gpu-process.force-enabled", false);
user_pref("gfx.canvas.accelerated.force-enabled", false);
user_pref("media.hardware-video-decoding.force-enabled", false);
user_pref("gfx.webgpu.force-enabled", false);
user_pref("gfx.webgpu.ignore-blocklist", false);
```

## Второй слой: под железо (мощный CPU / NVMe)

После базовых 6 фиксов, если машина мощная (много ядер, SSD):

```js
user_pref("dom.ipc.processCount", 16);             // дефолт Firefox капает на min(8, ядра); на 32 ядрах поднять до 12-16
user_pref("browser.sessionstore.interval", 60000); // реже писать сессию на диск (дефолт 15с) — меньше I/O
user_pref("browser.sessionstore.restore_on_demand", true);
user_pref("browser.sessionstore.restore_tabs_lazily", true); // старт быстрее, вкладки грузятся по клику
user_pref("gfx.font_rendering.directwrite.enabled", true);   // текст через DirectWrite (Windows)
user_pref("image.downscale-during-decode.enabled", true);    // декодирование сразу в нужный размер
user_pref("browser.tabs.unloadOnLowMemory", true);           // выгрузка неактивных вкладок при нехватке RAM
user_pref("browser.sessionhistory.max_entries", 30);         // меньше памяти на историю вкладки
```

Проверять железо перед этим: `os.cpu_count()` (логические ядра), тип диска (NVMe vs HDD) — на HDD дисковый кэш 1 GB может быть медленнее, чем его отсутствие.

## SQLite-фрагментация (старые профили)

places.sqlite / cookies.sqlite со временем фрагментируются → медленный старт и поиск. VACUUM при ЗАКРЫТОМ браузере часто даёт заметный прирост. Требует явного согласия пользователя (браузер обычно открыт).

## Верификация результата

1. Полностью закрыть браузер (все окна), запустить заново — user.js применится.
2. `about:support` → Graphics: `Compositing: WebRender (D3D11)`, GPU #1 = реальная видеокарта, Decision log без красных ошибок.
3. `about:config` → `browser.cache.disk.enable` = true.
4. Первый запуск после правок медленнее (кэш наполняется) — это норма.

## Откат

Удалить блок из MY OVERRIDES — вернётся стоковый Betterfox. Оверрайды изолированы, ничего в теле Betterfox не менять.

## Ограничения

- Приватность: включение кэша и prefetch снижает приватность (это осознанный трейд-офф Betterfox). Сообщить пользователю, что оверрайды легко откатить.
- Не трогать prefs.js вручную — user.js перезапишет при рестарте.
- Драйвер GPU: если у пользователя старый/битый драйвер, форс-флаги могли быть единственным способом включить ускорение — после снятия форса проверить about:support.
