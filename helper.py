import requests
from bs4 import BeautifulSoup
import json
from pprint import pprint
from datetime import datetime, date, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import itertools

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

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
    try:
        table_body = soup.find(
            "table", {"class": "views-table sticky-enabled cols-15"}).find("tbody")
        table_body = table_body.findAll("tr")
    except:
        return
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
    if not products == None:
        for product in products:
            if product['name'] not in products_json.keys():
                products_json[product['name']] = {}
            products_json[product['name']][product["date_data"][0]] = product["date_data"][1]

    with open("products.json", "w") as f:
        json.dump(products_json ,f)

def get_all_details():
    start_date = date(2020, 1, 1)
    end_date = date.today()
    for single_date in daterange(start_date, end_date):
        page_date = single_date.strftime("%Y-%m-%d")
        # print(page_date)
        link = "https://www.caat.it/it/listino/" + page_date
        products = get_page_details(link)
        add_products_json(products)

def get_dates():
    dates = []
    with open("products.json", "r") as f:
        products_json = json.load(f)
    for key, value in products_json.items():
        for d in value.keys():
            if d not in dates:
                dates.append(d)
    dates.sort()
    # print(dates)
    return dates


def make_matrix():
    ret_matrix = []
    with open("products.json", "r") as f:
        products_json = json.load(f)
    dates = get_dates()
    heading = ["Gruppo","Specie","Varieta","Calibro","Cat.","Presentazione","Marchio","Origine","Confezione","Unita Misura","Altre"]
    heading.extend(dates)
    ret_matrix.append(heading)
    for key, value in products_json.items():
        row = []
        row.extend(key.split(":"))
        dates_row = [""] * len(dates)
        for date_key, pre_value in value.items():
            index = dates.index(date_key)
            dates_row[index] = pre_value
        row.extend(dates_row)
        ret_matrix.append(row)
    return ret_matrix

def gsheet_load(array):
    scope = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
    ]
    file_name = 'client_key.json'
    creds = ServiceAccountCredentials.from_json_keyfile_name(file_name,scope)
    client = gspread.authorize(creds)
    sheet = client.open('CAAT.IT').sheet1
    sheet.clear()
    append_rows(sheet,array)
    print("MODIFIED")

def driver():
    get_all_details()
    matrix = make_matrix()
    gsheet_load(matrix)