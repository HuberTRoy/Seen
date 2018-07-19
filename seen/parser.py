import re
import asyncio
from html import unescape
from urllib.parse import urljoin, urlparse

from .logger import logger
from .item import BinItem


class BaseParser(object):
    """
    :param rules: list[function(response)]/tuple(function(response)). 
                  To judge the Url is wanted to be or None to parse all Urls. None by default.
    :param item: Item. 
    :param urlRule: str or function.
                    if it is a str will use re.findall(urlRule, response.text)
                    if it is a function will use urlRule(response.text), the function expects returning an iterable object that contains URL.
                    By default it is r'''(?i)href=["']([^\s"'<>]+)'''.
    """

    def __init__(self, urlRule=None, item=None, rules=None, isJson=False):
        # which spider own it.
        self.spider = None

        self.rules = rules or []
        self.item = item
        self.isJson = isJson

        if urlRule is None:
            urlRule = r'''(?i)href=["']([^\s"'<>]+)'''

        self.urlRule = urlRule

    def __call__(self, response):
        return self.analyze_response(response)

    def parse_item(self, response):
        item = self.item(self.spider, response, self.isJson)
        return item

    def _partial_url_or_not(self, url):
        if re.match('(http|https)://', url):
            return False
        return True

    def parse_partial_url_to_full(self, partialUrl, baseUrl):
        if self._partial_url_or_not(partialUrl):
            # //cdn.xxx.com/avator/2.jpg
            # to http://cdn.xxx.com/avator/2.jpg
            if partialUrl.startswith('//'):
                return urljoin('http:', partialUrl)
            # /item?abc=123
            # to http://root/item?abc=123
            elif partialUrl.startswith('/'):
                parse_base_url = urlparse(baseUrl)
                return urljoin('{}://{}'.format(parse_base_url.scheme, parse_base_url.netloc), partialUrl)
            # item?abc=123
            # to http://root/toor/item?abc=123
            else:
                # http://root/toor/xxx.yyy
                # to http://root/toor/
                baseUrl = baseUrl[:baseUrl.rfind('/')+1]
                return urljoin(baseUrl, partialUrl)
        return partialUrl

    def get_urls(self, html, baseUrl=''):
        if self.isJson:
            return {}

        if isinstance(self.urlRule, str):
            urls = set(re.findall(self.urlRule, html))
        else:
            urls = set(self.urlRule(html))

        urls = (self.parse_partial_url_to_full(i, baseUrl) for i in urls)

        return urls

    async def analyze_response(self, response):
        if any([i(response) for i in self.rules]) or not self.rules:
            if self.item is not None:
                item = self.parse_item(response)
                try:
                    # whether it is async function or not, it will be run
                    # the difference between them is normal function will raise a TypeError.
                    # For example:
                    # def save():
                    #      print('save me!')
                    # will raise `TypeError: object NoneType can't be used in 'await' expression` but will also output "save me".
                    #
                    await item.save()
                except Exception as e:
                    if 'await' in str(e):
                        logger.error(
                            "Got some error when tried to save data, it seems because `item.save()` is not an async function.")
                    else:
                        logger.error(
                            "Got some error when tried to save data, please check again, this is the error information:", exc_info=True)

        if issubclass(self.item, BinItem):
            return set()

        return self.get_urls(response.text, response.url)


class Parser(BaseParser):
    """
        normal parser.

        base judge:

        if rule in response.text:

    """

    def __init__(self, item=None, urlRule=None, rule=None, isJson=False):
        super().__init__(
            urlRule,
            item,
            rule and [lambda response: True if rule in response.text else False],
            isJson)


class ChromeParser(BaseParser):
    """
        Chrome parser use headless chrome/chromium browser to run JavaScript code.
        It depends on pyppeteer and request
    """


class ReParser(BaseParser):
    """
        re parser.

        re judge:

        if re.search(rule, response.text) is not None:
            True
    """

    def __init__(self, urlRule=None, item=None, rule=None, isJson=False):
        super().__init__(
            urlRule,
            item,
            rule and [lambda response: True if re.search(
                rule, response.text) else False],
            isJson)


class FuncParser(BaseParser):
    """
        function parser.
        use function judge:
        def function(response):
            if response.url == 'https://github.com':
                return True
            return False

        def function2(response):
            if 'google' in response.url:
                return True
            return False

        FuncParser(rule=[function, function2])

    """

    def __init__(self, urlRule=None, item=None,  rule: iter=None, isJson=None):
        super().__init__(
            urlRule,
            item,
            rule,
            isJson)
