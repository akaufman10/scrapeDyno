# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 16:00:47 2016

@author: alex
"""

from seleniumrequests import Chrome
from bs4 import BeautifulSoup
from distutils.spawn import find_executable

class Website(object):
    '''
    An container that holds lists of search input options and the page(s) html for a given site.
    Most importantly, this object contains the browser object for given url.
    The website object finds out what forms (pulldown and input) are available on the given page
    Use the getForms function to find out the identifying information for the forms
    See the python selenium documentation for the browser object
    '''
        
    def __init__(self, url, path_to_webdriver=None):
        '''
        The webdriver is needed to use Selenium.  
        Users may need to modify the path to their local webdriver.  
        Dino automatically looks for the webdriver in its default download location (determined by local OS and selenium)
        url: the url for the input page of the site to be scraped        
        path_to_webdriver: specify the location of the webdriver application used by selenium
        you can try leaving it blank and Dino will check the defaul selenium location
        '''
        self.url = url
        if path_to_webdriver: #if the path is specified
            self.path = path_to_webdriver 
        else: #otherwise assign the default location
            self.path = self.find_webdriver()
        self.goTo()
        self.getForms()
        self.getWindows()
        
    def find_webdriver(self):
        '''
        this is defined as a separate method so the user can attempt to locate the webdriver manually
        '''
        return find_executable('chromedriver')
    
    
    def resetPage(self):
        '''
        reset the browser to the specified URL.
        #NOTE: THIS DOES NOT CLEAR FORMS OR RESET OTHER OBJECTS!                
        '''
        self.browser.get(self.url)         

    def resetHTML(self, browser):
        '''
        replace the stored html with the html for the browser's current page
        for development        
        '''
        self.html = self.browser.page_source

    def goTo(self):
        '''
        open a new browser and navigate to the url given.
                
        '''
        browser = Chrome(executable_path = self.path) #create browser object
        info = browser.request('GET',self.url) #navigate to the website and get site metadata
        browser.get(self.url) #reset the webpage
        html = browser.page_source #get the html from the current page
        soup = BeautifulSoup("".join(html)) #pass the html to the BS parser
                
        self.html, self.info, self.soup, self.browser = (html, info, soup, browser) #return these objects as attributes
        
    def getForms(self):      
        '''
        get the name or ID for each input and pulldown element.  This assumes each element is tagged in the HTML and not just text.
        '''
        inputElementNames = [] #initialize empty list to contain names of input elements
        selectElementNames = [] #initialize empty list to contain names of pulldown elements
        inputElementIDs = [] #initialize empty list to contain names of input elements
        selectElementIDs = [] #initialize empty list to contain names of pulldown elements
  
        try:
            inputs = self.soup.find_all('form') #find all 'form' elements in the html    
        except:
            print ('no forms found for ' +str(self.url))
            return
        for line in inputs: #for each element in the selected 'form' elements
            for row in line.find_all('input'): #for each row in the element that is an input element
                try:
                    inputElementNames.append(row['name']) #append the name of the input element to the list
                except KeyError:
                    inputElementIDs.append(row['id']) #append the ID of the input element to the list
                except:
                    pass
            for row in line.find_all('select'): #for each row in the element that is an select element
                try:
                    selectElementNames.append(row['name']) #append the name of the pulldown menu to the list
                except KeyError:
                    selectElementIDs.append(row['id']) #append the ID of the pulldown menu to the list
                except:
                    pass                        
        if inputElementNames:
            inputs = inputElementNames
        else:
            inputs = inputElementIDs
        if selectElementNames:
            pulldowns = selectElementNames
        else:
            pulldowns = selectElementIDs
            
        self.inputs, self.pulldowns = (inputs, pulldowns) 
        
    def getWindows(self):
        '''
        return a list of the windows that accept input
        '''
        htmlDict = {} #create an empty dictionary
        labels = self.soup.find_all('label') #find all the labels in the HTML 
        for label in labels: #for each label
            name = label.text.strip() #get the name of the label
            name = name.replace(' ','') #remove spaces from the name
            ID = label.get('for') #figure out what HTML tag the label is for
            htmlDict[name] = ID #make a dictionary with the label name and the input ID
        
        self.windows = htmlDict
            
 
