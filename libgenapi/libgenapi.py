# -*- coding: utf-8 -*-
"""
Library to search in Library Genesis
"""

import requests
from lxml import html
from scrapers import NonFictionScraper
from scrapers import FictionScraper

import warnings


class MissingMirrorsError(Exception):
    """
    Error shown when there are no mirrors.
    """

    pass


class MirrorsNotResolvingError(Exception):
    """
    Error shown when none of the mirrors are resolving.
    """

    pass


class Libgenapi(object):
    """
    Main class representing the library
    TODO: Add documentation
    TODO: Check for strange encodings, other langauges chinese,etc..
    TODO: Change the actual output to json?
    TODO: Make a example terminal app that uses it
    TODO: Remove duplicate code. Reuse code between the different sections (LibGen,Scientific articles, Fiction,etc..).
    """

    def __init__(self, mirrors=None):
        self.mirrors = mirrors
        self.libgen = None
        self.scimag = None
        self.fiction = None
        self.comics = None
        self.standarts = None
        self.magzdb = None
        if mirrors is not None and len(mirrors) > 0:
            self.__choose_mirror()

    def set_mirrors(self, list_mirrors):
        """
        Sets the mirrors of Libgen Genesis
        """
        self.mirrors = list_mirrors
        self.__choose_mirror()

    def __choose_mirror(self):
        if self.mirrors is None:
            raise MissingMirrorsError("There are no mirrors!")
        if isinstance(self.mirrors, str):
            self.mirrors = [self.mirrors]
        last = len(self.mirrors) - 1
        for i, mirror in enumerate(self.mirrors):
            try:
                url = mirror
                response = requests.get(url)
                body = html.fromstring(response.text)
                categories = body.xpath("//input[contains(@name,'lg_topic')]")
                for category in categories:
                    if category.attrib["value"] == "libgen":
                        self.libgen = NonFictionScraper(url)
                    # elif category.attrib["value"] == "scimag":
                    #     self.scimag = self.__Scimag(
                    #         url + "/" + category.getnext().attrib["href"]
                    #     )
                    elif category.attrib["value"] == "fiction":
                        self.fiction = FictionScraper(url)
                    # elif category.attrib["value"] == "comics":
                    #     self.comics = self.__Comics(
                    #         url + "/" + category.getnext().attrib["href"]
                    #     )
                break
            except Exception:
                if i == last:
                    raise MirrorsNotResolvingError(
                        "None of the mirrors are resolving, check"
                        + "if they are correct or you have a working internet connection!"
                    )

    def search(self, search_term, column="title", number_results=25):
        warnings.warn(
            "Deprecated Method, use Libgenapi().libgen.search() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.libgen.search(search_term, column, number_results)
