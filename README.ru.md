# SENAITE Registries
[English README](README.md)

Простое дополнение для управления реестрами в SENAITE LIMS.

## Что реализовано

- Верхнеуровневый контейнер “Registries” для всех реестров
- Реестр журналов (Journal Registry) с объектами Journal
- JSON API для пакетного импорта
- Endpoint поиска пользователей для виджетов и импорта

## Быстрый старт

### Установка
- Добавьте `senaite.registries` в buildout (eggs) и выполните buildout
- Установите через Site Setup → Add-ons

### Использование
- Перейдите: Registries → Journals
- Добавляйте объекты Journal через стандартное меню “Add”
- Изменяйте состояние и редактируйте журналы через стандартное меню

## Запуск через Docker

См. пример `docker/compose.yml` для запуска SENAITE с этим дополнением.

## Реестр журналов

### Поля
- Title (обязательное)
- Description (необязательное)
- Number (1..100, обязательно)
- Start / End Dates
- Responsible
- Storage:
  - Active
  - Pre-archive
  - Archive
- Attachment (необязательное)

## Жизненный цикл Journal

### Состояния
- New: создан
- Active: в использовании
- Pre-archive: завершён, ожидает архивирования
- Archived: финальное состояние

### Действия
- Start Using: переводит New → Active
- End Using: переводит Active → Pre-archive
- Archive: переводит Pre-archive → Archived
- Unarchive: переводит Archived → Pre-archive

### Полезное
- Start date автоматически устанавливается при “Start Using” (если не задана)
- End date автоматически устанавливается при “End Using” (если не задана)

## Импорт журналов

- POST `/senaite_registries/journals/journal_import_api`
- Для пробного прогона: `?dry_run=true`

Минимальный пример:
```json
[
  {
    "title": "Batch Register 1",
    "number": 1,
    "start_date": "2025-01-01",
    "responsible": "labmanager",
    "storage_active": "Cold Room A"
  }
]
```

Примечания
- Импорт ищет ответственного среди пользователей по ID или имени
- Места хранения ищутся по UID, пути, id или названию
- Ответ включает статус по импорту каждого элемента и ссылки на созданные объекты

## Роли и права

| Permission                 | LabClerk | LabManager | Manager |
|---------------------------|:--------:|:----------:|:-------:|
| Manage Registries         |          |     X      |    X    |
| Add Journal               |    X     |     X      |    X    |
| Edit “Responsible” field  |          |     X      |    X    |
| Start Using / End Using   |    X     |     X      |    X    |
| Archive                   |          |     X      |    X    |
| Unarchive                 |          |            |    X    |

## Планы

- Другие типы реестров помимо Journals
- Унифицированный импорт/экспорт для всех реестров

## Совместимость

- Требуется SENAITE 2.6+

## Лицензия

- см. LICENSE
