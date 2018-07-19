class BrowserResponse:

    """
        url, text(HTML), cookies.
    """

    def __init__(self, url, text, cookies):
        self.url = url
        self.text = text
        self.cookies = cookies

    def __repr__(self):

        return 'Response [{}]'.format(self.url)


def emptyBrowserResponse(url):

    return BrowserResponse(url, text='<html><head></head><body></body></html>', cookies=[])
