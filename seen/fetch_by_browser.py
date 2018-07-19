import asyncio

from .browser_response import BrowserResponse, emptyBrowserResponse
from .logger import logger
try:
    from pyppeteer import launch
    from pyppeteer.errors import TimeoutError, NetworkError, PageError
except ImportError:
    logger.error('please install pyppeteer first.')


class Browser(object):
    """
        Return a launcher with totalPageNum page(s).
        
    """
    def __init__(self):

        self.browser = None

    async def launch(self):
        self.browser = await launch()

    async def fetch(self, url, **kwargs):
        try:
            max_tries = kwargs.pop('max_tries')
        except KeyError:
            # default 3
            max_tries = 3

        # Create a new page to load url.
        page = await self.browser.newPage()
        try:
            logger.info(f"try to get {url} by browser.")
            await page.goto(url, **kwargs)
            # break
        except TimeoutError:
            pass
        except PageError:
            return emptyBrowserResponse(url)

        # the TimeoutError not just occured when we cannot connect it.
        # for some reasons, it will also be happen when JavaScript not full load.
        # so we can also get the most page content.
        url = page.url
        for i in range(max_tries):
            try:
                text = await page.content()
                cookies = await page.cookies()
                break
            except NetworkError:
                # if timeout is too small, sometimes it will raise this error.
                try:
                    await page.reload(**kwargs)
                except TimeoutError:
                    pass
        else:
            await page.close()

            # text = <html><head></head><body></body></html>
            # means load failed.

            return emptyBrowserResponse(url)

        return BrowserResponse(url=url, text=text, cookies=cookies)    


    async def close(self):
        await self.browser.close()
