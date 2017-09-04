# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 21:38:51 2016

@author: alex
"""

from scrapedyno import Website, Window, Dino, all_tables_scraper

url = 'https://www.wellsfargo.com/mortgage/rates/calculator?dm=DMIGOGHCF4' #set url
wells = Website(url) #assign website to scrape


#assign pulldown windows
loanPurpose = Window('LoanPurpose',wells)
state = Window('PropertyState',wells)
#county = window('PropertyCounty',wells,depends_on=state)
county = Window('PropertyCounty',wells)
# fix associated pulldown options
loanPurpose.options = ['Purchase'] #reassign window options
state.options = ['MA','NH'] 
county.options = ['Suffolk','Middlesex','Carroll'] #note that this is a kluge, normally the county options available depend on the state

#assign input boxes
homeValList = [100000,500000]
downPayList = [25000, 50000]

#assign inputs windows
homeValue = Window('HomeValue', wells,options=homeValList)
downPayment = Window('DownPayment', wells,options=downPayList)
#-----Begin Scrape Procedure-------------------------------------------------------------

clickID='submitButton' #pass the html name or ID for the submit button
windows = Window.instances
tool = Dino(wells,all_tables_scraper,clickID,windows=windows,timeSleep=12) #assign the scrape tool.  This object will fill in the options and retrieve scraped data
#NOTE: the find_table and print_table functions won't work because the front end database has an intermediate step
tool.print_tables()

tool.scrape(get_table = 1, get_rows=[1,3]) #scrape the selected data.  You can pass this arguments.  Type tool.help
#data = tool.data




