import re
import asyncio
from html import unescape


from .logger import logger
from .item import BinItem


class BaseParser(object):
    """
    :param rules: list[function(response)]/tuple(function(response)).
    :param item: Item. 
    :param url_rule: str or function.
                    if it is a str will use re.findall(url_rule, response.text)
                    if it is a function will use url_rule(response.text), the function expects returning an iterable object that contains URL.
                    By default it is r'''(?i)href=["']([^\s"'<>]+)'''.
    """
    def __init__(self, url_rule=None, item=None, rules=None, isJson=False):
        # which spider own it.
        self.spider = None

        self.rules = rules or []
        self.item = item
        self.isJson = isJson

        if url_rule is None:
            url_rule = r'''(?i)href=["']([^\s"'<>]+)'''

        self.url_rule = url_rule

    def __call__(self, response):
        return self.analyze_response(response)

    def parse_item(self, response):
        item = self.item(self.spider, response, self.isJson)
        return item

    def get_urls(self, html):
        if self.isJson:
            return {}

        if isinstance(self.url_rule, str):
            urls = set(re.findall(self.url_rule, html))
        else:
            urls = set(self.url_rule(html))
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
                        logger.error("Get some error when tried to save data, it seems because `item.save()` is not an async function.")
                    else:
                        logger.error("Get some error when tried to save data, please check again, this is the error information:", exc_info=True)

        if issubclass(self.item, BinItem):
            return set()

        return self.get_urls(response.text)


class Parser(BaseParser):
    """
        normal parser.

        base judge:

        if rule in response.text:

    """
    def __init__(self, item=None, url_rule=None, rule=None, isJson=False):
        super().__init__(
            url_rule,
            item,
            rule and [lambda response: True if rule in response.text else False],
            isJson)


class ReParser(BaseParser):
    """
        re parser.

        re judge:

        if re.search(rule, response.text) is not None:
            True
    """
    def __init__(self, url_rule=None, item=None, rule=None, isJson=False):
        super().__init__(
            url_rule,
            item,
            rule and [lambda response: True if re.search(rule, response.text) else False],
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

        FuncParser([function, function2])
                
    """
    def __init__(self, url_rule=None, item=None,  rule:iter=None, isJson=None):
        super().__init__(
            url_rule, 
            item,
            rule,
            isJson)

