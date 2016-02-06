import grab
import re
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
        for i,mirror in enumerate(self.mirrors):
            try:
                self.g.go(mirror+"/search.php?req="+searchTerm)
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
            if i==11:            # Getting mirror links
                #print(type(result))
                book[dKeys[i]]=[x.text() for x in result.select("a/@href")]
            elif i==1:          # Getting title,isbn,series,edition
                try:            # Dammit... There is series,isbn or edition or all, now we have to separate it...
                    greenText=result.select("a/font")
                    book["title"]=result.select("a/text()").text()
                    regIsbn=re.compile(r'([A-z])')
                    regEdition=re.compile(r'(\[[0-9] ed\.\])')
                    for element in greenText:
                        if regIsbn.search(element.text())==None:
                            book["isbn"]=element.text()
                        elif regEdition.search(element.text())!=None:
                            book["edition"]=element.text()
                        else:
                            book["series"]=element.text()
                    i=i+3
                except:         #Easy, there is just the title. 
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
        
