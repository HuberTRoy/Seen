from seen import Item, BinItem, Css


class TestHtml:

    @property
    def text(self):
        return """
            <title> Test </title>
            <div class="testClass">
                <a href="http://test.com">A TEXT</a>
                <img src="http://test.png">
                <img src="http://test.jpg">
                <p>P TEXT</p>
            </div>     
            """


class TestJson:

    @property
    def text(self):
        return '{"testKey":"testValue"}'
    

class TestBinary:

    @property
    def content(self):
        return b'a binary data'
    

def test_item_parser():
    # test Html
    class TestItem(Item):

        title = Css('title')
        div_text = Css('.testClass')
        a_text = Css('a')
        a_href = Css('a', 'href')
        img_src = Css('.testClass img', 'src')

    test_result = TestItem(spider=None, response=TestHtml())

    # test define
    result = test_result.result
    assert 'title' in result
    assert 'div_text' in result
    assert 'a_text' in result
    assert 'a_href' in result
    assert 'img_src' in result

    # test result
    assert result['title'] == 'Test'
    assert result['a_text'] == 'A TEXT'
    assert type(result['a_href']) == list
    assert 'http://test.com' in result['a_href'] and isinstance(
        result['a_href'], list)
    assert 'http://test.png' in result['img_src'] and isinstance(
        result['img_src'], list)
    assert 'http://test.jpg' in result['img_src'] and isinstance(
        result['img_src'], list)


    # test Json
    class TestJsonItem(Item):
        pass

    test_result = TestJsonItem(spider=None, response=TestJson(), isJson=True)

    # test define
    result = test_result.result
    assert result.get('json') != None

    # test result
    json_data = result.get('json')
    assert json_data.get('testKey') == 'testValue'


    # test Binary data
    class TestBinaryItem(BinItem):

        pass

    test_result = TestBinaryItem(spider=None, response=TestBinary())

    # test define
    assert 'content' in test_result.__dict__

    # test result
    assert isinstance(test_result.content, bytes)