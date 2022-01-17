import requests
from pymongo import MongoClient
from lxml import html
import re

def get_news(url):
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
    response = requests.get(url, headers=header)
    dom = html.fromstring(response.text)
    items = dom.xpath("//div[@class='last24']//a[contains(@class,'card-mini _compact')]")
    news = []
    for item in items:
        article = {}
        article['text'] = item.xpath(".//span[@class='card-mini__title']/text()")[0]
        article['link'] = item.xpath("./@href")[0]
        article['date'] = date_parser(article['link'])
        article['source'] = 'lenta.ru'
        news.append(article)
    return news

def date_parser(link):
    date = re.findall(r'((\d\d\d\d)\/(\d\d)\/(\d\d))', link)
    if date:
        return date[0][1] + '-' + date[0][2] + '-' + date[0][3]
    else:
        date = re.findall(r'((\d\d)-(\d\d)-(\d\d\d\d))', link)
        return date[0][3] + '-' + date[0][2] + '-' + date[0][1]


if __name__ == "__main__":
    news = get_news('https://lenta.ru/')
    client = MongoClient('mongodb://localhost:27017/')
    db = client.news
    result = db.news.insert_many(news)
