# -*- coding: utf-8 -*-
import grab
import re
import math
import urllib
import sys
import weblib
if sys.version_info[0]>3:
    import urllib.parse

class MissingMirrorsError(Exception):
    pass
class MirrorsNotResolving(Exception):
   pass 
class Libgenapi(object):
    def __init__(self,mirrors=[]):
        self.g=grab.Grab()
        self.mirrors=mirrors
    def setMirrors(self,listMirrors):
        self.mirrors=listMirrors
    def search(self,searchTerm,numberResults=25):
        """
        TODO: 
        Add documentation
        Search multiple pages untile the numberResults is meet or the end.
        Check for strange encodings, other langauges chinese,etc..
        Simplify,simplify,simply...For exemple the book dictionary
        should start with all keys with an empty string.
        Change the actual output to json?
        Make a example terminal app that uses it
        Add parameters to the search apart from the searchTerm
        
        """
        error=None
        last=len(self.mirrors)-1
        if last==-1:
            raise MissingMirrorsError("There are no mirrors!")
        if type(self.mirrors)!=type([]):
            self.mirrors=[self.mirrors]
        for i,mirror in enumerate(self.mirrors):
            try:
                if sys.version_info[0]<3:
                    url=mirror+"/search.php?"+urllib.urlencode({"req":searchTerm})
                    self.g.go(url)
                else:
                    url=mirror+"/search.php?"+urllib.parse.urlencode({"req":searchTerm})
                    self.g.go(url)
                break
            except grab.GrabError as e:
                if i==last:
                    raise MirrorsNotResolving("None of the mirrors are resolving, check if they are correct or you have connection!")
                pass
        searchResult=[]
        book={}
        i=0
        dKeys=["author","series","title","edition","isbn","publisher","year","pages","language","size","extension","mirrors"]
        for result in self.g.doc.select('//body/table[3]/tr[position()>1]/td[position()>1 and position()<=10]'):
            if dKeys[i]=="mirrors":            # Getting mirror links
                book[dKeys[i]]=[x.text() for x in result.select("a/@href")]
            elif i==1:          # Getting title,isbn,series,edition
                try:            # Dammit... There is series,isbn or edition or all, now we have to separate it...
                    greenText=result.select("a/font")  # Cheking if there is any "green" text. If there is it means there is the title and something else.
                    book["title"]=result.select("a/text()").text()
                    # regIsbn=re.compile(r'([A-z])')  # There isn't letters? Then is an ISBN,I guess?¿? This would fail if there is a series with only numbers..
                    regIsbn=re.compile(r"(ISBN[-]*(1[03])*[ ]*(: ){0,1})*(([0-9Xx][- ]*){13}|([0-9Xx][- ]*){10})")  # A regex I found for isbn, not sure if perfect but better than mine. 
                    regEdition=re.compile(r'(\[[0-9] ed\.\])')
                    for element in greenText:
                        if regIsbn.search(element.text())!=None:
                            book["isbn"]=[]
                            # book["isbn"]=[]
                            for x in element.text().split(","):
                                book["isbn"]+=[regIsbn.search(x).group(0)]
                                # for isbn in regIsbn.seach(x):
                                #     book["isbn"]+=[isbn]
                        elif regEdition.findall(element.text())!=None:
                            book["edition"]=element.text()
                        else:
                            book["series"]=element.text()
                    i=i+3
                except weblib.error.DataNotFound:         #Easy, there is just the title. 
                    book["series"]=""  # Series Empty
                    i+=1
                    book["title"]=result.text()  # Title
                    i+=1
                    book["edition"]=""  # Edition empty
                    i+=1
                    book["isbn"]=""  # ISBN empty
            else:
                book[dKeys[i]]=result.text()
            i+=1
            if i>11:
                searchResult+=[book]
                i=0
                book={}
        return searchResult
        
