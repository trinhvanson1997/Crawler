from selenium import webdriver
import scrapy
from scrapy import Selector
from time import sleep
import json


class SisSpider(scrapy.Spider):
    name = 'sis'
    start_urls = ['http://sis.hust.edu.vn/ModuleProgram/CourseLists.aspx']

    def __init__(self):
        self.driver = webdriver.Chrome('/usr/lib/chromedriver_linux64/chromedriver')
        self.number_pages = 50       #  số trang muốn crawl

    def parse(self, response):
        self.driver.get(response.url)
        i = 0
        while True:
            if i == self.number_pages:
                break

            try:
                print('CRAWLING PAGE ' + str(i + 1) + ' ....')
                self.parse_page(self.driver.page_source)    # crawl trang hiện tại
                print('CRAWLED PAGE ' + str(i+1))

                next_url = self.driver.find_element_by_class_name('dxWeb_pNext_SisTheme')
                next_url.click()    # sang trang tiếp theo
                i += 1

                sleep(1)
            except:
                break

    def parse_page(self, body):
        sel = Selector(text=body)   # chuyển từ text sang Selector
        table = sel.css('.dxgvTable_SisTheme')

        data_rows = table.css('.dxgvDataRow_SisTheme')

        number_subjects = len(data_rows)

        with open('sis2.json', 'a') as f:
            for i in range(number_subjects):
                data = data_rows[i].css('.dxgv::text').getall()
                btn_collapse = self.driver.find_elements_by_class_name('dxGridView_gvDetailCollapsedButton_SisTheme')
                if i == 0 or i == 1:
                    btn_collapse[0].click()
                else:
                    btn_collapse[i-1].click()

                sleep(0.5)

                detail = Selector(text=self.driver.page_source).css('.dxgvDetailCell_SisTheme b::text').getall()

                if len(detail) == 3:
                    condition_subject = None
                    english_name = detail[0]
                    short_name = detail[1]
                    faculity = detail[2]
                else:
                    condition_subject = detail[0]
                    english_name = detail[1]
                    short_name = detail[2]
                    faculity = detail[3]

                json_row = {
                    'ma_hoc_phan': data[0],
                    'ten_hoc_phan': data[1],
                    'thoi_luong': data[2],  # thoi luong
                    'so_tin_chi': data[3],  # so tin chi
                    'tc_hoc_phi': data[4],  # tin chi hoc phi
                    'trong_so': data[5],
                    'hoc_phan_dieu_kien': condition_subject,
                    'ten_tieng_anh': english_name,
                    'ten_viet-tat': short_name,
                    'vien_quan_ly': faculity
                }

                f.write(json.dumps(json_row, ensure_ascii=False))
                f.write('\n')


        f.close()
