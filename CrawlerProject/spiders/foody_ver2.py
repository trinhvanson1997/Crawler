import scrapy
import requests
import json
import time

url_load_more = "https://www.foody.vn/__get/Review/ResLoadMore"
url_review_info = "https://www.foody.vn/__get/Review/GetReviewInfo"
url_list_home_page = "https://www.foody.vn/__get/Place/HomeListPlace"

headers = {
    'X-Requested-With': "XMLHttpRequest",
    'cache-control': "no-cache"
}


class FoodyVer2(scrapy.Spider):
    name = "foody2"

    start_urls = ["https://www.foody.vn/ha-noi"]

    def __init__(self):
        self.number_home_page = 1

    def parse(self, response):
        list_product_urls = self.get_list_product_urls()
        list_product_urls = set(list_product_urls)

        for v in list_product_urls:
            yield scrapy.Request(url=v, callback=self.parse_review_page)

    def parse_review_page(self, response):

        # lấy dữ liệu khởi tạo ban đầu của trang web, trong biến initDataView của thẻ script
        # có sẵn 10 review đầu tiên, trích chọn thành dạng json

        init_data = response.css('.micro-review-list .list-reviews script::text').get()
        try:
            init_data = init_data[init_data.index('{'):init_data.rindex('initDataReviews')]
            init_data = init_data[:init_data.rindex(';')]
            init_data = json.loads(init_data)
        except:
            print(init_data)

        # Lấy mã nhà hàng và id của review cuối cùng  (trong số các review đang xét)
        res_id = init_data['ResId']
        last_id = init_data['LastId']

        # Lấy ra tên thương hiệu
        brand_name = response.css('.main-info-title h1::text').get()

        # Lưu lại 10 review init
        self.save_data(brand_name, items=init_data['Items'])
        print('CRAWLING PAGE =====> ' + brand_name)
        self.more_review_page(res_id, last_id, brand_name)

    def get_list_product_urls(self):
        list_urls = []

        for i in range(self.number_home_page):
            t = str(int(time.time()))
            querystring = {"t": t, "page": i + 1, "count": "12", "type": "1"}
            res = requests.request("GET", url_list_home_page, headers=headers, params=querystring)

            items = json.loads(res.text)['Items']
            for item in items:
                list_urls.append('https://www.foody.vn' + item['Url'] + '/binh-luan')
        return list_urls

    def more_review_page(self, res_id, last_id, brand_name):
        """
        Lấy ra 10 review tiếp theo. Request này cần có tham số t: timestamp, ResId, LastId,
        Count: max là 10 bình luận tiếp theo, type mặc định là 1

        :param res_id: mã nhà hàng
        :param last_id:
        :param brand_name:
        :return:
        """

        # biến thời gian - định dạng timestamp
        t = str(int(time.time()))

        while True:
            try:
                querystring = {"t": t, "ResId": res_id, "LastId": last_id, "Count": "10", "Type": "1"}
                res = requests.request("GET", url_load_more, headers=headers, params=querystring)
                data = json.loads(res.text)

                # Nếu không tìm thấy bình luận nào tiếp theo dừng
                if len(data['Items']) == 0:
                    break

                items = data['Items']

                # cập nhập LastId để lấy ra 10 bình luận tiếp
                last_id = data['LastId']
                self.save_data(brand_name, items)
            except:
                break

    def save_data(self, brand_name, items):
        """
        Lưu các review vào file

        :param brand_name: tên thương hiệu
        :param items: danh sách các review đang xét
        :return:
        """

        with open('foody-data.json', 'a') as f:

            for item in items:
                # Lấy thông tin về số điểm đánh giá bằng cách gửi request tới url_review_info
                # kèm theo mã bình luận
                querystring = {"reviewId": item['Id']}

                res = None
                try:
                    res = requests.request("GET", url_review_info, headers=headers, params=querystring)
                    res = json.loads(res.text)
                except:
                    print(res.text)

                print(item['Owner']['DisplayName'])
                data = {
                    'brand_name': brand_name,
                    #'user_name': item['Owner']['DisplayName'],
                    #'user_link': 'https://www.foody.vn' + item['Owner']['Url'],
                    #'review_title': item['Title'],
                    'review_content': item['Description'],
                    #'review_link': 'https://www.foody.vn' + item['Url'],
                    #'avg_score': item['AvgRating'],
                    #'location_point': res['Position'],
                    #'price_point': res['Price'],
                    #'quality_point': res['Food'],
                    #'service_point': res['Services'],
                    #'space_point': res['Atmosphere']
                }
                f.write(json.dumps(data, ensure_ascii=False))
                f.write(',\n')
        f.close()
