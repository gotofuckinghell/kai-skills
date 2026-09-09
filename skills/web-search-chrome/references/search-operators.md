# Search Operators Reference

Проверено по официальной документации (сентябрь 2026).

## DuckDuckGo (duckduckgo.com/duckduckgo-help-pages/results/syntax)

| Оператор | Пример | Что делает |
|----------|--------|------------|
| `cats dogs` | `cats dogs` | Любой из слов (OR по умолчанию) |
| `"..."` | `"cats and dogs"` | Точная фраза |
| `~"..."` | `~"cats and dogs"` | Семантически похожие фразы (эксперим.) |
| `-` | `cats -dogs` | Исключить слово |
| `+` | `cats +dogs` | Обязательное слово |
| `filetype:` | `cats filetype:pdf` | pdf, doc(x), xls(x), ppt(x), html |
| `site:` | `dogs site:example.com` | Только с сайта |
| `-site:` | `cats -site:example.com` | Исключить сайт |
| `intitle:` | `intitle:dogs` | Слово в заголовке |
| `inurl:` | `inurl:cats` | Слово в URL |
| `\` | `\futurama` | Перейти сразу на первый результат |
| `!bang` | `!a blink182` | Поиск на другом сайте (!g !w !yt !amazon...) |
| `!safeon`/`!safeoff` | `cats !safeoff` | Безопасный поиск для одного запроса |

Параметры URL: `?q=запрос&kl=ru-ru` (регион), `&df=w` (период: d/w/m), `&ia=web` (вкладка).

## Brave Search (search.brave.com/help/operators)

| Оператор | Пример | Что делает |
|----------|--------|------------|
| `ext:` | `Honda GX120 ext:pdf` | Расширение файла |
| `filetype:` | `... filetype:pdf` | Тип файла |
| `inbody:` | `nvidia 1080 ti inbody:"founders edition"` | Слово в теле страницы |
| `intitle:` | `seo conference intitle:2023` | Слово в заголовке |
| `inpage:` | `oscars 2024 inpage:"best costume design"` | Слово в заголовке ИЛИ теле |
| `lang:`/`language:` | `visas lang:es` | Язык (ISO 639-1) |
| `loc:`/`location:` | `niagara falls loc:ca` | Страна (ISO 3166-1) |
| `site:` | `goggles site:brave.com` | Сайт (работают поддомены и частичные домены) |
| `+` | `gpu +freesync` | Обязательное слово |
| `-` | `office -microsoft` | Исключить слово |
| `"..."` | `harry potter "order of the phoenix"` | Точная фраза |
| `AND` | `visa loc:gb AND lang:en` | И |
| `OR` | `inpage:australia OR inpage:"new zealand"` | Или |
| `NOT` | `brave search NOT site:brave.com` | Не |

Уникально для Brave: `lang:`, `loc:`, `inbody:`, `inpage:`.

## Яндекс (yandex.com/support/search)

Слова и фразы (query-language/search-context):

| Оператор | Пример | Что делает |
|----------|--------|------------|
| `!` | `!mountain` | Слово в ТОЧНОЙ форме |
| `+` | `mountain +forest +river` | Обязательное слово |
| `"..."` | `"fell down stood up"` | Точная цитата |
| `"*"` в кавычках | `"fell down * up"` | Пропущенное слово (одна * = одно слово) |
| `\|` | `mountain \| river \| forest` | Любое из слов |
| `-` | `climb mountain -Elbrus` | Исключить слово — СТАВИТЬ В КОНЕЦ запроса |

Страницы и сайты (query-language/qlanguage):

| Оператор | Пример | Что делает |
|----------|--------|------------|
| `url:` | `temperature url:en.wikipedia.org/wiki/Climate_change` | Точный URL (можно `*` в конце) |
| `site:` | `search site:wikiquote.org` | Весь сайт + поддомены |
| `host:` | `warming host:www.wikipedia.org` | Конкретный хост |
| `rhost:` | `warming rhost:org.wikipedia.*` | Хост в обратном порядке, `*` = все поддомены |
| `domain:` | `search domain:com` | Домен верхнего уровня |

Дата, язык, файлы (query-language/search-operators):

| Оператор | Пример | Что делает |
|----------|--------|------------|
| `mime:` | `passport application mime:doc` | pdf, doc, xls, ppt, rtf, odt, ods, odp, odg, swf |
| `lang:` | `passeport lang:fr` | Язык (ISO 639-1: de, en, fr, ru...) |
| `date:` | `festival date:20231001` | Дата публикации |
| | `festival date:>20231001` | После даты (<, <=, >, >=) |
| | `festival date:20230101..20231001` | Диапазон |
| | `festival date:202310*` | Месяц (год обязателен) |
| | `festival date:2023*` | Год |

Нюансы Яндекса:
- Оператор с пробелом — заменить пробел на %20
- host:/url:/rhost: — указывать ОСНОВНОЙ адрес сайта (не www)
- Исключаемое слово с `-` — в конец запроса
- `-` перед числом читается как отрицательное число — брать в кавычки

## Google (классика, частично работает и в других системах)

`site:` `intitle:` `inurl:` `intext:` `filetype:` `"фраза"` `-слово` `OR` `*` (wildcard) `..` (диапазон: `camera $300..$500`) `related:site.com` `define:слово` `inanchor:` `allintitle:` `allinurl:` `cache:url` (не работает с 2024).

Параметры URL: `&tbs=qdr:w` (неделя), `&tbs=qdr:m` (месяц), `&num=50`, `&start=10` (пагинация), `&hl=ru` (интерфейс), `&lr=lang_ru` (язык результатов), `&gl=cz` (регион), `&safe=off`.
