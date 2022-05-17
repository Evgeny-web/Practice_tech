from bs4 import BeautifulSoup
import requests as req
import csv

URL = "https://gzt.ru/news/sport/"
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
    'accept': '*/*'}

HOST = "https://gzt.ru"
FILE = 'News.csv'


def get_html(url, params=None):
    r = req.get(url, headers=HEADERS, params=params)
    return r


def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    page = soup.find_all('font', class_='text')
    page1 = page[-1].find_all('a')
    pagination = page1[-2].get('href')
    if pagination:
        try:
            return int(pagination[-2:])
        except Exception:
            return int(pagination[-1])
    else:
        return 1


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_="news-item")

    news = []
    for item in items:
        # создаем переменную и присваиваем ей ссылку новости
        link_news = HOST + item.find('a', class_="title").get('href')

        # получаем код страницы и парсим текст новости
        link = get_html(link_news)
        soup_news = BeautifulSoup(link.text, 'html.parser')
        # возможно 2 варианта тега div, поэтому проверяем через условие
        text_page = soup_news.find('div', class_='detail')
        if text_page:
            text = text_page.get_text(strip=True)
        else:
            text = soup_news.find('div', class_='hidden').get_text(strip=True)
        #print(test1)

        news.append({
            'title': item.find('a', class_="title").get_text(strip=True),
            'date': item.find('div', class_='news-date-time').get_text(),
            'link': link_news,
            'text': text,
            'topic': 'Спорт'
        })
    return news


def save_file(items, path):
    with open(path, 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Title', 'Дата', 'Ссылка', 'Text', 'Topic'])
        for item in items:
            writer.writerow([item['title'], item['date'], item['link'], item['text'], item['topic']])


def parse():
    html = get_html(URL)
    if html.status_code == 200:
        news = []
        pages_count = get_pages_count(html.text)
        for page in range(1, pages_count + 1):
            print(f"парсим страницу {page} из {pages_count}...")
            html = get_html(URL, params={'PAGEN_1': page})
            news.extend(get_content(html.text))
        save_file(news, FILE)
        print(f"Получено {len(news)} новостей")
    else:
        print("Сайт недоступен")


parse()
