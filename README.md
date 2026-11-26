# femboyfind

**femboyfind** — Python-библиотека и CLI для агрегированного поиска по сайтам
с контентом для взрослых. Требуется Python 3.9 или новее.

> **Только для совершеннолетних (18+).** CLI требует подтверждение возраста,
> запросы, связанные с несовершеннолетними, блокируются. Используйте источники
> только законно и соблюдайте условия их использования.

[Исходный код на GitHub](https://github.com/leekleek1337/femboyfind)

## Возможности

- Ищет сразу по нескольким сайтам и объединяет найденные результаты.
- Встроенные источники: Eporner, Pornhub, RedTube, xHamster, XVideos и XNXX.
- Поддерживает JSON API и публичные HTML-страницы поиска.
- Позволяет использовать собственный список провайдеров в `providers.json`.
- Выводит результаты в обычном или JSON-формате.

HTML-провайдеры читают доступные публичные страницы и не обходят авторизацию,
CAPTCHA или другие ограничения доступа. Изменения разметки сайтов могут
временно нарушить работу источника.

## Установка

Пакет пока не опубликован на PyPI. Установить текущую версию можно напрямую
из GitHub:

```bash
python -m pip install "git+https://github.com/leekleek1337/femboyfind.git"
```

Либо клонируйте репозиторий и установите проект локально:

```bash
git clone https://github.com/leekleek1337/femboyfind.git
cd femboyfind
python -m pip install .
```

Для разработки используйте editable-установку:

```bash
python -m pip install -e .
```

## Быстрый старт: командная строка

Поиск по встроенному списку сайтов:

```bash
femboyfind cosplay --i-am-18
```

По умолчанию к запросу добавляется `femboy`. Чтобы сохранить результаты в JSON:

```bash
femboyfind cosplay --json --i-am-18
```

Основные параметры:

| Параметр | Описание |
| --- | --- |
| `--providers PATH` | Путь к пользовательскому JSON-файлу провайдеров. Заменяет список по умолчанию |
| `--limit N` | Максимум результатов, по умолчанию `20` |
| `--page N` | Номер страницы, по умолчанию `1` |
| `--exclude WORD [WORD ...]` | Исключить результаты, содержащие слова в заголовке или тегах |
| `--json` | Вывести результаты как JSON |
| `--i-am-18` | Подтвердить, что вам не менее 18 лет |

Например, исключить результаты с указанными словами:

```bash
femboyfind cosplay --exclude amateur compilation --i-am-18
```

## Использование из Python

```python
from femboyfind import JsonApiProvider, SearchClient

provider = JsonApiProvider(
    name="example",
    url_template=(
        "https://api.example.com/search"
        "?q={query}&page={page}&limit={limit}"
    ),
    results_path="data.videos",
    fields={
        "title": "title",
        "url": "url",
        "thumbnail": "thumbnail",
        "duration": "duration",
    },
)

# По умолчанию библиотека добавляет к запросу слово "femboy".
client = SearchClient([provider])
for result in client.search("cosplay", limit=10):
    print(result.source, result.title, result.url)
```

Чтобы отключить добавление базового слова, задайте его пустым:

```python
client = SearchClient([provider], base_term="")
```

## Пользовательские провайдеры

Параметр `--providers` принимает путь к JSON-массиву. Для JSON API объект
провайдера задаёт шаблон URL, путь к списку результатов и пути к нужным полям:

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

В `url_template` поддерживаются `{query}`, `{page}` и `{limit}`. Пути в
`results_path` и `fields` разделяются точками; числовой сегмент выбирает
элемент списка.

Для HTML-поиска укажите `"type": "html"`, шаблон поисковой страницы и
регулярное выражение для путей ссылок на видео:

```json
[
  {
    "type": "html",
    "name": "example",
    "url_template": "https://example.com/search/{query}?page={page}",
    "video_url_pattern": "^/videos/"
  }
]
```

HTML-шаблон также поддерживает `{page_index}` — номер страницы с нуля — и
`{limit}`. Готовая конфигурация встроенных источников находится в
[`providers.json`](https://github.com/leekleek1337/femboyfind/blob/main/providers.json).

## Публикация на PyPI

В репозитории настроен GitHub Actions workflow:
[`publish.yml`](https://github.com/leekleek1337/femboyfind/blob/main/.github/workflows/publish.yml).
Он запускает тесты для Python 3.9 и 3.14 при push и pull request в `main`, а
также при GitHub Release. Публикация запускается автоматически при создании
опубликованного GitHub Release: workflow собирает пакет и отправляет его на
PyPI через Trusted Publishing. API-токен PyPI в GitHub Secrets не нужен.

### Однократная настройка Trusted Publishing

1. На PyPI откройте **Account settings → Publishing**. Добавьте **pending
   publisher** для нового проекта либо настройте Trusted Publisher в настройках
   уже созданного проекта `femboyfind`.
2. Укажите:
   - Owner: `leekleek1337`
   - Repository: `femboyfind`
   - Workflow filename: `publish.yml`
   - Environment name: `pypi`
3. В GitHub откройте **Settings → Environments** и создайте environment с именем
   `pypi`.
4. Убедитесь, что версия в `pyproject.toml` ещё не публиковалась. Создайте GitHub
   Release с тегом, соответствующим версии, например `v0.1.0`, и опубликуйте его.
5. Проверьте ход сборки и публикации во вкладке **Actions** репозитория.

Каждую новую версию нужно указать в `pyproject.toml` и опубликовать под новым
тегом/релизом. Версии, уже загруженные в PyPI, повторно загрузить нельзя.

Подробнее: [Trusted Publishing на PyPI](https://docs.pypi.org/trusted-publishers/using-a-publisher/).

## Тесты

Из корня репозитория:

```bash
python -m pip install -e .
python -m pip install pytest
python -m pytest
```

## Лицензия

MIT.
