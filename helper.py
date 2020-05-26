import requests
from bs4 import BeautifulSoup
import json
from pprint import pprint
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import itertools


def getSoup(link):
    req = requests.get(link)
    html = req.content
    soup = BeautifulSoup(html, "html.parser")
    return soup


def append_rows(self, values, value_input_option='RAW'):
    params = {
        'valueInputOption': value_input_option
    }
    body = {
        'majorDimension': 'ROWS',
        'values': values
    }
    return self.spreadsheet.values_append(self.title, params, body)


def get_page_details(link):
    products = []
    soup = getSoup(link)
    table_body = soup.find(
        "table", {"class": "views-table sticky-enabled cols-15"}).find("tbody")
    table_body = table_body.findAll("tr")
    for product in table_body:
        detail = {}
        detail["date_data"] = ['','']
        detail["date_data"][0] = link.split('/')[-1]
        detail["date_data"][1] = product.find("td", {"data-title": "P. Pre"}).text.strip().replace(",", ".")
        gruppo = product.find("td", {"data-title": "Gruppo"}).text.strip()
        specie = product.find("td", {"data-title": "Specie"}).text.strip()
        varieta = product.find("td", {"data-title": "Varietà"}).text.strip()
        calibro = product.find("td", {"data-title": "Calibro"}).text.strip()
        cat = product.find("td", {"data-title": "Cat."}).text.strip()
        presentazione = product.find("td", {"data-title": "Presentazione"}).text.strip()
        marchio = product.find("td", {"data-title": "Marchio"}).text.strip()
        origine = product.find("td", {"data-title": "Origine"}).text.strip()
        confezione = product.find("td", {"data-title": "Confezione"}).text.strip()
        unita_misura = product.find("td", {"data-title": "Unita misura"}).text.strip()
        altre = product.find("td", {"data-title": "Altre"}).text.strip()
        detail["name"] = "{gruppo}:{specie}:{varieta}:{calibro}:{cat}:{presentazione}:{marchio}:{origine}:{confezione}:{unita_misura}:{altre}".format(
            gruppo=gruppo, specie=specie, varieta=varieta, calibro=calibro, cat=cat, presentazione=presentazione, marchio=marchio, origine=origine, confezione=confezione, unita_misura=unita_misura, altre=altre)
        # detail["p_pre"] = product.find("td", {"data-title": "P. Pre"}).text.strip().replace(",", ".")
        products.append(detail)
        # print(detail)
    return products


def add_products_json(products):
    with open("products.json", "r") as f:
        products_json = json.load(f)

    for product in products:
        if product['name'] not in products_json.keys():
            products_json[product['name']] = {}
        products_json[product['name']][product["date_data"][0]] = product["date_data"][1]
    with open("products.json", "w") as f:
        json.dump(products_json ,f)

add_products_json(get_page_details("https://www.caat.it/it/listino/2020-04-01"))
