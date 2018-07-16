import json

from html import unescape

from .logger import logger
from .selector import Selector


class BaseItem(type):
    """
        The meta class for item.
    """
    def __new__(cls, name, bases, namespace):
        selector = {}
        for name, value in namespace.items():
            if isinstance(value, Selector):
                selector[name] = value

        namespace['selector'] = selector

        return type.__new__(cls, name, bases, namespace)


# Get help of metaclass:
# https://stackoverflow.com/questions/100003/what-is-a-metaclass-in-python
class Item(metaclass=BaseItem):
    """
      class MyItem(Item):
        # css rule
        title = Css('title')

        # asynchronous or synchronize
        def save(self):
            print(self.title)
    """

    def __init__(self, spider, response, isJson=False):
        self.html = response.text
        self.result = {}
        self.spider = spider
        self.response = response
        if isJson:
            try:
                self.result['json'] = json.loads(self.html)
            except:
                logger.error("The JSON contents returned by URL ({}) loaded failure, please check again.".format(
                    response.url), exc_info=True)
        else:
            self.html = unescape(self.html)

            for name, selector in self.selector.items():
                contents = selector.get_select(self.html)
                if contents is None:
                    logger.error('selector "{}:{}" was error, please check again.'.format(
                        name, selector), exc_info=True)
                    continue

                self.result[name] = contents

    def save(self):

        raise(TypeError('No save operation.'))


# save binary data.
class BinItem(object):

    def __init__(self, spider, response):
        self.response = response
        self.spider = spider
        self.content = response.content

    def save(self):

        raise(TypeError('No save operation.'))
