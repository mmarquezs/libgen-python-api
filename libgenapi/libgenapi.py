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
    DONE -> Search multiple pages untile the number_results is meet or the end.
    TODO: Check for strange encodings, other langauges chinese,etc..
    TODO: Simplify,simplify,simply...For exemple the book dictionary should
    start with all keys with an empty string.
    TODO: Change the actual output to json?
    TODO: Make a example terminal app that uses it
    TODO: STARTED -> Add parameters to the search apart from the search_term
    """

    class __Libgen(object):
        def __init__(self,url):
            self.url=url

        def __parse(self,doc):
            book = {"author":None, "series":None, "title":None, "edition":None, "isbn":None,
                    "publisher":None, "year":None, "pages":None, "language":None, "size":None,
                    "extension":None, "mirrors":None}
            i = 0
            d_keys = ["author", "series_title_edition_and_isbn", "publisher", "year", "pages",
                    "language", "size", "extension", "mirror","mirror","mirror","mirror"]
            parse_result = []
            for result in doc.select('//body/table[3]/tr[position()>1]/td[position()>1'+ \
                                                'and position()<last()]'):
                if i > len(d_keys)-1:
                    parse_result += [book]
                    i = 0
                    book = {"author":None, "series":None, "title":None, "edition":None, "isbn":None,
                            "publisher":None, "year":None, "pages":None, "language":None, "size":None,
                            "extension":None, "mirrors":None}
                if d_keys[i] == "mirror":            # Getting mirror links
                    mirror=result.select("a/@href")
                    if len(mirror)>0:
                        if book["mirrors"] is None:
                            book["mirrors"] = [mirror.text()]
                        else:
                            book["mirrors"] += [mirror.text()]
                        book["mirrors"][-1]=book["mirrors"][-1].replace("../",self.url+"/")
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

        def search(self, search_term, column="title", number_results=25 ):
            g = grab.Grab()
            request={"req":search_term,"column":column}
            if sys.version_info[0] < 3:
                url = self.url+"/search.php?"+ \
                        urllib.urlencode(request)
            else:
                url = self.url+"/search.php?"+ \
                        urllib.parse.urlencode(request)
            g.go(url)
            search_result = []
            nbooks = re.search(r'([0-9]*) books',
                            g.doc.select("/html/body/table[2]/tr/td[1]/font").text())
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
                    url = self.url+"/search.php?"+ \
                        urllib.urlencode(request)
                else:
                    url = self.url+"/search.php?"+ \
                        urllib.parse.urlencode(request)
                g.go(url)
                search_result += self.__parse(g.doc)
                if page != pages_to_load:
                    # Random delay because if you ask a lot of pages,your ip might get blocked.
                    time.sleep(random.randint(250, 1000)/1000.0)
            return search_result[:number_results]


    class __Scimag(object):
        # http://libgen.io/scimag/index.php?s=DOI_or_PMID_or_Author_%2B_Article&journalid=title_or_issn&v=Volume_or_year&i=Issue&p=Pages&redirect=1
        def __init__(self,url):
            self.url=url

        def __parse(self,doc):
            article = {"doi":None, "author":None, "article":None, "doi_owner":None, "journal":None,
                       "issue":None, "issn":None, "size":None, "mirrors":[]}
            i = 0
            d_keys = ["doi_and_mirrors", "author", "article", "doi_owner", "journal", "issue", "issn", "size"]
            parse_result = []
            #/html/body/table[2]/tbody/tr[1]
            for result in doc.select('/html/body/table[2]/tr/td[position()<last()]'):
                if i > len(d_keys)-1:
                    parse_result += [article]
                    i = 0
                    article = {"doi":None, "author":None, "article":None, "doi_owner":None, "journal":None,
                               "issue":None, "issn":None, "size":None, "mirrors":[]}
                if d_keys[i] == "doi_and_mirrors":            # Getting doi and mirrors links
                    #/table/tbody/tr[1]/td[2]/nobr
                    article["doi"]=result.select("table/tr[1]/td[2]/nobr").text()
                    mirrors = result.select("table/tr//a/@href")
                    for mirror in mirrors:
                        article["mirrors"] += [mirror.text()]
                elif d_keys[i] == "issn":
                    article["issn"] = result.select("text()").node_list()
                else:
                    article[d_keys[i]] = result.text()
                i += 1
            parse_result += [article]
            return parse_result

        def search(self, search_term="", journal_title_issn="", volume_year="",issue="", pages="", number_results=25 ):
            g = grab.Grab()
            request={"s":search_term, "journalid":journal_title_issn, "v":volume_year, "i":issue, "p":pages, "redirect":"0"}
            if sys.version_info[0] < 3:
                url = self.url+"?"+ \
                        urllib.urlencode(request)
            else:
                url = self.url+"?"+ \
                        urllib.parse.urlencode(request)
            g.go(url)
            search_result = []
            #body > font:nth-child(7) Displayed first  100  results 
            #body > font:nth-child(7) Found 1 results
            nresults = re.search(r'([0-9]*) results',
                                 g.doc.select("/html/body/font[1]").one().text())
            nresults = int(nresults.group(1))
            pages_to_load = int(math.ceil(number_results/25.0)) # Pages needed to be loaded
            # Check if the pages needed to be loaded are more than the pages available
            if pages_to_load > int(math.ceil(nresults/25.0)):
                pages_to_load = int(math.ceil(nresults/25.0))
            for page in range(1, pages_to_load+1):
                if len(search_result) > number_results:  # Check if we got all the results
                    break
                url = ""
                request.update({"page":page})
                if sys.version_info[0] < 3:
                    url = self.url+"?"+ \
                        urllib.urlencode(request)
                else:
                    url = self.url+"?"+ \
                        urllib.parse.urlencode(request)
                g.go(url)
                search_result += self.__parse(g.doc)
                if page != pages_to_load:
                    # Random delay because if you ask a lot of pages,your ip might get blocked.
                    time.sleep(random.randint(250, 1000)/1000.0)
            return search_result[:number_results]


    def __init__(self, mirrors=None):
        self.mirrors = mirrors
        self.__selected_mirror = None
        self.libgen = None
        self.scimag = None
        self.fiction = None
        self.comics = None
        self.standarts = None
        self.magzdb = None
        if mirrors != None and len(mirrors)>0:
            self.__choose_mirror()
    def set_mirrors(self, list_mirrors):
        """
        Sets the mirrors of Libgen Genesis
        """
        self.mirrors = list_mirrors
        self.__choose_mirror()
    def __choose_mirror(self):
        g = grab.Grab()
        if self.mirrors is None:
            raise MissingMirrorsError("There are no mirrors!")
        if isinstance(self.mirrors, str):
            self.mirrors = [self.mirrors]
        last = len(self.mirrors)-1
        for i, mirror in enumerate(self.mirrors):
            try:
                if sys.version_info[0] < 3:
                    url = mirror
                    g.go(url)
                else:
                    url = mirror
                    g.go(url)
                self.__selected_mirror = mirror
                categories = g.doc("//input[contains(@name,'lg_topic')]").node_list()
                for category in categories:
                    if category.attrib["value"] == "libgen":
                        self.libgen = self.__Libgen(g.make_url_absolute(category.getnext().attrib["href"]))
                    elif category.attrib["value"] == "scimag":
                        self.scimag = self.__Scimag(g.make_url_absolute(category.getnext().attrib["href"]))
                break
            except grab.GrabError:
                if i == last:
                    raise MirrorsNotResolvingError("None of the mirrors are resolving, check" + \
                                                   "if they are correct or you have connection!")
    def search(self, search_term, column="title", number_results=25):
        warnings.warn("Deprecated Method, use Libgenapi().libgen.search() instead.", DeprecationWarning, stacklevel=2)
        return self.libgen.search(search_term,column,number_results)
