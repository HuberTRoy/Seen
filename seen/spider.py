import re
import asyncio

from .asrequests import asrequests

from .logger import logger
from .fetch import fetch_content


Queue = asyncio.Queue
# requests = AsRequests()


class Spider:
    roots = ''
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
    work_queue = Queue()
    seen_url = set()

    def __init__(self):

        self.session = asrequests
        if isinstance(self.roots, str):
            logger.info('get root url: {}'.format(self.roots))
            self.work_queue.put_nowait(self.roots)
        else:
            for root in self.roots:
                logger.info('get root url: {}'.format(root))
                self.work_queue.put_nowait(root)

    def get_host(self, url):
        host = re.search(r'://(.*?)/', url)
        if not host:
            host = re.search(r'://(.*)', url)

        if not host:
            return ''

        return host.group(1)

    async def work(self):
        try:
            while 1:
                url = await self.work_queue.get()
                
                if url in self.seen_url:
                    self.work_queue.task_done()
                    continue

                # 
                if 'http' not in url:
                    logger.info('This is an invalidURL: {}'.format(url))
                    self.work_queue.task_done()
                    continue
                
                logger.info('Getting url: {}'.format(url))
                
                host = self.get_host(url)

                if self.url_limit:
                    if not host:
                        logger.info('This url({}) cannot get host, please check again'.format(url))
                        self.work_queue.task_done()
                        continue

                    if host not in self.url_limit:
                        logger.info('This url({}) out of the url_limit'.format(url))
                        self.work_queue.task_done()
                        continue

                for i in range(self.max_tries):
                    response = await fetch_content(url, self.session, headers=self.headers, timeout=self.timeout, cookies=self.cookies)
                    if response is None:
                        logger.info('This url({}) get some error, retring...'.format(url))
                        continue

                    new_urls = []
                    for parser in self.parsers:
                        urls = await parser(response)
                        new_urls.extend(urls)

                    logger.info('url {} has finished.'.format(url))
                    break
                else:
                    self.error_urls.add(url)
                    self.work_queue.task_done()
                    continue

                self.seen_url.add(url)
                
                for i in new_urls:
                    self.work_queue.put_nowait(i)

                self.work_queue.task_done()

        except asyncio.CancelledError:
            pass

    async def crawl(self):
        logger.info('Spider start.')
        workers = [asyncio.Task(self.work()) for _ in range(self.concurrency)]
        asyncio.gather(*workers)

        await self.work_queue.join()

        for i in workers:
            i.cancel()
        
        logger.info("Error urls: {}".format(len(self.error_urls)))
        logger.info("Spider finished.")

    def start(self):
        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(self.crawl())