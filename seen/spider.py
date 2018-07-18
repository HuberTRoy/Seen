import re
import asyncio

from collections import MutableMapping

from .asrequests import asrequests

from .logger import logger
from .fetch import fetch_content

try:
    from .fetch_by_browser import get_browser, fetch_content_by_browser
    Browser = True
except ImportError:
    Browser = False

Queue = asyncio.Queue
# requests = AsRequests()


class Spider(MutableMapping):
    roots = ''
    # url_limit:
    # if url in url_limit:
    #      continue
    # else:
    #      pass this url.
    url_limit = set()
    parsers = []
    error_urls = set()

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'
    }
    cookies = {}
    concurrency = 3
    max_tries = 4
    timeout = 3.05
    interval = 0
    work_queue = Queue()
    seen_url = set()
    # save
    state = {}

    # load JavaScript.
    # True to startup.
    # False by default.
    use_browser = False

    def __init__(self):
        self.session = asrequests
        if isinstance(self.roots, str):
            logger.info('get root url: {}'.format(self.roots))
            self.work_queue.put_nowait(self.roots)
        else:
            for root in self.roots:
                logger.info('get root url: {}'.format(root))
                self.work_queue.put_nowait(root)

        # given .spider attribute for parser.
        for parser in self.parsers:
            parser.spider = self

    def __setitem__(self, key, value):
        self.state[key] = value

    def __getitem__(self, key):
        return self.state.get(key)

    def __delitem__(self, key):
        del self.state[key]

    def __iter__(self):
        return iter(self.state)

    def __len__(self):
        return len(self.state)

    def add_roots(self, roots: iter):
        for root in roots:
            logger.info('Got root URL: {}'.format(root))
            self.work_queue.put_nowait(root)

    def add_parsers(self, parsers: iter):
        for parser in parsers:
            logger.info('Got root URL: {}'.format(root))
            self.work_queue.put_nowait(root)

    def get_host(self, url):
        host = re.search(r'://(.*?)/', url)
        if not host:
            host = re.search(r'://(.*)', url)

        if not host:
            return ''

        return host.group(1)

    def _add_url_to_workqueue(self, urls: iter):
        for i in urls:
            self.work_queue.put_nowait(i)

    def _check_url(self, url):
        if url in self.seen_url:
            return False

        if 'http' not in url:
            logger.info('This is an invalid URL: {}'.format(url))
            return False

        if self.url_limit:
            host = self.get_host(url)
            if not host:
                logger.info(
                    'This URL ({}) cannot get its host, please check again'.format(url))
                return False

            if host not in self.url_limit:
                logger.info('This URL ({}) out of the url_limit'.format(url))
                return False

        return True

    async def init_browser(self):
        if Browser is False:
            logger.error("please install pyppeteer correctly and try again.")
            exit("No pyppeteer.")

        # browser = Browser(totalPageNum=self.concurrency)

        logger.info("launch browser, please wait..")
        try:
            browser = await get_browser()
            # await browser.launch()
        except:
            # accurate error will be set later.
            logger.error("failed to launch browser, please try again", exc_info=True)
            exit("browser launch failure")

        self.state['browser'] = browser

    async def url_failed_handler(self, url):
        """
            Do something with the URL that connected failure.
            Should be override.
        """
        await asyncio.sleep(0)

    async def init_spider(self):
        """
            Should be override.
            if browser is True then startup browser.
        """
        if self.use_browser:
            await self.init_browser()
        await asyncio.sleep(0)

    async def _parse_content(self, response):
        # parse response's content.
        new_urls = []
        for parser in self.parsers:
            urls = await parser(response)
            new_urls.extend(urls)

        return new_urls

    async def _fetch_url(self, url):
        for i in range(self.max_tries):
            response = await fetch_content(url, 
                self.session, headers=self.headers, timeout=self.timeout, cookies=self.cookies)
            # return None if failed.
            if response is None:
                logger.info(
                    'Got None when requested this URL ({}), retring...'.format(url))
                continue

            return response
        else:
            await self.url_failed_handler(url)
            return None

    async def _fetch_url_by_browser(self, url, **kwargs):
        # return BrowserResponse
        # url text(HTML) cookies.
        browser = self.state.get('browser')
        kwargs['max_tries'] = self.max_tries
        # ms
        # kwargs['timeout'] = self.timeout * 1000
        kwargs['cookies'] = self.cookies

        response = await fetch_content_by_browser(browser, url, **kwargs)
        if response.text == '<html><head></head><body></body></html>':
            await self.url_failed_handler(url)
            return None

        return response

    async def _parse_response(self, response):
        # parse response using _parse_content.
        if response:
            new_urls = await self._parse_content(response)
            self._add_url_to_workqueue(new_urls)
            logger.info('URL {} checked over.'.format(response.url))
            return True

        return False

    async def work(self):
        # 1. Get URL from work_queue
        # 2. Check whether the URL is corresponded.
        # 3. Fetch content of this URL and parse it.
        # 4. Add this URL to `seen` list.
        # 5. Sleep `interval` seconds.
        # 6. Again or Done.
        try:
            while True:
                url = await self.work_queue.get()
                logger.info('Getting URL: {}'.format(url))

                # Check whether the URL is corresponded.
                if not self._check_url(url):
                    self.work_queue.task_done()
                    continue

                # use browser or not.
                if self.use_browser:
                    _fetch = self._fetch_url_by_browser
                else:
                    _fetch = self._fetch_url

                parse_result = await self._parse_response(await _fetch(url))

                if not parse_result:
                    # this url cannot be open.
                    self.error_urls.add(url)
                    self.work_queue.task_done()
                    continue

                # all done.
                self.seen_url.add(url)
                self.work_queue.task_done()
                await asyncio.sleep(self.interval)

        except asyncio.CancelledError:
            pass

    async def crawl(self):
        logger.info('Start spider.')
        logger.info('Execute initialization.')
        try:
            await self.init_spider()
        except TypeError:
            logger.error(
                "Got some error information it seems because 'init_spider' is not an async function.", exc_info=True)

        logger.info('Initialization finished.')

        logger.info("Start work.")
        workers = [asyncio.Task(self.work()) for _ in range(self.concurrency)]
        asyncio.gather(*workers)

        await self.work_queue.join()

        for i in workers:
            i.cancel()

        if self.use_browser:
            await self.state.get('browser').close()

        logger.info("Gathering information...")
        logger.info("Error urls: {}".format(len(self.error_urls)))
        logger.info("Spider finished.")

    def start(self):
        try:
            event_loop = asyncio.get_event_loop()
            event_loop.run_until_complete(self.crawl())
        except KeyboardInterrupt:
            event_loop.run_until_complete(self.state.get('browser').close())

            for task in asyncio.Task.all_tasks():
                task.cancel()
                event_loop.run_forever()
        finally:
            event_loop.close()
