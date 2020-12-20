import csv
import requests
from bs4 import BeautifulSoup


def get_base_url():
    try:
        with open('url.txt', 'r') as file:
            base_url = file.readline()
    except FileNotFoundError:
        base_url = 'https://kinovod.cc/'
    return base_url


def get_film_data(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'lxml')
    details = soup.find(class_='details')
    return {
        'title': soup.find('h1').text,
        'url': url,
        'year': details.find_next('li').find('a').text,
        'country': details.find_all('li')[1].find('a').text,
        'genre': details.find_all('li')[2].find('a').text,
        'ratings': soup.find(class_='rating-votes').text.strip()
    }


if __name__ == '__main__':
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/' +
                  'avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)' +
                      'Chrome/86.0.4240.198 YaBrowser/20.11.3.179 Yowser/2.5 Safari/537.36'
    }

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
            print(f'Проверка адреса: {url}')
            req = requests.get(url, headers=headers, timeout=2)
            target_url = url
            print(f'Рабочий адрес: {url}')
            break
        except requests.exceptions.ConnectionError:
            continue

    # Запись рабочего адреса в файл, чтобы можно было начать поиск с этого адреса в следующий раз
    with open('url.txt', 'w') as f:
        f.write(target_url)
        print('Адрес записан в файл')

    # Список фильмов в лицензионном качестве
    target_url += 'films?video=license'
    page_suffix = '&page='

    # Получаем адреса страниц
    pages = []
    for i in range(1, 10):
        search_url = target_url if i == 1 else target_url + page_suffix + str(i)  # Пропускаем страницу с индексом 1
        pages.append(search_url)

    # Получаем ссылки на фильмы
    films_href = []
    print(f'Получаем ссылки на фильмы...')
    for url in pages:
        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'lxml')
        page_films = soup.find_all(class_='link')

        for film in page_films:
            films_href.append(get_base_url() + film.get('href')[1:])

    # Получаем данные фильмов
    films_data = []
    print(f'Получаем данные по каждому фильму..')
    for film_url in films_href:
        films_data.append(get_film_data(film_url))

    # Сохраняем данные в файл
    print('Сохраняем данные в файл')
    with open('results.csv', 'w', newline='') as file:
        csv_writer = csv.writer(file, delimiter=';')
        csv_writer.writerow(['Название', 'Ссылка', 'Год', 'Страна', 'Жанр', 'Рейтинг'])
        for film in sorted(films_data, key=lambda i: i['year'], reverse=True):
            csv_writer.writerow([
                film['title'],
                film['url'],
                film['year'],
                film['country'],
                film['genre'],
                film['ratings']
            ])

