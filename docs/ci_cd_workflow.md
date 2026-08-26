# CI/CD Workflow Setup

В проекте используется GitHub Actions для непрерывной интеграции.
Файл конфигурации уже создан и находится по пути: `.github/workflows/ci.yml`.

## Правила работы с ветками

В проекте используется 2 основные ветки:
1. **`dev`** - ветка разработки. Сюда отправляются все новые наработки и изменения.
2. **`master`** - основная (стабильная) ветка.

## Как работает CI (GitHub Actions)

1. При любом `git push` в ветку `dev`, GitHub Actions автоматически запускает тесты (из каталога `tests/`).
2. При создании Pull Request из ветки `dev` в `master` тесты также будут запущены автоматически.
3. Вы не сможете слить `dev` в `master`, если тесты не пройдут (при условии настройки Branch Protection).

## Настройка Branch Protection (Защита ветки master)

Чтобы запретить слияние кода с ошибками в `master`, необходимо настроить правила в самом GitHub:

1. Откройте ваш репозиторий на сайте GitHub.
2. Перейдите во вкладку **Settings** (Настройки).
3. В левом меню выберите **Branches** (в разделе Code and automation).
4. Нажмите кнопку **Add branch ruleset** (или Add branch protection rule, если интерфейс старый).
5. **Имя правила (Branch name pattern):** введите `master`.
6. Включите галочку **Require a pull request before merging**.
7. Включите галочку **Require status checks to pass before merging**.
8. В появившемся поиске статусов (Search for status checks) найдите и добавьте задачу тестирования (она называется `test` — так назван job в файле `ci.yml`).
9. Нажмите **Create** (или Save changes).

Теперь никто (даже администратор, если стоит галочка *Do not allow bypassing the above settings*) не сможет сделать merge в `master`, пока галочка теста от GitHub Actions не станет зеленой.