# -*- coding: utf-8 -*-
"""
Created on Tue May 31 17:54:43 2016

@author: alex
"""




from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import time


class Window(object):
    '''
    define a window by passing the window class 
    varname: the name of the VARIABLE (the global binding) for this object.  This is the VARialbe NAME you give to the window.
    3) the website object that was assigned to the page with the window
    4) (Optional) a list of the options you want to cycle through for that window
       (if you dont know what options you want, leave it blank and the findOptions() 
       function will try to populate self.options)
    5) (Optinal) depends_on = 'Window', where "Window" is the name of a previously
        assigned window which affects the options for the current window
    '''
    instances = []   #this list will capture instances of the class
    
    def __init__(self, varname, website, options=None, depends_on=None):
        self.varname = varname #get the name of the variable, which is also the name of the window
        self.website = website #a website object
        self.name = self.website.windows[self.varname] #this gets the right window ID/name tag by referencing the website's window dictionary

        self.browser = website.browser #this is the selenium browser object
        self.default_removed = False #this records whether you have used the removeDefault function yet
        self.__class__.instances.append((self.varname, self)) #adds the variable name to a classwide list
        try: #try entering the id/name and getting the associated html element tag
            windowType = self.browser.find_element_by_id(self.name).tag_name #get the tag based on an ID   
        except NoSuchElementException:
            windowType = self.browser.find_element_by_name(self.name).tag_name #get the tag based on a name
        if windowType == 'select': # if the window has the 'select' tag 
            self.type = 'pulldown' # the tag indicates a pulldown menu - assign the type of window as pulldown
        else: #if it does not have a select tag, assume its some type of input window
            self.type = 'input' #assign the type of window as input
        if options: #if a list of options is already specified
            self.options = options #store the list of options
        if not options: 
            if depends_on: #if depends_on = <window>, 
                self.depends_on = depends_on         
                print (str(self.varname) +' depends on the ' + str(self.depends_on.varname) + ' window')
                self.options = self.findOptions_dependents()             
            else:
                pass
                self.options = self.findOptions() # run the findOptions function and pass the results to the objects options
        
        print ('successfully assigned ' + str(self.type) + ' type window: name/ID = ' + str(self.name))       
                        
    
    def findOptions_dependents(self):
        '''
        this function is used only when one window's options depend on the input
        of another (previously assigned) window.
        '''
        if self.type != 'pulldown':
            raise Exception('This is not a pulldown window, so the values are not dependent on any other window')            
        try:
            optionListFull = [] #initialize empty list to hold new options
            for option in self.depends_on.options: #loop through the options of the parent window
                try:
                    Select((self.browser).find_element_by_name(self.depends_on.name)).select_by_visible_text(option) #select the parent option
                except NoSuchElementException:
                    Select((self.browser).find_element_by_id(self.depends_on.name)).select_by_visible_text(option) #select the parent option                                        
                time.sleep(.3) #pause for load          
                optionListFull = optionListFull + self.findOptions() #add the results from the findOptions function to the list of options
            optionListFull = [x for x in optionListFull if x != 'Select'] #remove any options that say "Select" from the list 
            return set(optionListFull) #assign the unique values from the list to the object
        except AttributeError:
            print('this window does not depend on ' +str(self.depends_on.varname))

    
    def removeDefualt(self): 
        '''
        sometimes there is a default option that should not be selected from a pulldown
        it will usually appear first, so this just removes the first option from the list!
                '''
        if not self.default_removed: #if this function has not already be excercised
            tempopts = self.options   #get the options list             
            tempopts.remove(tempopts[0]) #remove the first item in the list
            self.options = tempopts #reassign the options 
            self.default_removed = True #change the value to indicate that the function was called already
        
    def findOptions(self):
        #get the text for options associated with the element with <name> (from whatever url browser is set to)
        optionList = [] #initialize empty list to hold the options
        if self.type == 'pulldown':
            try:
                select = Select((self.browser).find_element_by_name(self.name)) #get the html text from the object with <name>
            except NoSuchElementException: #if the name isn't found, try the same string as the ID
                select = Select((self.browser).find_element_by_id(self.name)) #get the html text from the object with <id>
            for opt in select.options: #loop through the options tags in the html that was selected
                optionList.append(opt.text) #append the option to a list 
            return optionList
        else: 
            input_html = self.website.soup.findAll('input',{'name':self.name})
            if not input_html:
                input_html = self.website.soup.findAll('input',{'ID':self.name})
                if not input_html:
                    raise Exception("This window is could not be identified.  Probably its not a part of a regular html form")
            if input_html[0]['type'] == "text":
                print("This is a text input window so you will have to make a list of options and pass it to this object")
                return []
            else:
                # TODO: add code to get all the input forms with right ID or Name and get those options? This might not play nice with the iterator though
                print("This window is a checkbox or other unrecognized format.  I haven't built in the functionality for this type of winow yet, maybe I will in 2.0")                
                return []
                