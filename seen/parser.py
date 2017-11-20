import re
import asyncio
from html import unescape


from .logger import logger


class BaseParser(object):
    """
    :param rules: list[function(response)]/tuple(function(response)).
    :param item: Item. 
    """
    def __init__(self, rules=None, item=None, url_rule=None):

        self.rules = rules or []
        self.item = item

        if url_rule is None:
            url_rule = r'''(?i)href=["']([^\s"'<>]+)'''
        self.url_rule = url_rule

    def __call__(self, response):
        return self.analyze_response(response)

    def parse_item(self, html):
        item = self.item(html)
        return item

    def get_urls(self, html):
        urls = set(re.findall(self.url_rule, html))
        return urls

    async def analyze_response(self, response):
        text = response.text
        if any([i(text) for i in self.rules]):
            if self.item is not None: 
                item = self.parse_item(text)

                # TODO: if async or not.
                await item.save()

        return self.get_urls(text)


class Parser(BaseParser):
    """
        normal parser.

        base judge:

        if 'x' in response:

    """
    def __init__(self, rule=None, item=None, url_rule=None):
        super().__init__(rule and [lambda x: True if rule in x else False],
            item,
            url_rule)


class ReParser(BaseParser):
    """
        re parser.

        re judge:

        if re.match(rule, x) is not None:
            True
    """
    def __init__(self, rule=None, item=None, url_rule=None):
        super().__init__(rule and [lambda x: True if re.match(rule, x) else False],
            item,
            url_rule)
