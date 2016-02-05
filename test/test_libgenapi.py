#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import *
from lib.libgenapi import Libgenapi


class LibgenApiTest(unittest.TestCase):
    @patch('lib.libgenapi.grab.Grab.go')
    def test_libgenapi_search_method_returns_correct_result(self,mock_go):
        lg=Libgenapi()
        f=open('testwebsearchresult.html','r')
        HTML=f.read().encode("utf-8")
        f.close()
        lg.g.setup_document(HTML)
        result=lg.search("python",1)
        expectedResult=[
            {
                "author":"Dat Guy",
                "series":"Library of New Guy Studies volume 420",
                "title":"Dat perfect 5/7 Title !",
                "isbn":"123456",
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
        self.maxDiff=None
        self.assertEqual(result,expectedResult)

if __name__ == '__main__':
    unittest.main()
        
