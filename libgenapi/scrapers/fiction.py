from datetime import time
import math
from random import random
import re
from typing import List
from lxml import html

import requests
from .helpers.lxml_helpers import get_all_text_in_element

from lxml.etree import _Element


class FictionBook:
    author: str | None
    series: str | None
    title: str
    language: str | None
    format: str | None
    size: str | None
    mirrors: List[str]

    def __init__(self):
        self.mirrors = []


class FictionScraper:
    __columns = [
        "author",
        "series",
        "title",
        "language",
        "format_and_size",
        "mirrors",
    ]

    def __init__(self, url):
        self.url = url

    def __get_format(self, text: str) -> str:
        return text.split("/")[0].strip()

    def __get_size(self, text: str) -> str:
        return text.split("/")[1].strip().replace("\xa0", " ")

    def __get_mirror(self, element: _Element) -> str:
        return str(element.xpath("a/@href")[0]).replace("../", self.url + "/")

    def __get_mirrors(self, element: _Element) -> List[str]:
        return [self.__get_mirror(e) for e in element.xpath("*/li")]

    def __get_search_results_table_rows(self, element: _Element) -> _Element:
        return element.xpath("//body/table/tbody/tr")

    def __parse_column(
        self, book: FictionBook, column: str, document: _Element
    ) -> None:
        text = get_all_text_in_element(document)
        if column == "format_and_size":
            book.format = self.__get_format(text)
            book.size = self.__get_size(text)
        elif column == "mirrors":
            book.mirrors = self.__get_mirrors(document)
        else:
            setattr(book, column, text)

    def __parse(self, doc: _Element) -> List[FictionBook]:
        parse_result = []

        resultRow: _Element
        for resultRow in self.__get_search_results_table_rows(doc):
            book = FictionBook()

            col: _Element
            for i, col in enumerate(resultRow.xpath("td[position()<last()]")):
                if i > (len(self.__columns) - 1):
                    break
                self.__parse_column(book, self.__columns[i], col)
            parse_result += [book]
        return parse_result

    def search(self, search_term="", column: str = "title", number_results=25):
        # TODO: Add missing search parameters.
        params = {
            "req": search_term,
            "column": column,
            "lg_topic": "fiction",
            "res": number_results,
        }
        response = requests.get(self.url, params)
        body = html.fromstring(response.text)
        search_result = []
        nresults = re.search(
            r"([0-9]*)filesfound",
            body.xpath("/html/body/div[2]/div[1]")[0].text.replace(" ", ""),
        )

        nresults = int(nresults.group(1))
        pages_to_load = int(math.ceil(number_results / 25.0))
        # Check if the pages needed to be loaded are more than the pages available
        if pages_to_load > int(math.ceil(nresults / 25.0)):
            pages_to_load = int(math.ceil(nresults / 25.0))
        for page in range(1, pages_to_load + 1):
            if len(search_result) > number_results:  # Check if we got all the results
                break
            params.update({"page": page})
            response = requests.get(self.url, params)
            body = html.fromstring(response.text)
            search_result += self.__parse(body)
            if page != pages_to_load:
                # Random delay because if you ask a lot of pages,your ip might get blocked.
                time.sleep(random.randint(250, 1000) / 1000.0)
        return [vars(_) for _ in search_result[:number_results]]
