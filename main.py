from scrapy import cmdline
import requests

cmdline.execute("scrapy crawl vnexpress".split())

# data = open('/home/sontrinh/projects/NewProject/vn.json','r').readlines()
# data[-1][-2] = ']'
# print(data[-1][-2])

