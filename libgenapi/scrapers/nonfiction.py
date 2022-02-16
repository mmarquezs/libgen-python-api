import math
from random import random
import re
from time import time
from typing import List
from .helpers.lxml_helpers import get_all_text_in_element
from lxml.etree import _Element
import requests
from lxml import html


class NonFictionBook:
    id: int  # noqa: A003 | Shadowing id here doesn't mather.
    author: str | None
    series: str | None
    title: str
    edition: str | None
    isbn: str | None
    publisher: str | None
    year: int | None
    pages: int | None
    language: str | None
    size: str | None
    extension: str | None
    mirrors: List[str]

    def __init__(self):
        self.mirrors = []


class NonFictionScraper:
    __columns = [
        "id",
        "author",
        "series_title_edition_and_isbn",
        "publisher",
        "year",
        "pages",
        "language",
        "size",
        "extension",
        "mirror",
        "mirror",
        "mirror",
    ]

    def __init__(self, url):
        self.url = url

    def __get_mirror(self, element: _Element) -> str:
        return str(element.xpath("a/@href")[0]).replace("../", self.url + "/")

    def __get_author(self, element: _Element) -> str | None:
        return get_all_text_in_element(element)

    def __get_title(self, element: _Element) -> str:
        return str(element.xpath("a/text()")[0])

    def __get_isbn(self, element: _Element) -> List[str] | None:
        text = get_all_text_in_element(element)
        if text is None:
            return None
        reg_isbn = re.compile(
            r"(ISBN[-]*(1[03])*[ ]*(: ){0,1})*"
            + "(([0-9Xx][- ]*){13}|([0-9Xx][- ]*){10})"
        )
        if reg_isbn.search(text) is not None:  # isbn found
            return [
                reg_isbn.search(_).group(0)
                for _ in text.split(",")
                if reg_isbn.search(_) is not None
            ]
        return None

    def __get_search_results_table_rows(self, element: _Element) -> _Element:
        return element.xpath('//body/table[contains(@class,"c")]//tr[position()>1]')

    def __get_edition(self, element: _Element) -> str | None:
        text = get_all_text_in_element(element)
        if text is None:
            return None
        reg_edition = re.compile(r"(\[.+.*ed.*?\.?\])", re.IGNORECASE)
        if reg_edition.search(text) is not None:
            return text
        return None

    def __parse_column(
        self, book: NonFictionBook, column: str, document: _Element
    ) -> None:
        # Getting mirror links
        if column == "mirror":
            mirror = self.__get_mirror(document)
            if len(mirror) > 0:
                book.mirrors += [mirror]
        elif column == "author":
            book.author = self.__get_author(document)
        elif column == "series_title_edition_and_isbn":
            book.title = self.__get_title(document)
            # If there is green text it means there is the title and something else.
            green_text = document.xpath("a/font")

            element: _Element
            for element in green_text:
                if (i := self.__get_isbn(element)) is not None:
                    book.isbn = i
                elif (e := self.__get_edition(element)) is not None:
                    book.edition = e
                elif (s := get_all_text_in_element(element)) is not None:
                    book.series = s
        else:
            setattr(book, column, get_all_text_in_element(document))

    def __parse(self, doc: _Element) -> List[NonFictionBook]:
        parse_result = []

        resultRow: _Element
        for resultRow in self.__get_search_results_table_rows(doc):
            book = NonFictionBook()

            col: _Element
            for i, col in enumerate(resultRow.xpath("td[position()<last()]")):
                if i > (len(self.__columns) - 1):
                    break
                self.__parse_column(book, self.__columns[i], col)
            parse_result += [book]
        return parse_result

    def search(
        self, search_term: str, column: str = "title", number_results: int = 25
    ) -> List[dict]:
        params = {
            "req": search_term,
            "column": column,
            "lg_topic": "libgen",
            "res": number_results,
        }
        url = self.url + "/search.php"
        response = requests.get(url, params)
        body = html.fromstring(response.text)
        search_result = []
        nbooks = re.search(
            r"([0-9]*) (books|files)",
            body.xpath("/html/body/table[2]/tr/td[1]/font")[0].text,
        )
        nbooks = int(nbooks.group(1))
        pages_to_load = int(math.ceil(number_results / 25.0))
        # Check if the pages needed to be loaded are more than the pages available
        if pages_to_load > int(math.ceil(nbooks / 25.0)):
            pages_to_load = int(math.ceil(nbooks / 25.0))
        for page in range(1, pages_to_load + 1):
            if len(search_result) > number_results:  # Check if we got all the results
                break
            params.update({"page": page})
            response = requests.get(url, params)
            body = html.fromstring(response.text)
            search_result += self.__parse(body)
            if page != pages_to_load:
                # Random delay because if you ask a lot of pages,your ip might get blocked.
                time.sleep(random.randint(250, 1000) / 1000.0)

        return [vars(_) for _ in search_result[:number_results]]
