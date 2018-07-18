import asyncio

from .browser_response import BrowserResponse
from .logger import logger
try:
    from pyppeteer import launch
    from pyppeteer.errors import TimeoutError
except ImportError:
    logger.error('please install pyppeteer first.')


Queue = asyncio.Queue


async def get_browser():
    browser = await launch()

    return browser


async def fetch_content_by_browser(browser, url, **kwargs):
        # Get a free page.
        # page = await self.pages.get()
        page = await browser.newPage()
        try:
            logger.info(f"try to get {url}.")
            page.setDefaultNavigationTimeout(30500)
            await page.goto(url, **kwargs)
            # break
        except:
            pass

        # the TimeoutError not just occured when we cannot connect it.
        # for some reasons, it will also be happen when JavaScript not full load.
        # so we can also get the most page content.
        url = page.url
        text = await page.content()
        cookies = await page.cookies()

        await page.close()
        # page = await browser.newPage()
        # self.pages.put_nowait(page)
        # self.pages.task_done()
        return BrowserResponse(url=url, text=text, cookies=cookies)


# class Browser(object):
#     """
#         Return a launcher with totalPageNum page(s).
        
#     """
#     def __init__(self, totalPageNum=1):

#         self.browser = None
#         self.pages = Queue()
#         self.totalPageNum = totalPageNum

#     async def launch(self):
#         self.browser = await launch()
#         # for i in range(self.totalPageNum):
#         #     page = await self.browser.newPage()
#         #     self.pages.put_nowait(page)

#     async def fetch(self, url, **kwargs):
#         try:
#             max_tries = kwargs.pop('max_tries')
#         except KeyError:
#             # default 3
#             max_tries = 3

#         # Get a free page.
#         # page = await self.pages.get()
#         self.page = await self.browser.newPage()
#         try:
#             logger.info(f"try to get {url}.")
#             await self.page.goto(url, **kwargs)
#             # break
#         except TimeoutError:
#             pass

#         # the TimeoutError not just occured when we cannot connect it.
#         # for some reasons, it will also be happen when JavaScript not full load.
#         # so we can also get the most page content.
#         url = self.page.url
#         text = await self.page.content()
#         cookies = await self.page.cookies()

#         await self.page.close()
#         # page = await self.browser.newPage()
#         # self.pages.put_nowait(page)
#         # self.pages.task_done()
#         return BrowserResponse(url=url, text=text, cookies=cookies)    


#     async def close(self):
#         self.browser.close()
