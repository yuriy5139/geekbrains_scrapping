import requests
from bs4 import BeautifulSoup, element
import pandas as pd
import re

from pymongo import MongoClient
from random import randint

pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 500)


def parse_hh_page(vac_df, res):
    soup = BeautifulSoup(res.text)
    vacancies = soup.findAll("div", {"class": "vacancy-serp-item"})
    for vacancy in vacancies:
        compensation = vacancy.findAll("span", {"data-qa": "vacancy-serp__vacancy-compensation"})
        start_money = 0
        end_money = 0
        currency = ''

        if compensation:
            start_money, end_money, currency = comp_parser(''.join(compensation[0].contents))

        title = vacancy.findAll("a", {"data-qa": "vacancy-serp__vacancy-title"})
        employer = vacancy.findAll("a", {"data-qa": "vacancy-serp__vacancy-employer"})
        address = vacancy.findAll("div", {"data-qa": "vacancy-serp__vacancy-address"})
        link = vacancy.findAll("a", {"class": "bloko-link"})

        location = ''
        if len(address[0].contents) == 1:
            location = address[0].contents[0]
        elif len(address[0].contents) > 1:
            metro_stations = vacancy.findAll("span", {"class": "metro-station"})
            for station in metro_stations:
                for elem in station.contents:
                    if isinstance(elem, element.Tag):
                        continue
                    else:
                        location += ', метро ' + elem

        vac_df = vac_df.append({'title': ''.join(title[0].contents) if title else '',
                                'startmoney': start_money,
                                'endmoney': end_money,
                                'currency': currency,
                                'employer': ''.join(employer[0].contents) if employer else '',
                                'address': location,
                                'link': ''.join(link[0].attrs['href']) if link else '',
                                'source': "hh.ru"
                                }, ignore_index=True)
    return vac_df


def parse_hh(pages=1, vac_df=None):
    if not vac_df:
        vac_df = pd.DataFrame(
            columns=['title', 'startmoney', 'endmoney', 'currency', 'employer', 'address', 'link', 'source'])

    STARTREQ = 'https://hh.ru/search/vacancy?area=1&fromSearchLine=true&text=python+developer'
    headers = {"User-Agent": "curl/7.58.0", "Accept": "*/*"}
    res = requests.get(STARTREQ, headers=headers)
    vac_df = parse_hh_page(vac_df, res)

    if pages > 1:
        for cnt in range(1, pages):
            url = STARTREQ + '&page=' + str(cnt)
            res = requests.get(url, headers=headers)
            vac_df = parse_hh_page(vac_df, res)

    return vac_df


def comp_parser(compensation):
    currency = compensation.split(' ')[-1]

    sums = re.findall(r'(\d+)\s(\d+)', compensation)
    if len(sums) == 2:
        return int("".join(sums[0])), int("".join(sums[1])), currency

    sums = re.findall(r'\s*от\s*(\d+)\s*(\d+)', compensation)
    if sums:
        return int("".join(sums[0])), 0, currency

    sums = re.findall(r'\s*до\s*(\d+)\s*(\d+)', compensation)
    if sums:
        return 0, int("".join(sums[0])), currency

    return None


def add_new_only(vacancies, conn_url):
    client = MongoClient(conn_url)
    db = client.vacancies
    current_rec = pd.DataFrame(list(db.collection.find({})))
    df_new = vacancies[~(vacancies['link'] == current_rec['link'])]
    result = db.collection.insert_many(df_new.to_dict('records'))
    return result


def find_by_money(money, conn_url):
    client = MongoClient(conn_url)
    db = client.vacancies
    interested = pd.DataFrame(
        list(db.collection.find({"$or": [{"startmoney": {"$gte": money}}, {"endmoney": {"$gte": money}}]})))
    return interested


if __name__ == '__main__':
    # получим новые вакансии (2 страницы)
    # vacancies = parse_hh(pages=2)

    #Добавим только те, которые отсутствуют в БД на данный момент
    # add_new_only(vacancies, 'mongodb://mongo:password@localhost:27017/?authSource=admin')

    #Запросим вакансии с оплатой более 300К рублей
    df_res = find_by_money(300000, 'mongodb://mongo:password@localhost:27017/?authSource=admin')
    print(df_res)
