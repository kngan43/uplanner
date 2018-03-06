from ..items import CourseInfo
from ..items import CourseLoader
import logging
import copy
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import scrapy
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from scrapy.http import Request
from scrapy.shell import inspect_response


class TestSpider(scrapy.Spider):
    name = 'Section'
    login_url = 'https://www.spire.umass.edu/psp/heproda/?cmd=login&languageCd=ENG#'
    start_urls = [login_url]

    def __init__(self):
        self.driver = webdriver.Chrome('C:/Users/Kerry Ngan\Miniconda3/chromedriver.exe')

    def parse(self, response):
        wait = WebDriverWait(self.driver,10)

        #login to spire
        self.driver.get(response.url)
        username = self.driver.find_element_by_id('userid')
        password = self.driver.find_element_by_id('pwd')
        with open('C:/Users/Kerry Ngan/Documents/login_info.txt') as f:
            line = f.read()
        f.close()
        login_info = line.split()
        username.send_keys(login_info[0])
        password.send_keys(login_info[1])
        self.driver.find_element_by_name('Submit').submit()

        #move to student center
        wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="ptifrmtgtframe"]')))
        student_center_url =self.driver.find_element_by_xpath('//*[@id="ptifrmtgtframe"]').get_attribute('src')
        self.driver.get(student_center_url)

        #click on class search button
        class_search = self.driver.find_element_by_xpath('//*[@id="DERIVED_SSS_SCL_SSS_GO_4$83$"]') 
        class_search.click()

        wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH"]')))

        #select options for searching
        self.driver.find_element_by_xpath('//*[@id="UM_DERIVED_SA_UM_TERM_DESCR"]/option[3]').click() #spring 2018
        self.driver.find_element_by_xpath('//*[@id="CLASS_SRCH_WRK2_SUBJECT$108$"]/option[35]').click() #computer science
        self.driver.find_element_by_xpath('//*[@id="CLASS_SRCH_WRK2_SESSION_CODE$12$"]/option[2]').click() #university
        self.driver.find_element_by_xpath('//*[@id="CLASS_SRCH_WRK2_SSR_OPEN_ONLY"]').click() #uncheck only open courses
        self.driver.find_element_by_xpath('//*[@id="CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH"]').click() #start search
        wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="CLASS_SRCH_WRK2_SSR_PB_NEW_SEARCH"]')))
        

        #start scraping spire for course information

        webelement_list = [] #creates a webelement list container
        index = 0 #count of the links on the page
        while  self.driver.find_elements_by_css_selector("[id^='DERIVED_CLSRCH_SSR_CLASSNAME_LONG$" + str(index) + "']"): 
            search_result = self.driver.find_element_by_css_selector("[id^='DERIVED_CLSRCH_SSR_CLASSNAME_LONG$" + str(index) + "']") #finds the first section for a course
            search_result.click() #clicks on the section
            wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="CLASS_SRCH_WRK2_SSR_PB_BACK"]'))) #wait for page to load
            driver_selector = Selector(text = self.driver.page_source)#update the driver selector with the current page source
            webelement_list.append(driver_selector.xpath("//div[@id = 'win0divPSPAGECONTAINER']/table/tbody/tr")) #adds webelements from course section
            self.driver.find_element_by_css_selector("[id^='CLASS_SRCH_WRK2_SSR_PB_BACK']").click() #clicks on view search results to go back
            wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="DERIVED_CLSRCH_SSR_CLASSNAME_LONG$1"]')))#wait for page to load
            index = index + 1 
        else:
            file = open('C:/compsci326/uplanner/project1/scrapespire/test.txt','w')
            file.write(str(self.driver.find_elements_by_css_selector("[id^='DERIVED_CLSRCH_SSR_CLASSNAME_LONG$" + str(index) + "']")))
            file.write("\n"+"does not exist at " + str(index))
            file.close()
        

        #creates an item for each section
        cloader = None
        for webelement in webelement_list:
            for selector in webelement:
                if(cloader is None):
                    cloader = CourseLoader(item = CourseInfo(), selector = selector)
                else:
                    cloader.selector = selector

                if selector.css("[id^='DERIVED_CLSRCH_DESCR200']"):
                    cloader.add_css('name', "[id^='DERIVED_CLSRCH_DESCR200']")

                if selector.css("[id^='win0divSSR_CLS_DTL_WRK_GROUP1']"):
                    cloader.add_css('class_number', "[id^='SSR_CLS_DTL_WRK_CLASS_NBR']")
                    cloader.add_css('units', "[id^='SSR_CLS_DTL_WRK_UNITS_RANGE']")
                    cloader.add_css('career', "[id^='PSXLATITEM_XLATLONGNAME']")
                    cloader.add_css('grading', "[id^='GRADE_BASIS_TBL_DESCRFORMAL']")
                    cloader.add_css('gened', "[id^='UM_DERIVED_SA_UM_GENED']")
                    cloader.add_css('rap_tap_hlc', "[id^='UM_RAPTAP_CLSDT_UM_RAP_TAP']")
                    cloader.add_css('topic', "[id^='CRSE_TOPICS_DESCR']")

                if selector.css("[id^='win0divSSR_CLSRCH_MTGGP']"):          
                    cloader.add_css('date', "[id^='MTG_SCHED']")
                    cloader.add_css('room', "[id^='MTG_LOC']")
                    cloader.add_css('instructor', "[id^='MTG_INSTR']")
                    cloader.add_css('meet_dates', "[id^='MTG_DATE']")
                
                if selector.css("[id^='win0divSSR_CLS_DTL_WRK_GROUP2']"):          
                    cloader.add_css('add_consent', "[id^='PSXLATITEM_XLATLONGNAME']")
                    cloader.add_css('enrollement_req', "SSR_CLS_DTL_WRK_SSR_REQUISITE_LONG")

                if selector.css("[id^='ACE_SSR_CLS_DTL_WRK_GROUP6']"):          
                    cloader.add_css('description', "[id^='DERIVED_CLSRCH_DESCRLONG']")
                else:
                    continue

                loaded = copy.deepcopy(cloader)
                cloader = None
                yield loaded.load_item()

