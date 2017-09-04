# -*- coding: utf-8 -*-
"""
Created on Sun Jun 19 15:06:09 2016

@author: alex
"""

import pandas as pd
from itertools import product
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import time
from copy import copy
from collections import OrderedDict
from .utilities import HTMLTableParser

class Dino(object):

    def __init__(self, website=None, scraper=None, clickID=None, windows = {},timeSleep = 10):
        '''
        website: a Website class object 
        scraper: any scraper built for the data page - must contain an unbound method "run" that performs scrape
        clickID:  #HTML ID or NAME that uniquely identifies the submit button
        windows: the "instances" attribute from a Window class object. 
        timeSleep: wait time for page to load after inputs are submitted (can also be used to space out queries)
        '''
        self.website = website # browser object
        self.windows = copy(windows) #should contain the "instnaces" attribute from a Window class object 
        self.windowDict = dict(windows) #make a dictionary from the list of windows
        self.scraper = scraper #scraper must have a run method
        self.clickID = clickID  
        self.timeSleep = timeSleep 
        self.getWindows()
        
    def getWindows(self): 
        '''
        Return an iterable with all window-option combinations.
        WARNING! this function creates a cartesian product of options!
        It gets big really fast! If you have 3 windows with 10 options each,
        thats 10^3 options = 1,000.  But if you have have 6 windows 10^6 options = 1,000,000! 
        TODO: build this function to accept dictionaries instead of lists to narrow down the possible
        combinations of options based on dependencies.         
        '''
        
        windowDict = OrderedDict((window[1].varname,window[1].options) for window in self.windows)  #make a dictionary that links windows and options
        tupples = [[(key,value) for value in windowDict[key]] for key in windowDict.keys()] #create a tupple for each window-option combo
        
        '''
        you can interpert the above assignment as "for each key in the dictionary, create 
        the tupple (key, value) for each value corresponding to that key"
        The product that is returned is a list of (name, option) tupples for each name
        '''    
        
        iteroptions = product(*tupples) #make an iterator from the tupples that includes all possible combination of options
        
        self.iterobject = iteroptions       
        
    def find_tables(self):
        '''
        identify tables that can be scraped from a dynamically loaded page.  
        This function inputs some test info and uses a lightweight scraper to return
        and show you what tables are dynamically loaded.  Most, but not all, dynamic pages
        will return queries in tabular format.
        The scraper used is ...
        '''

        for options in self.iterobject: #loop through each set of options
        
            skipOptions = False #default value for whether to skip this set of options     
          
            print ('inputting options:  ' + ', '.join('{}={}'.format(*opt) for opt in options))
                    
            tuppleCount = len(options) #get the number of options to input
                    
            for i in range(tuppleCount): #loop over each option to input
                window = options[i] #get the option 
                windowName = window[0] #get the option name
                windowID = self.windowDict[windowName].name #get the option html identifier
                windowOpt = window[1] #get the input/pulldown value
                windowType = self.windowDict[windowName].type #get the option type
                #the following code selects the option assuming that the window is identified by an HTML name or ID tag                    
                if windowType == 'pulldown': 
                    try:    #try using the window name to activate the window options 
                        Select((self.website.browser).find_element_by_name(windowID)).select_by_index(0) #reset the window
                        time.sleep(.1)
                        Select((self.website.browser).find_element_by_name(windowID)).select_by_visible_text(windowOpt) #input the window option
                    except NoSuchElementException: #try using the window html id to activate the window options
                        try: #this try statement is newsted as workaround for a bug
                            Select((self.website.browser).find_element_by_id(windowID)).select_by_index(0) #reset the window
                            time.sleep(.1)
                            Select((self.website.browser).find_element_by_id(windowID)).select_by_visible_text(windowOpt) #input the window option
                        except NoSuchElementException:
                            print ('didnt find window ' +str(windowName) + ' option ' + str(windowOpt))
                            skipOptions = True                                
                            pass
                if windowType == 'input':
                    try:
                        self.website.browser.find_element_by_id(windowID).clear()  
                        time.sleep(.1)
                        self.website.browser.find_element_by_id(windowID).send_keys(str(windowOpt))
                    except NoSuchElementException:
                        try: #this nested try statement is a workaround for a bug
                            self.website.browser.find_element_by_name(windowID).clear()  
                            time.sleep(.1)
                            self.website.browser.find_element_by_name(windowID).send_keys(str(windowOpt))
                        except NoSuchElementException:
                            print ('didnt find window ' +str(windowName) + ' option ' + str(windowOpt))
                            skipOptions = True                                
                            pass
            time.sleep(1)
                
            if skipOptions:
                continue
                
            try: #click submit after all options are entered
                self.website.browser.find_element_by_id(self.clickID).click() 
            except NoSuchElementException:
                self.website.browser.find_element_by_name(self.clickID).click() 
                
            time.sleep(self.timeSleep) #wait for the page to load
            html = self.website.browser.page_source #get the newly loaded page HTML
            parser = HTMLTableParser() #
            parser.feed(html) 
            self.tables = parser.tables #store the scraped tables
            self.website.resetPage() #load the original input page
            break
            
        self.getWindows() #remake the itterator with all options
    
    def print_tables(self):
        '''
        print the tables that were found in a readable format
        this can be used to extract a table number and row_numbers 
        to pass to the TODO NAME function
        '''
        try:
            self.tables
        except AttributeError:
            self.find_tables()
            pass

        for i in range(len(self.tables)):
            for j in range(len(self.tables[i])):
                print ('table' + str(i-1) + ' row' + str(j) + ' is:')
                print (self.tables[i][j])
    
        self.getWindows()
    
    def scrape(self, *args, **kwargs):
        '''
        the arguments here depend on the scraper being used
        use the find_tables and the print_tables functions to 
        determine the table and row numbers.
        
        scrape takes the list of option-combinations (an itterable)
        created by the getWindows function, and uses each option-combo
        to fill in the windows on the browser page.
        
        each time it fills in the options, it clicks the submit button and calls
        the scraper, which then passes back a pandas dataframe containing the 
        scraped data, which is appended to the objects data
        
        then the loop resets the webpage for the next options-combination
        '''           
        
        firstSearch = True
    
        for options in self.iterobject:
            
            skipOptions = False            
            
            print ('inputting options:  ' + ', '.join('{}={}'.format(*opt) for opt in options))
            
            windowList = []
            optionsList = []
            
            tuppleCount = len(options)
                    
            for i in range(tuppleCount):
                
                window = options[i]
                windowName = window[0]                    
                windowID = self.windowDict[windowName].name
                windowOpt = window[1]
                windowType = self.windowDict[windowName].type
                windowList.append(windowName)  #add the name of the window to the list
                optionsList.append(windowOpt) #add the selected option to the list
                if windowType == 'pulldown':
                    try:     
                        Select((self.website.browser).find_element_by_name(windowID)).select_by_index(0)
                        time.sleep(.1)
                        Select((self.website.browser).find_element_by_name(windowID)).select_by_visible_text(windowOpt)
                    except NoSuchElementException:
                        try: #this nested try statement is a workaround for a bug
                            Select((self.website.browser).find_element_by_id(windowID)).select_by_index(0)
                            time.sleep(.1)
                            Select((self.website.browser).find_element_by_id(windowID)).select_by_visible_text(windowOpt)
                        except NoSuchElementException:
                            print ('didnt find window ' +str(windowName) + ' option ' + str(windowOpt))
                            skipOptions = True                            
                            pass
                if windowType == 'input':
                    try: 
                        self.website.browser.find_element_by_id(windowID).clear() 
                        time.sleep(.1)
                        self.website.browser.find_element_by_id(windowID).send_keys(str(windowOpt))
                    except NoSuchElementException:
                        try: #this nested try statement is a workaround for a bug
                            self.website.browser.find_element_by_name(windowID).clear()              
                            time.sleep(.1)
                            self.website.browser.find_element_by_name(windowID).send_keys(str(windowOpt))
                        except NoSuchElementException:
                            print ('didnt find window ' +str(windowName) + ' option ' + str(windowOpt))
                            skipOptions = True                            
                            pass
                time.sleep(1)
            
            
            optionData = pd.DataFrame(data=[optionsList],columns=windowList)   
            optionData['key'] = 1
            try:      
                self.website.browser.find_element_by_id(self.clickID).click() 
            except NoSuchElementException:
                self.website.browser.find_element_by_name(self.clickID).click() 
            time.sleep(self.timeSleep)
            if skipOptions:
                tempData = optionData
            else:
                tempData = self.scraper.run(self.website,*args,**kwargs)
                tempData['key'] = 1
                tempData = pd.merge(tempData,optionData,on='key')
            if firstSearch:
                data = tempData
                firstSearch = False
            else:
                data = data.append(tempData)                  
            
            self.website.resetPage()
                
            self.data = data
            self.getWindows()
