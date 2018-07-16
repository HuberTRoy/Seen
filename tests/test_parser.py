from seen import Item, Parser, Css


class TestHtml:

    url = 'https://test.com/testFolder/test.html'

    @property
    def text(self):
        return """
            <title> Test </title>
            <div class="testClass">
                <a href="http://test.com">A TEXT</a>
                <a href="/test?id=1">Test One</a>
                <a href="test?id=2">Test Two</a>
                <p>P TEXT</p>
            </div>     
            """


def test_parser():
    class TestItem(Item):
        title = Css('title')
        p = Css('p')

    # test item
    t_parser = Parser(item=TestItem)

    parser_item = t_parser.parse_item(TestHtml())

    assert parser_item.result == {'title': 'Test', 'p': 'P TEXT'}

    # test url
    new_urls = t_parser.get_urls(TestHtml().text, TestHtml.url)

    assert sorted(new_urls) == sorted(
        ('http://test.com', 'https://test.com/test?id=1', 'https://test.com/testFolder/test?id=2'))
