# PyMASL
## _Программа для учета посетителей и реализации услуг в детском развлекательном центре_

PyMASL это небольшая программа, позволяющая вести учет посетителей детского центра и производить реализацию услуг с использованием торгового оборудования.

## Реализованный функционал

- учет сведений о клиентах: внесение, изменение, поиск;
- продажи билетов: формирование заказов, сохранение заказов для оплаты в будущем периоде, “привязка” продажи к сопровождающему, применение различных видов скидок ( льготы многодетным и инвадидам, применение скидки с шагом 5%);
- соблюдение правил посещения детского центра при оформлении заказов;
- выполнение операций с торговым оборудованием: ведение денежных операций при помощи ККМ АТОЛ, работа с эквайринговым терминалом Сбербанка, генерация и печать входных билетов;
- ведение статистики продаж и посещений;
- формирование отчетности.

> Проект внедрен и дорабатывается исходя из пожеланий заказчика.


## Используемые технологии

PyMASL написан на Python и использует ряд проектов с открытым исходным кодом:
- В качестве СУБД используется [PostgreSQL](https://www.postgresql.org/).
- БД развернута в Docker контейнере, для этого используется [Docker](https://www.docker.com/) и [Docker Compose](https://docs.docker.com/compose/).  
- Для безопасного изменения состояния БД используется инструмент для управления миграциями [Alembic](https://alembic.sqlalchemy.org/).
- Для работы с БД используется ORM инструмент [SQLAlchemy](https://www.sqlalchemy.org/).
- Графический интерфейс создан при помощи [PySide6](https://pypi.org/project/PySide6/), предоставляющего доступ ко всему фреймворку Qt 6.0+. Интерфейс разработан в Qt Designer.
- Для запуска программы в ОС Windows проект конвертируется в исполняемый exe файл при помощи [Auto PY to EXE](https://pypi.org/project/auto-py-to-exe/) (графический интерфейс к PyInstaller).
- Для работы с эквайринговые терминалы PAX/Ingenico ипользуется утилита loadparm.exe.
- Для работы с онлайн-кассами АТОЛ FPrint-22ПТК используется драйвер контрольно-кассовой техники v.10 [дККТ10] (https://integration.atol.ru/api/).
- Для генерации форм различных документов используется библиотека [ReportLab](https://www.reportlab.com/).
- Для автоматической печати pdf документов используется [SumatraPDF](https://www.sumatrapdfreader.org/).

И, конечно же, PyMASL это open source проект, размещенный в [публичном репозитории](https://github.com/MarcusStill/PyMASL) на GitHub.

## Интерфейс.
При запуске проекта отображается форма идентификации.

![0](https://user-images.githubusercontent.com/69536339/182655887-3c1b2eda-a743-44c4-8ffe-9ea71f2bd82d.jpg)

После успешной аутентификации пользователя открывается главная форма приложения.

![1](https://user-images.githubusercontent.com/69536339/182656660-c582def5-0488-4cc1-ac39-1689b7712b65.jpg)
Она состоит из следующих вкладок: пометители, продажи, доп.услуги, статистика, касса.

#### Вкладка "клиенты".
На ней отображается список всех клиентов. Доступны следующие фильтры: фамилия и имя (например, фраза "ива алекс" отфильтрует всех клиентов фамилия которых начинается с "ива" и имя начинается с "алекс"), фамилия, номер телефона, статус "инвалид", статус "многодетный".
При нажатии на кнопку "добавить" открывается форма для внесения сведений о новом посетителе.

![7](https://user-images.githubusercontent.com/69536339/182657898-2e758b02-cbd7-4f13-860b-24a0a919c058.jpg)

Если требуется изменить имеющиеся данные, то надо дважды нажать на нужную строку, либо выделить ее и нажать кнопку "изменить".

#### Вкладка "продажи".
На ней отображаются сведения о всех оформленных продажах билетов. Доступны следующие фильтры: за текущий день, за 3 дня и за 7 дней.

![2](https://user-images.githubusercontent.com/69536339/182658705-e110741b-751b-4ba2-ac3d-5f311cd28768.jpg)

При нажатии на кнопку "новая" открывается форма для формирования новой продажи.

![8](https://user-images.githubusercontent.com/69536339/182658871-724e9350-7d16-45a2-ba68-e3b9f4053ed7.jpg)

Она разделена на несколько частей. Верхняя таблица используется для фильтрации клиентов по тем же фильтрам, как и на вкладке "посетители" (фамилия и имя, фамилия, номер телефона, статус "инвалид", статус "многодетный"). Кнопка "новый" позволяет внести в базу данных нового клиента, а кнопка "+" добавляет этого посетителя в продажу. Кнопка "изменить" открывает форму со сведениями о посетителе для их корректировки. В таблицу, расположенную в правой части формы продажи, выводится список посетителей, которые были вместе в одной продаже ранее. В таблицу, расположенную в нижней счасти формы, добавляются клиенты для формирования продажи. Для этого Нужно сделать двойной клик на нужном клиенте в верхней таблице.
На форме присутствует поле с выбором даты посещения, выпадающий список с выбором продолжительности посещения. Checkbox "продление в день многодетных" позволяет оформить дополнительную продажу для посетителей со статусом многодетный в первое воскресение месяца.

В зависимости от возраста посетители делятся на следующие группы:
- младше 5 лет получают бесплатный билет;
- от 5 до 14 лет получают детский билет;
- старше 14 лет получают взрослый билет.

Цена билета автоматически рассчитывается в зависимости от возрастной груммы и категории посетителя. Реализован следующий механизм рассчета:
- многодетным в будние дни предоставляется скидка 50%;
- в первое воскресение месяца многодетным предоставляется бесплатный билет на два часа;
- инвалидам предоставляется бесплатное посещение в любой день с одним сопровождающим.
Возможно применение скидки  с шагом в 5%. Каждая продажа "привязывается" ко взрослому посетителя. Если он не хочет посещать развлекательный центр - его можно исключить из продажи.

#### Вкладка "доп.услуги".
Предполагается реализация дополнительных услуг: дни рождения, дискотеки и т.д. 
> Примечание: данный функционал находится в стадии разработки.

#### Вкладка "статистика".
На ней формируются сведения о продажах за выбранный период. Формираются следующие показатели:
- количество проданных билетов в разрезе по времени посещения и категории посетителя;
- финансовые показатели с разбивкой по виду оплаты и рабочему месту.

![4](https://user-images.githubusercontent.com/69536339/182663990-5abcf272-a533-45a4-942f-30fc10c338a8.jpg)

Для получения сведений нужно выбрать временной диапазон и нажать на кнопку "сформировать". После этого можно сгенерировать отчет кассира и администратора.

![5](https://user-images.githubusercontent.com/69536339/182664347-2de36ef2-191f-4476-b599-b7b207358af1.jpg)

![6](https://user-images.githubusercontent.com/69536339/182665904-ddcece38-9dc6-4cb4-a6b6-a701c4d2c165.jpg)


#### Вкладка "касса".
На ней расположены кнопки для работы с банковским терминалом и кассовым аппаратом.

![9](https://user-images.githubusercontent.com/69536339/182664637-d298a77d-fc67-43e0-bbe7-fceec0eb4b8c.jpg)


## Установка
> Примечание: `--раздел находится` в разработке.
> 
Зависимости указаны в requirements.txt. Для работы в ОС Windows проект конвертируется в exe при помощи [Auto PY to EXE](https://pypi.org/project/auto-py-to-exe/) - GUI к PyInstaller.

Процесс преобразования..

В дополнительные файлы нужно добавить содержимое каталога Files/platforms. состав Для корректног озапуска требуются следующие dll




## Docker
> Примечание: `--раздел находится` в разработке.
> 

```sh
cd pymasl
docker build -t ...
```

This will create the PyMASL image and pull in the necessary dependencies.


```sh
docker run -d -p 8000:8080 --restart=always ...}
```

Verify the deployment by navigating to your server address in
your preferred browser.

```sh
127.0.0.1:8000
```

## Лицензия
> Примечание: `--раздел находится` в разработке.

**Free Software, Hell Yeah!**
