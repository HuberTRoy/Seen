from seen import Spider, Parser, Item, Css


class Post(Item):
    title = Css('title')
    img = Css('img', 'src')


    def save(self):

        print(self.result['title'])
        print(self.result['img'])


class MySpider(Spider):
    roots = 'https://www.v2ex.com'
    url_limit = ('www.v2ex.com')
    concurrency = 1
    parsers = [Parser(Post)]


if __name__ == '__main__':
    spider = MySpider()

    spider.start()