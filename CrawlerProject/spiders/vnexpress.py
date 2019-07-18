import scrapy
import json
from datetime import datetime

class VnExpressSpider(scrapy.Spider):
    name = 'vnexpress'
    start_urls = [
                    # 'https://vnexpress.net/the-thao',
                    'https://vnexpress.net/giao-duc',
                    # 'https://vnexpress.net/thoi-su',
                    # 'https://vnexpress.net/the-gioi',
                    # 'https://vnexpress.net/kinh-doanh',
                    # 'https://vnexpress.net/giai-tri',
                    # 'https://vnexpress.net/phap-luat',
                    # 'https://vnexpress.net/suc-khoe',
                    # 'https://vnexpress.net/doi-song',
                    # 'https://vnexpress.net/du-lich',
                    # 'https://vnexpress.net/khoa-hoc',
                    # 'https://vnexpress.net/tam-su'
                ]

    def __init__(self):
        self.categories = {
            'the-thao': 'thể thao',
            'giao-duc': 'giáo dục',
            'thoi-su': 'thời sự',
            'the-gioi': 'thế giới',
            'kinh doanh': 'kinh doanh',
            'giai-tri': 'giải trí',
            'phap-luat': 'pháp luật',
            'suc-khoe': 'sức khỏe',
            'doi-song': 'đời sống',
            'du-lich': 'du lịch',
            'khoa-hoc': 'khoa học',
            'tam-su': 'tâm sự'
        }

        self.num_pages = 5  # Số trang cần crawl, mỗi trang có hơn 25 bài viết
        self.cur_page = 0
        self.current_category = None


    def parse(self, response):
        for v in self.categories.keys():
            if v in response.url:
                self.current_category = self.categories[v]
                break

        if self.cur_page < self.num_pages:
            list_news = response.css('.sidebar_1 .list_news')
            news_urls = set([v.css('.title_news a::attr(href)').get() for v in list_news])

            for url in news_urls:
                yield scrapy.Request(url=url, callback=self.parse_page)

            self.cur_page += 1

            next_url = response.css('.next::attr(href)').get()
            yield response.follow(next_url, self.parse)

    def parse_page(self, response):
        sentences = response.css('.content_detail p::text').getall()
        upload_time = response.css('.sidebar_1 .time::text').get()

        content = ' '.join(v for v in sentences)
        upload_time = upload_time[upload_time.index(',') + 2: upload_time.index('(') - 1]

        # upload_time = datetime.strptime(upload_time, '%d/%m/%Y, %H:%M')

        #  nếu là tin tức chỉ chứa video, bỏ qua
        if content != "":
            with open('vnex.json', 'a') as f:
                f.write(json.dumps({
                    'id': response.css('.myvne_save_for_later::attr(data-article-id)').get(),
                    'upload_time': upload_time,
                    'title': response.css('.title_news_detail::text').get().strip(),
                    'description': response.css('.description::text').get().strip(),
                    'content': content.strip(),
                    'url': response.url,
                    'category': self.current_category
                }, ensure_ascii=False))
                f.write(',\n')
            f.close()
