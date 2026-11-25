# femboyfind

**femboyfind** — Python-библиотека и CLI для агрегированного поиска по сайтам
с контентом для взрослых. Требуется Python 3.9 или новее.

> **Только для совершеннолетних (18+).** Перед поиском CLI просит подтвердить
> возраст. Запросы, указывающие на несовершеннолетних, блокируются. Используйте
> источники только законно и соблюдайте их правила и условия использования.

## Возможности

- Поиск по нескольким источникам с объединением и удалением дубликатов.
- Встроенный список из шести сайтов: Eporner, Pornhub, RedTube, xHamster,
  XVideos и XNXX.
- Поддержка JSON API и публичных HTML-страниц поиска.
- Настраиваемый список источников в `providers.json`; без `--providers`
  используется конфигурация, включённая в пакет.
- Вывод в обычном или JSON-формате.

HTML-провайдеры читают доступные публичные страницы и не обходят авторизацию,
CAPTCHA или другие ограничения доступа. Изменения в разметке сайта могут
временно нарушить такой источник.

## Установка

Установка опубликованного пакета с PyPI:

```bash
python -m pip install femboyfind
```

Для разработки из локальной копии репозитория:

```bash
python -m pip install -e .
```

## CLI

Запустить поиск с встроенными источниками:

```bash
femboyfind cosplay --i-am-18
```

Основные параметры:

| Параметр | Назначение |
| --- | --- |
| `--providers PATH` | Использовать свой файл конфигурации вместо встроенного списка |
| `--limit N` | Максимум результатов (по умолчанию `20`) |
| `--page N` | Номер страницы (по умолчанию `1`) |
| `--exclude WORD [...]` | Исключить результаты по словам в заголовке или тегах |
| `--json` | Вывести результаты в JSON |
| `--i-am-18` | Подтвердить, что пользователю не менее 18 лет |

Пример с собственной конфигурацией:

```bash
femboyfind cosplay --providers providers.json --i-am-18
```

## Python API

```python
from femboyfind import JsonApiProvider, SearchClient

provider = JsonApiProvider(
    name="example",
    url_template="https://api.example.com/search?q={query}&page={page}&limit={limit}",
    results_path="data.videos",
    fields={
        "title": "title",
        "url": "url",
        "thumbnail": "thumbnail",
        "duration": "duration",
    },
)

client = SearchClient([provider])
for result in client.search("cosplay", limit=10):
    print(result.title, result.url)
```

## Конфигурация источников

`providers.json` — JSON-массив. Для API укажите шаблон URL, путь к списку
результатов и соответствие полей:

```json
[
  {
    "name": "example",
    "url_template": "https://api.example.com/search?q={query}&page={page}&limit={limit}",
    "results_path": "data.videos",
    "fields": {
      "title": "title",
      "url": "url",
      "thumbnail": "thumbnail",
      "duration": "duration"
    }
  }
]
```

В `url_template` доступны `{query}`, `{page}` и `{limit}`. `results_path` и
значения `fields` задаются путями через точку; числовой сегмент выбирает элемент
списка. Для HTML-поиска укажите тип, URL и регулярное выражение для ссылок на
видео:

```json
{
  "type": "html",
  "name": "example",
  "url_template": "https://example.com/search/{query}?page={page}",
  "video_url_pattern": "^/videos/"
}
```

Для HTML-провайдера также доступны `{page_index}` (нумерация с нуля) и
`{limit}`. Полная конфигурация с готовыми сайтами находится в файле
`providers.json` репозитория.

## Разработка и тесты

Из корня репозитория:

```bash
python -m pip install -e .
python -m pip install pytest
python -m pytest
```

## Лицензия

MIT. См. [`pyproject.toml`](./pyproject.toml).
