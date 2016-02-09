# libgen-python-api
A Python library that provides an api to search and get links from Books,Magazines,Comics,... from Library Genesis.

Requirements:
-------------
* Python 3/2
* Grab library and it's dependencies.

Installation:
-------------
Two options:
* Clone this repo and use "python setup.py install"
* Use pip, "pip install libgenapi"

Example of usage:
-----------------

> import libgenapi

> lg=libgenapi.Libgenapi(["http://[INSERT MIRROR DOMAIN 1 HERE].com","http://[INSERT MIRROR DOMAIN 2 HERE].com]) # You can add as many mirrors as you want.

> lg.search("python")


Then the results are something like this (but... without the crazyness :P real links and titles...):

        [
            {
                "author":"Dat Guy",
                "series":"Library of New Guy Studies volume 420",
                "title":"Dat perfect 5/7 Title !",
                "isbn":[123456],
                "edition":"[1 ed.]",
                "publisher":"WHo knows? Me no!",
                "year":"420",
                "pages":"420",
                "language":"chan",
                "size":"420 kb",
                "extension":"vap",
                "mirrors":["http://IDontWantADMCA.takedown/view.php?id=1337HAYKER",
                         "http://IDontWantADMCA.takedown/ads.php?md5=MD5HERE",
                         "http://IDontWantADMCA.takedown/md5/MD5HERE",
                         "http://IDontWantADMCA.takedown/md5/MD5HERE"
                         ]
            }
        ]
