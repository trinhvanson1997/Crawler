from selenium import webdriver
import scrapy
from scrapy import Selector
import requests

import json
from time import sleep


class FoodySpider(scrapy.Spider):
    name = "foody"

    start_urls = ["https://www.foody.vn/ha-noi"]

    # start_urls = ["https://www.foody.vn/ha-noi/mokchang-do-an-han-quoc/binh-luan"]

    def __init__(self):
        self.driver = webdriver.Chrome('/home/sontrinh/projects/NewProject/chromedriver')

    def parse(self, response):

        # self.driver.get(response.url)
        # while True:
        #     try:
        #         next_url = self.driver.find_element_by_class_name('fd-btn-more')
        #         next_url.click()
        #         sleep(0.2)
        #     except:
        #         break
        with open('foody.html', 'w') as f:
            f.write(response.text)
        f.close()
        # self.parse_page(body=self.driver.page_source)
        # self.driver.close()


    def parse_page(self, body):
        res = Selector(text=body)
        review_list = res.css('.review-list')[0]

        with open('data.json', 'a') as f:

            for rv in review_list.css('.review-item'):

                data = {
                    'person_name': rv.css('.ru-username::text').get(),
                    'datetime': rv.css('.ru-time::text').get(),
                    'title': rv.css('.rd-title::text').get(),
                    'content': rv.css('.rd-des span::text').get(),
                    'point': rv.css('.review-points span::text').get(),
                }
                f.write(json.dumps(data, ensure_ascii=False))
                f.write('\n')
        f.close()