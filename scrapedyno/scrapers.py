# -*- coding: utf-8 -*-
"""
Created on Sun Jun 19 15:09:21 2016

@author: alex
"""

import pandas as pd
import os
import time
from .scrapely_mod import MonkeyPatch
import hashlib
import scrapely
from .utilities import HTMLTableParser, isnumber

def advanced_scraper(website,data=None):
    '''
    website: website type object with selenium browser
    data: values contain the data that should be used to create the template.  
    Keys contain arbitrary lables.  See https://github.com/scrapy/scrapely
    for example of the dictionary format.
    '''
    MonkeyPatch()            
    
    page_id = hashlib.sha1(website.url).hexdigest()  
    filename = 'scrapers/%s' % page_id
    scraper = scrapely.ScraperMod() #the scraper object gets imported from the MonkeyPatch function
    if not os.path.isfile(filename):
        file = open(filename,'w')
        scraper.train_mod(website,data)
        scraper.tofile(file)
        file.close
    else:
        file = open(filename,'r+')
        scraper = scraper.fromfile(file)
        file.close()
    
    newData = scraper.scrape_mod(website)
    newFrame = pd.DataFrame(newData, index=[0])
    newFrame['time'] = (time.strftime("%H:%M:%S"))
    newFrame['date'] = (time.strftime("%d/%m/%Y")) 
    
    return newFrame

def basic_table_scraper(website, table_number=None,row_numbers=None):
    '''
    allows you to specify the exact parts of the table you want to scrape. In addition to
    selecting the table numbers, you can also select the row numbers.
    use the print_tables function on the scrapetool to identify table and row numbers (indexed from 0)     
    
    '''
    if not table_number or not row_numbers:
        raise KeyError('This scraper needs you to tell it which table and rows to scrape using table_number= and row_number= as keyword arguments')
    
    html = website.browser.page_source
    parser = HTMLTableParser()
    parser.feed(html)
    try:
        table = parser.tables[table_number]
        data = pd.DataFrame(columns=table[row_numbers[0]])
    except IndexError:
        print 'the scraper could not find the right table or row, this will be handled by the scrape function'
        return
    print 'the following columns were assigned for scraping: ' + ", ".join(table[row_numbers[0]])
    for i in range(len(row_numbers)):
        if i == 0: #skip the first row, since it defines variables not data
            pass
        else:
            values = table[row_numbers[i]]
            tempData = pd.DataFrame(data=[values], columns=table[row_numbers[0]])
            data = data.append(tempData)
    data['time'] = (time.strftime("%H:%M:%S"))
    data['date'] = (time.strftime("%d/%m/%Y"))     
    return data

class all_tables_scraper(object):
    '''
    a scraper that can return all tables on a page, return a single table, 
    or return specified rows from a single table
    '''
    @staticmethod
    def run(website, transpose=False, get_tables=None, get_rows=None):
        '''
        This unbound method is automatically run when the scraper is specified in the scrapeTool.  
        transpose : boolean indicating if variables names are listed on the left side instead of top    
        get_table : scrape only a specific table number 
        get_rows : scrape only specified rows from table 
        NOTE: use the Dino's print_tables function to view tables available for scraping
        '''
        transpose_temp = False # set temporary transpose boolean to False as default

        if get_rows and not get_tables: #logical check that user selected a table to scrape rows from
            raise KeyError('You need to specify a single table for scraping using the get_table key')
        
        html = website.browser.page_source #get html
        parser = HTMLTableParser() #assign parser object
        parser.feed(html) #pass html to parser object
        dataList = [] #create empty list to hold dataframes if tables > 1
        
        if get_tables: #if a specific table is specified
            copyTables = parser.tables
            parser.tables = [] #reset the parser.tables to be an empty list            
            [parser.tables.append(table) for table in [copyTables[i] for i in get_tables]] #pull out each table assigned in get_tables and reassign it to parser.tables
            
        for i in range(len(parser.tables)): # for each table 
        
            table = parser.tables[i] #assign table for scraping 
            if get_rows: #if rows are scraped, 
                table = list(table[i] for i in get_rows) #replace the table with only the desired rows
            
            data = pd.DataFrame(data=table[1:], columns=table[0]) #assign table data to a dataframe, using the first row as the column values
            
            
            #begin checking procedure to determine if table should be transposed
            allStrings = True #assume all the table's values are strings
            sideStrings = True #assume all values in col=0 are strings
            topStrings = True #assume all values in row=0 are strings
            allStrings_temp = allStrings
            sideStrings_temp = sideStrings
            topStrings_temp = topStrings            
            
            for j in range(len(table)): #for each row in the table
                try:
                    valuetest = table[j][j].encode('ascii','ignore') #get the diagonal value
                    allStrings = not isnumber(valuetest) #test if the value is a number
                except IndexError: #if col < row, move on
                    pass
                if allStrings_temp != allStrings: #if the value is a number, stop checking 
                    break
            for j in range(len(table)): #for each row in the table
                valuetest = table[j][0].encode('ascii','ignore') #get the value of the first col
                sideStrings = not isnumber(valuetest) #test if its a number
                if sideStrings_temp != sideStrings: #i if the value is a number, stop checking
                    break
            for j in range(len(table[0])): #for each col in the table
                valuetest = table[0][j].encode('ascii','ignore') #get the value of the first col
                topStrings = not isnumber(valuetest) #test if its a number
                if topStrings_temp != topStrings: #if the value us a number, stop checking
                    break
            notAllStrings = not allStrings #create a flag that is true if not all values are strings          
            notTopStrings = not topStrings #create a flag that is true if not all values in the top row are strings            
            if sideStrings & notTopStrings & notAllStrings: #if the table has numbers but all the values in the first col are strings, assume the table is "sideways"
                transpose_temp = True
                                
            if transpose or transpose_temp: # if the table should be transposed
                    data = data.transpose() #transpose the data
                    data.columns = data.iloc[0] #use the first row of data as column names 
                    print("Sideways table detected, transposing. Set sideTable=False to prevent this action")      
            
            transpose_temp = False #reset temporary transpose variable

            #add time and date to the data
            data['time'] = (time.strftime("%H:%M:%S"))
            data['date'] = (time.strftime("%d/%m/%Y")) 
            dataList.append(data) #add the dataset to the list of scraped tables
        
            return dataList