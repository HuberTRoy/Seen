import asyncio

from seen import *


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
    # use browser to load all URLs.
    use_browser = True
    timeout = 30
    parsers = [Parser(Post)]


if __name__ == '__main__':
    sp = MySpider()

    sp.start()