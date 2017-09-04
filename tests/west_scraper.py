# -*- coding: utf-8 -*-
"""
Created Jan 22, 2016

@author: Dee
"""
from scrapedyno import Website, Window, Dino, all_tables_scraper

#get the url for inputs
url = 'https://bankofthewest.mortgagewebcenter.com/CheckRates/SearchCriteria.asp?PID=22' #set url

#assign webbrowser (this comes first so you can scrape window options on assignment)
west = Website(url) #assign website to scrape

#----------------------------------------------------------------------------------
'''
Windows must be assigned with the prefix sc. in order for the getWindows function to work later!
'''
#-----ASSIGN OPTIONS ------------------------------------------------------------
types = ['Purchase']
states = ['Idaho','Iowa']
counties = ['Adams ', 'Clay ']
priceList = [100000,500000]
loanList = [75000, 450000]

#-----ASSIGN WINDOWS ------------------------------------------------------------

#assign pulldowns
loanPurpose = Window('LoanPurpose',west) #assign the Loan Purpose window. 
state = Window('State',west,states) #assign the state window
county = Window('County',west,depends_on=state) #assign the "county" window
#sc.propuse=sc.window('propuse', ...
#sc.proptype=sc.window('proptype', ...
#sc.creditscore=sc.window('creditscore', ...
#sc.veteran=sc.window('veteran', ... 

#assign input windows
purchasePrice = Window('PurchasePrice',west,options=priceList)
loanAmount = Window('LoanAmount', west,options=loanList)

#--------Assign Submit Button-------------------------------------------------------

clickID='get-quotes-button' #pass the html name or ID for the submit button


windows = Window.instances
tool = Dino(west,all_tables_scraper,clickID,windows=windows,timeSleep=12) #assign the scrape tool.  This object will fill in the options and retrieve scraped data
tool.print_tables() #get a list of tables available for scraping.  Optional
'''
tool.scrape(0,[0,1,3]) #scrape the selected data.  You can pass this arguments.  Type tool.help
data = tool.data

'''


