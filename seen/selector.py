import re

from pyquery import PyQuery as pq


class Selector(object):
    """

    """

    def __init__(self, rule, attr=None):
        self.rule = rule
        self.attr = attr

    def __str__(self):
        return '<selector: {class_name} rule: {rule}>'.format(class_name=self.__class__.__name__, rule=self.rule)

    def __repr__(self):

        return str(self)

    def get_select(self, html):

        raise TypeError('No selector.')


class Css(Selector):

    def get_select(self, html):

        html = pq(html)
        if self.attr is None:
            try:
                return html(self.rule).text()
            except Exception as e:
                return None

        return [i.attr(self.attr) for i in html(self.rule).items()]


class Regex(Selector):

    def get_select(self, html):

        return re.findall(self.rule, html)
