import subprocess
from logger import *


# def check_file(value):
#     """Проверка файла с результатом работы дбанковского терминала"""
#     logger.info("Proverka file")
#     pinpad_file = r"C:\sc552\p"
#     option = value
#     result = 0
#     if option == 1:
#         """Проверяем одобрение операции"""
#         file_result = 'ОДОБРЕНО'
#         try:
#             with open(pinpad_file, encoding='IBM866') as file:
#                 text = file.read()
#             if file_result in text:
#                 logger.info("Проверка файла успешно завершена")
#                 result = 1
#         except FileNotFoundError as not_found:
#             print('File not found:', not_found.filename)
#             logger.warning("Проверка файла завершилась с ошибкой")
#             #result = 0
#     elif option == 2:
#         """Выводим результат сверки итогов"""
#         try:
#             with open(pinpad_file, encoding='IBM866') as file:
#                 lines = file.readlines()[2:]
#             logger.info(lines)
#             logger.info("Сверка итогов успешно завершена")
#             result = 1
#         except FileNotFoundError as not_found:
#             print('File not found:', not_found.filename)
#             logger.info("File not found")
#             result = 0
#     print('Res= ', result)
#     return result


# def check_operation(value):
#     """Проверка результата работы функции check_file"""
#     res = check_file(value)
#     if res == 1:
#         logger.info("Операция работы с банковским терминалом успешно завершена")
#     else:
#         logger.info("Операция работы с банковским терминалом Error")
#     return res


# def oplata(sum):
#     sum += '00'
#     pinpad = 'C:\\sc552\\loadparm.exe'
#     pay_param = ' 1 ' + sum
#     pinpad_run = pinpad + pay_param
#     subprocess.call(pinpad_run)
#     check_file(1)

def oplata(sum):
    """Операуия оплаты по дбанковскому терминалу"""
    sum += '00'
    pinpad = 'C:\\sc552\\loadparm.exe'
    pay_param = ' 1 ' + sum
    pinpad_run = pinpad + pay_param
    subprocess.call(pinpad_run)
    """Проверка файла с результатом работы дбанковского терминала"""
    logger.info("Proverka file")
    pinpad_file = r"C:\sc552\p"
    """Проверяем одобрение операции"""
    file_result = 'ОДОБРЕНО'
    try:
        with open(pinpad_file, encoding='IBM866') as file:
            text = file.read()
        if file_result in text:
            logger.info("Проверка файла успешно завершена")
            result = 1
    except FileNotFoundError as not_found:
        print('File not found:', not_found.filename)
        logger.warning("Проверка файла завершилась с ошибкой")
        result = 0
    return result


def vozvrat(sum):
    """Операуия возврата по дбанковскому терминалу"""
    pinpad_file = r"C:\sc552\p"
    sum += '00'
    pinpad = 'C:\\sc552\\loadparm.exe'
    pay_param = ' 8 ' + sum
    pinpad_run = pinpad + pay_param
    subprocess.call(pinpad_run)
    """Проверка файла с результатом работы дбанковского терминала"""
    logger.info("Proverka file")
    """Проверяем одобрение операции"""
    file_result = 'ОДОБРЕНО'
    try:
        with open(pinpad_file, encoding='IBM866') as file:
            text = file.read()
        if file_result in text:
            logger.info("Проверка файла успешно завершена")
            result = 1
    except FileNotFoundError as not_found:
        print('File not found:', not_found.filename)
        logger.warning("Проверка файла завершилась с ошибкой")
        result = 0
    return result


def check_itog():
    """Сверка итогов работы дбанковского терминала"""
    logger.info("Proverka file")
    pinpad_file = r"C:\sc552\p"
    subprocess.call('C:\\sc552\\loadparm.exe 7')
    logger.debug('Check itog')
    """Выводим результат сверки итогов"""
    try:
        with open(pinpad_file, encoding='IBM866') as file:
            lines = file.readlines()[2:]
        logger.info(lines)
        logger.info("Сверка итогов успешно завершена")
        result = 1
    except FileNotFoundError as not_found:
        print('File not found:', not_found.filename)
        logger.info("File not found")
        result = 0
    return result


menu = int(input('Доступные операции: \n 1 - оплата, 2 - возврат, 3 - сверка итогов.\n Выберите операцию: '))
if menu == 1:
    sum = input('Введите сумму: ')
    if oplata(sum) == 1:
        print('Good')
    else:
        print('Err')

elif menu == 2:
    sum = input('Введите сумму: ')
    if vozvrat(sum) == 1:
        print('Good')
    else:
        print('Err')

elif menu == 3:
    if check_itog() == 1:
        print('Good')
    else:
        print('Err')