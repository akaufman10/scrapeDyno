# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 17:09:54 2016

@author: alex
"""

from scrapely import Scraper    
from scrapely.htmlpage import HtmlPage

def MonkeyPatch():
    import scrapely
    scrapely.ScraperMod = ScraperMod


class ScraperMod(Scraper):
    
    def train_mod(self, website, data, encoding=None):
        page = self.url_to_page_mod(website, encoding)
        self.train_from_htmlpage(page, data)

    def scrape_mod(self, website, encoding=None):
        page = self.url_to_page_mod(website, encoding)    
        return self.scrape_page(page)
    
    def url_to_page_mod(self,website, encoding=None, default_encoding='utf-8'):
        '''this function has been modified to take a website object insteal of going to the url    
        '''
        """Fetch a URL, using python urllib2, and return an HtmlPage object.
        
        The `url` may be a string, or a `urllib2.Request` object. The `encoding`
        argument can be used to force the interpretation of the page encoding.
        
        Redirects are followed, and the `url` property of the returned HtmlPage object
        is the url of the final page redirected to.
        
        If the encoding of the page is known, it can be passed as a keyword argument. If
        unspecified, the encoding is guessed using `w3lib.encoding.html_to_unicode`.
        `default_encoding` is used if the encoding cannot be determined.
        """
        
        #fh = urllib2.urlopen(url)
        #info = fh.info()
        info = website.info
        headers_dict = dict(info.headers)
        #body_str = fh.read() 
        body= website.browser.page_source
        # guess content encoding if not specified
        if encoding is None:
            encoding = default_encoding
        return HtmlPage(website.url, headers=headers_dict, body=body, encoding=encoding)



'''
#monkey patch the scrapely functions manually!  NOTE: requires functions to be defined outside class
def MonkeyPatch():
    import scrapely
    from scrapely import Scraper
    scrapely.Scraper2 = Scraper2    
    
    Scraper.train = train_mod
    Scraper.scrape = scrape_mod
    scrapely.url_to_page = url_to_page_mod
'''


