---
name: stolle-concord-decorator
description: "Use when working with Stolle Concord can decorators."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [stolle, concord, decorator, cans, manuals, maintenance, printing]
---

# Stolle Concord Can Decorators — коллекция мануалов и знания

Рабочая база по декораторам банок Stolle (Concord 24/36 MRT-8, Rutherford, basecoaters). Пользователь работает на заводе (Пльзень, JBS-инструкции).

## Где лежат мануалы (Windows)

- `C:/Users/Administrator/Desktop/Stolle/` — основная коллекция PDF:
  - `Concord 24MRT8 Decorator.pdf` (208 стр, 1-Aug-19) — Installation, Operation & Maintenance. **Имеет текстовый слой** — извлекать pymupdf/fitz, OCR не нужен. Серия 24/36 идентична по конструкции, отличается числом мандрелей (24 vs 36).
  - `8cd6 Rutherford Decorator.pdf` (382 стр) и `STOLLE CMD Rutherford Decorator.pdf` (386 стр) — тоже с текстовым слоем.
  - `OCR_dro_results.txt`, `OCR_png_results.txt` — OCR чешских JBS-инструкций завода (Пльзень) + куски мануалов. OCR грязный: пробелы слипшиеся, латинские подмены. Полезен для поиска операций (ID-1702-10791 и др.).
  - `Deco/` — фото DRO-экранов. Прочие: Technical Updates (1107-1, 1411-1...), Infeed, Blanket Wheel Gearbox, Cupper, lnkjector, standun bodymaker.
- Сканы фото мануалов в `Desktop/Stolle/*.png` (большие, 4-30 МБ).

## Ключевые факты (проверено по мануалам)

### Мойка валов: температуры НИГДЕ нет

Stolle в мануалах НЕ задаёт температуру мытья красочных/лаковых валов. Процедуры:
- **Inker wash-up** (Rutherford, стр. ~269): wash-up kit, машина на 60 cpm, растворитель по рекомендации производителя краски, маслёнка. Fountain block моется в wash-up tank.
- **Varnish wash-up (Graco pump)** (стр. ~186): снять Graco-насос в 2-галлонное ведро растворителя, ролик на Idle, зазор 0.010" между gravure и applicator. ВАЖНО: не гонять gravure в контакте с applicator без лака/растворителя — сталь порвёт резину.
- Реальная температура мойки диктуется производителем резинового покрытия валов и краски, не Stolle. Горячая вода >60°C разрушает нитрил/EPDM. Общие ориентиры 40-50°C.

### Какие температуры реально есть в мануале Concord

- Охлаждающая вода инкеров: только расход 24 GPM (91 LPM), температуры нет.
- Static lube: 110-130°F (43-54°C).
- Рабочая среда машины: 40-120°F (4-49°C), влажность <70%.
- Температура краски/лака — для вязкости (Ford #4 cup), не для мойки.
- Чешские JBS: «Ohrev válců» — нагрев валов ПЕРЕД печатью (качество с первого оттиска), мытьё пластин — изопропиловый спирт, гравировального вала — ацетон.

## Поиск по мануалам — рабочий приём

```python
import pymupdf
for fname in ['Concord 24MRT8 Decorator.pdf', '8cd6 Rutherford Decorator.pdf', 'STOLLE CMD Rutherford Decorator.pdf']:
    doc = pymupdf.open('C:/Users/Administrator/Desktop/Stolle/' + fname)
    for i in range(doc.page_count):
        t = doc[i].get_text()
        if 'wash' in t.lower():
            print(fname, 'p', i+1)  # + контекст вокруг совпадения
```

Технические данные (вес, габариты, воздух/вакуум/вода) — глава 3 Technical Data (стр. ~17). Датчики и диапазоны — глава 5, таблица Sensor/Gauge (стр. ~283 OCR).

## Питфоллы

- Не путать «мытьё валов» с «can washer» (мойка банок) и «washing cans» — это про банки, не про валы.
- В OCR_png_results.txt намешаны Rutherford и Concord — проверять номер страницы/машины.
- Вопрос «температура мытья валов» — частый; ответ: в доках Stolle её нет, искать у производителя резины/краски.
