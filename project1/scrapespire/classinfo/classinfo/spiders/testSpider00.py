import scrapy
import logging
from selenium import webdriver
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from scrapy.http import Request
from scrapy.shell import inspect_response

class testSpider00(scrapy.Spider):
    name = 'spire_login'
    login_url = 'https://www.spire.umass.edu/psp/heproda/?cmd=login&languageCd=ENG#'
    start_urls = [login_url]

    def parse(self, response):
        data = {'userid' : 'insert username',
                'pwd' : 'insert password',
            }
        yield scrapy.FormRequest(url = self.login_url, formdata = data, callback = self.after_login)

    def after_login(self, response):
        if 'Your User ID and/or Password are invalid.' in response.css('#login > p:nth-child(6)').extract_first(default='valid'):
            self.logger.error("Login Failed!")
            return
        else:
            return Request(url = 'https://www.spire.umass.edu/psp/heproda/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL?FolderPath=PORTAL_ROOT_OBJECT.HCCC_ACADEMIC_RECORDS.HC_SSS_STUDENT_CENTER&IsFolder=false&IgnoreParamTempl=FolderPath,IsFolder',
                            callback = self.parse_redirect)   

    def parse_redirect(self,response):
        studentcenter = response.selector.xpath('//*[@id="ptifrmtgtframe"]/@src').extract_first()
        return Request(url = studentcenter, callback = self.parse_classsearch)

    def parse_classsearch(self, response):
        driver = webdriver.Chrome('C:/Users/Kerry Ngan\Miniconda3/chromedriver.exe')
        classsearch = driver.find_element_by_name(response.selector.xpath('//*[@id="DERIVED_SSS_SCL_SSS_GO_4$83$"]/@name').extract_first())
        inspect_response(response, self)
        filename = 'spire.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)