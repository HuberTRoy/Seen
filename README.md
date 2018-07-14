## Seen

Seen is a lightweight web crawling framework for everyone.
Written with `asyncio`，`aiohttp/requests`.

It is useful for writting a web crawling quickly.

**Working Process:**
![workingProcess](https://github.com/HuberTRoy/seen/blob/master/img/process.png)


## Requirements:
* Python 3.5+
* aiohttp or requests
* pyquery

## Installation:
```
pip install seen
```

## Usage:

1. Write spider.py
```
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
```

2. Run `python spider.py`.
3. Check result.

## Contribution

* Pull request.
* Open an issue.