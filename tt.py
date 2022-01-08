import subprocess


def check_file(value):
    """Проверка файла с результатом работы дбанковского терминала"""
    pinpad_file = r"C:\sc552\p"
    option = value
    if option == 1:
        """Проверяем одобрение операции"""
        file_result = 'ОДОБРЕНО'
        try:
            with open(pinpad_file, encoding='IBM866') as file:
                text = file.read()
            if file_result in text:
                return 1
        except FileNotFoundError as not_found:
            print('File not found:', not_found.filename)
    elif option == 2:
        """Выводим результат сверки итогов"""
        try:
            with open(pinpad_file, encoding='IBM866') as file:
                lines = file.readlines()[2:]
            print(lines)
        except FileNotFoundError as not_found:
            print('File not found:', not_found.filename)


def check_operation(value):
    """Проверка результата работы функции check_file"""
    res = check_file(value)
    if res == 1:
        return("Success!")
    else:
        return("Error!")


menu = int(input('Доступные операции: \n 1 - оплата, 2 - возврат, 3 - сверка итогов.\n Выберите операцию: '))
if menu == 1:
    sum = input('Введите сумму: ')
    sum += '00'
    pinpad = 'C:\\sc552\\loadparm.exe'
    pay_param = ' 1 '+sum
    pinpad_run = pinpad+pay_param
    sberbank = subprocess.call(pinpad_run)
    res = check_file(1)
    print(check_operation(res))
elif menu == 2:
    sum = input('Введите сумму: ')
    sum += '00'
    pinpad = 'C:\\sc552\\loadparm.exe'
    pay_param = ' 8 ' + sum
    pinpad_run = pinpad + pay_param
    sberbank = subprocess.call(pinpad_run)
    res = check_file(1)
    print(check_operation(res))
elif menu == 3:
    sberbank = subprocess.call('C:\\sc552\\loadparm.exe 7')
    check_file(2)
