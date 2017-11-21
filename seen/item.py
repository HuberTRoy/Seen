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

    def __init__(self, response):
        html = response.text
        self.result = {}
        self.response = response
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

    def __init__(self, response):
        self.response = response
        self.content = response.content

    def save(self):

        raise(TypeError('No save operation.'))


