import requests
from bs4 import BeautifulSoup
import csv
from pydantic import BaseModel
from typing import Iterator

base_url: str = "https://www.metalmarket.eu"


# TODO: Error handling
def get_pages() -> int:  # fuction for get all pages from website
    response = requests.get(f"{base_url}/en/menu/gold-coins-850.html")
    
    if response.status_code != 200:
        print(f"Error: Code status {response.status_code}")
        return 0
    
    soup = BeautifulSoup(response.content, "html.parser")
    pagination = soup.find("ul", {"class": "pagination"})
    return int(pagination.find_all("li")[-2].text)


def process_page(url: str) -> dict:  # function for getting all coins
    response = requests.get(url)
    print(response)
    soup = BeautifulSoup(response.content, "html.parser")
    page_coins = soup.find_all("div", {"class": "product"})

    for coin_html in page_coins:
        coin = coin_html.find("a", href=True)
        if coin is not None:
            get_details(coin["href"])


class BaseParams(BaseModel):
    series: str
    type: str
    alloy: str
    weight: str
    diameter: str
    denomination: str
    edge: str
    producer: str


class Product:
    products = []

    def __init__(self, params: BaseParams) -> str:
        self._series: str = params.series
        self._type: str = params.type
        self._alloy: str = params.alloy
        self._weight: str = params.weight
        self._diameter: str = params.diameter
        self._denomination: str = params.denomination
        self._edge: str = params.edge
        self._producer: str = params.producer

        self.__class__.products.append(self)

    def __iter__(self) -> Iterator[str]:
        return iter(
            [
                self._series,
                self._type,
                self._alloy,
                self._weight,
                self._diameter,
                self._denomination,
                self._edge,
                self._producer,
            ]
        )

    @classmethod
    def save_to_csv(cls, filename: str = "out.csv", delimiter: str = ";") -> None:
        columns = BaseParams.__dict__["__annotations__"].keys()

        with open("scrapper", "w", encoding="utf-8") as csv_file:
            csv_file.write(f"{delimiter}".join([c for c in columns]) + "\n")

            for instance in cls.products:
                csv_file.write(f"{delimiter}".join([i for i in instance]) + "\n")


def get_details(url: str) -> dict:
    response = requests.get(f"{base_url}{url}")
    soup = BeautifulSoup(response.content, "html.parser")
    params = soup.find_all("div", {"class": "dictionary__param"})
    main_dict = {}
    for param in params:
        key = param.find("span", {"class": "dictionary__name_txt"})
        value = param.find("span", {"class": "dictionary__value_txt"})
        if key is None or value is None:
            continue
        main_dict[key.text.lower()] = value.text

    Product.products.append(main_dict)


Product.save_to_csv()

if __name__ == "__main__":
    for page in range(0, get_pages()):
        url: str = f"{base_url}/en/menu/gold-coins-850.html?counter={page}"
        process_page(url)

        break
