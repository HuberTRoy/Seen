import json

from html import unescape

from .logger import logger
from .selector import Selector 


class BaseItem(type):

    def __new__(cls, name, bases, namespace):
        selector = {}
        for name, value in namespace.items():
            if isinstance(value, Selector):
                selector[name] = value
        
        namespace['selector'] = selector

        return type.__new__(cls, name, bases, namespace)


# get help of metaclass:
# https://stackoverflow.com/questions/100003/what-is-a-metaclass-in-python
class Item(metaclass=BaseItem):

    def __init__(self, spider, response, isJson=False):
        html = response.text
        self.result = {}
        self.spider = spider
        self.response = response
        if isJson:
            self.result['json'] = json.loads(html)
        else:
            html = unescape(html)

            for name, selector in self.selector.items():
                contents = selector.get_select(html)
                if contents is None:
                    logger.error('selector "{}:{}" was error, please check again.'.format(name, selector))
                    continue
                
                self.result[name] = contents

    def save(self):

        raise(TypeError('No save operation.'))


# save binary data.
class BinItem(object):

    def __init__(self, spider,  response):
        self.response = response
        self.spider = spider
        self.content = response.content

    def save(self):

        raise(TypeError('No save operation.'))


