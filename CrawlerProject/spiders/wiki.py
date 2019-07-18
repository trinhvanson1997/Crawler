import scrapy
from scrapy.crawler import CrawlerProcess
import numpy as np
from scipy.sparse import csc_matrix
import pickle

# create list contain dicts {url_web_wiki: list_url}
wiki_pages = {}
list_title = {}
node = 1


class TestSpider(scrapy.Spider):
    name = 'test'
    start_urls = [
        'https://vi.wikipedia.org/wiki/Kh%C3%A1_B%E1%BA%A3nH'
    ]

    def parse(self, response):
        global wiki_pages
        global list_title
        global node

        yield {
            'url': response.request.url,
            'title': response.xpath("//title/text()").extract_first()
        }

        list_page = response.xpath("//a[starts-with(@href,'/wiki') and not(contains(@href,':'))]/@href").extract()

        key = response.request.url.replace("https://vi.wikipedia.org", "")
        wiki_pages[key] = list_page
        list_title[key] = response.css('.firstHeading::text').get()

        # for link in list_page:
        #     if (link.startswith('/wiki/')):
        #         print("https://en.wikipedia.org" + link)
        #         nodes = nodes + 1
        if (list_page is not None) and node < 500:
            node = node + len(list_page)
            for next_page in list_page:
                yield response.follow(next_page, callback=self.parse)


def pageRank(G, s=.85, maxerr=.0001):
    """
    Computes the pagerank for each of the n states
    Parameters
    ----------
    G: matrix representing state transitions
       Gij is a binary value representing a transition from state i to j.
    s: probability of following a transition. 1-s probability of teleporting
       to another state.
    maxerr: if the sum of pageranks between iterations is bellow this we will
            have converged.
    """
    n = G.shape[0]

    # transform G into markov matrix A
    A = csc_matrix(G, dtype=np.float)
    rsums = np.array(A.sum(1))[:, 0]
    ri, ci = A.nonzero()
    A.data /= rsums[ri]

    # bool array of sink states
    sink = rsums == 0

    # Compute pagerank r until we converge
    ro, r = np.zeros(n), np.ones(n)
    while np.sum(np.abs(r - ro)) > maxerr:
        ro = r.copy()
        # calculate each pagerank at a time
        for i in range(n):
            # inlinks of state i
            Ai = np.array(A[:, i].todense())[:, 0]
            # account for sink states
            Di = sink / float(n)
            # account for teleportation to state i
            Ei = np.ones(n) / float(n)

            r[i] = ro.dot(Ai * s + Di * s + Ei * (1 - s))

    # return normalized pagerank
    return r / float(sum(r))



def build_matrix(wiki_pages):
    nodes = []

    for key in list(wiki_pages.keys()):
        if key not in nodes:
            nodes.append(key)

    for value in list(wiki_pages.values()):
        for v in value:
            if v not in nodes:
                nodes.append(v)

    nodes = nodes[:500]
    value_nodes = [list_title[v] for v in nodes]

    f = open('titles.pickle', 'wb')
    pickle.dump(value_nodes, f)

    size = len(nodes)

    matrix = np.zeros(shape=(size, size), dtype=np.int32)

    for i in range(size):
        cur_page = nodes[i]
        for j in range(size):

            if i == j:  # 2 trang web trùng tên, bỏ qua
                continue

            try:
                list_urls = wiki_pages[cur_page]
                if nodes[j] in list_urls:
                    matrix[i][j] = 1
            except:
                continue
    return matrix
    # np.save('matrix500.npy', matrix)


if __name__ == '__main__':
    # os.remove('result.json')
    f = open('titles.pickle', 'rb')
    data = pickle.load(f)

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    })

    process.crawl(TestSpider)
    process.start()
    #
    # wiki_pages = {'1': ['2', '3'],
    #               '3': ['4', '7'],
    #               '4': ['1', '2']}

    matrix = build_matrix(wiki_pages)

    print(pageRank(matrix))
