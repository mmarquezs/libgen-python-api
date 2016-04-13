# -*- coding: utf-8 -*-
"""
Library to search in Library Genesis
"""

import time
import random
import re
import math
import sys
import urllib
if sys.version_info[0] > 3:
    import urllib.parse
import grab
import weblib

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
    """
    def __init__(self, mirrors=None):
        self.grabber = grab.Grab()
        self.mirrors = mirrors
        self.__selected_mirror = None
    def set_mirrors(self, list_mirrors):
        """
        Sets the mirrors of Libgen Genesis
        """
        self.mirrors = list_mirrors
    def __choose_mirror(self):
        if self.__selected_mirror is not None:
            return
        if self.mirrors is None:
            raise MissingMirrorsError("There are no mirrors!")
        if isinstance(self.mirrors, str):
            self.mirrors = [self.mirrors]
        last = len(self.mirrors)-1
        for i, mirror in enumerate(self.mirrors):
            try:
                if sys.version_info[0] < 3:
                    url = mirror
                    self.grabber.go(url)
                else:
                    url = mirror
                    self.grabber.go(url)
                self.__selected_mirror = mirror
                break
            except grab.GrabError:
                if i == last:
                    raise MirrorsNotResolvingError("None of the mirrors are resolving, check" + \
                                                   "if they are correct or you have connection!")
    def __parse_books(self):
        book = {"author":None, "series":None, "title":None, "edition":None, "isbn":None,
                "publisher":None, "year":None, "pages":None, "language":None, "size":None,
                "extension":None, "mirrors":None}
        i = 0
        d_keys = ["author", "series_title_edition_and_isbn", "publisher", "year", "pages",
                  "language", "size", "extension", "mirrors"]
        parse_result = []
        for result in self.grabber.doc.select('//body/table[3]/tr[position()>1]/td[position()>1'+ \
                                              'and position()<=10]'):
            # if len(search_result)>=number_results:
            #     break
                                                      # 'and position()<=10]')])
            if i > len(d_keys)-1:
                parse_result += [book]
                i = 0
                book = {"author":None, "series":None, "title":None, "edition":None, "isbn":None,
                        "publisher":None, "year":None, "pages":None, "language":None, "size":None,
                        "extension":None, "mirrors":None}
            if d_keys[i] == "mirrors":            # Getting mirror links
                book[d_keys[i]] = [x.text() for x in result.select("a/@href")]
            elif d_keys[i] == "series_title_edition_and_isbn": # Getting title,isbn,series,edition.
                try:
                    # If there isn't an exception there is series,isbn or edition or all,
                    # now we have to separate it...
                    #
                    # Cheking if there is any "green" text.
                    # If there is it means there is the title and something else.
                    # This makes an exception if there is nothing, which means no green text.
                    green_text = result.select("a/font")
                    book["title"] = result.select("a/text()").text()
                    # A regex I found for isbn, not sure if perfect but better than mine.
                    reg_isbn = re.compile(r"(ISBN[-]*(1[03])*[ ]*(: ){0,1})*"+ \
                                          "(([0-9Xx][- ]*){13}|([0-9Xx][- ]*){10})")
                    reg_edition = re.compile(r'(\[[0-9] ed\.\])')
                    for element in green_text:
                        if reg_isbn.search(element.text()) != None:  # isbn found
                            book["isbn"] = [reg_isbn.search(_).group(0)
                                            for _ in element.text().split(",")
                                            if reg_isbn.search(_) != None]
                        elif reg_edition.search(element.text()) != None:  # edition found
                            book["edition"] = element.text()
                        else:   # Series found
                            book["series"] = element.text()
                except weblib.error.DataNotFound:  #Easy, there is just the title.
                    book["title"] = result.text()  # Title found
            else:
                book[d_keys[i]] = result.text()
            i += 1
        parse_result += [book]
        return parse_result
    def search(self, search_term, column="title", number_results=25):
        """
        TODO:
        Add documentation
        DONE -> Search multiple pages untile the number_results is meet or the end.
        Check for strange encodings, other langauges chinese,etc..
        Simplify,simplify,simply...For exemple the book dictionary
        should start with all keys with an empty string.
        Change the actual output to json?
        Make a example terminal app that uses it
        STARTED -> Add parameters to the search apart from the search_term
        """
        request={"req":search_term,"column":column}
        self.__choose_mirror()
        if sys.version_info[0] < 3:
            url = self.__selected_mirror+"/search.php?"+ \
                    urllib.urlencode(request)
        else:
            url = self.__selected_mirror+"/search.php?"+ \
                    urllib.parse.urlencode(request)
        self.grabber.go(url)
        search_result = []
        nbooks = re.search(r'([0-9]*) books',
                           self.grabber.doc.select("/html/body/table[2]/tr/td[1]/font").text())
        nbooks = int(nbooks.group(1))
        pages_to_load = int(math.ceil(number_results/25.0)) # Pages needed to be loaded
        # Check if the pages needed to be loaded are more than the pages available
        if pages_to_load > int(math.ceil(nbooks/25.0)):
            pages_to_load = int(math.ceil(nbooks/25.0))
        for page in range(1, pages_to_load+1):
            if len(search_result) > number_results:  # Check if we got all the results
                break
            url = ""
            request.update({"page":page})
            if sys.version_info[0] < 3:
                url = self.__selected_mirror+"/search.php?"+ \
                      urllib.urlencode(request)
            else:
                url = self.__selected_mirror+"/search.php?"+ \
                      urllib.parse.urlencode(request)
            self.grabber.go(url)
            search_result += self.__parse_books()
            if page != pages_to_load:
                # Random delay because if you ask a lot of pages,your ip might get blocked.
                time.sleep(random.randint(250, 1000)/1000.0)
            return search_result[:number_results]
