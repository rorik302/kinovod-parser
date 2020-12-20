import requests


def get_base_url():
    try:
        with open('url.txt', 'r') as file:
            base_url = file.readline()
    except FileNotFoundError:
        base_url = 'https://kinovod.cc/'
    return base_url


if __name__ == '__main__':
    start_url = get_base_url()

    # Берем числа из адреса
    nums = ''.join([i for i in start_url if i.isdigit()])

    # Убираем числа из адреса
    root_url_split = start_url.replace(nums, '').split('.')

    # Рабочий адрес
    target_url = ''

    # Счетчик итераций
    loop_count = 0

    # Поиск рабочего адреса
    while not target_url and loop_count <= 1000:
        suffix = int(nums) + loop_count if nums else loop_count
        loop_count += 1
        url = root_url_split[0] + str(suffix) + '.' + root_url_split[1]
        try:
            req = requests.get(url, timeout=2)
            target_url = url
            print(f'Рабочий адрес: {url}')
        except requests.exceptions.ConnectionError:
            continue

    # Запись рабочего адреса в файл, чтобы можно было начать поиск с этого адреса в следующий раз
    with open('url.txt', 'w') as f:
        f.write(target_url)
