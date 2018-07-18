# -*- coding: utf-8 -*-

"""
This module contains an asynchronous method to send get and post http requests.

Use 'AsRequests' to send them.

Simple and effective.
:)

"""
import json
import logging
import asyncio

try:
    import requests
    noRequests = False
except ImportError:
    noRequests = True

try:
    import aiohttp
    import async_timeout
    noAiohttp = False
except ImportError:
    if noRequests:
        print('aiohttp and requests cannot be found.')
    else:
        noAiohttp = True

import chardet

from collections import namedtuple


logger = logging.getLogger(__name__)

__all__ = (
    'AsRequests'
)

ErrorRequest = namedtuple('ErrorRequest', 
                          ['url',
                          'text',
                          'content',
                          'code',
                          'error_info'])


class AioResult(object):
    
    def __init__(self, url, content, headers, cookies, code, encoding=None):
        self.url = url
        self.content = content
        self.header = headers
        self.cookies = cookies
        self.code = code
        self.encoding = encoding

    def __repr__(self):

        return '<Response [{code}]>'.format(code=self.code)

    @property
    def text(self):
        if not self.encoding:
            encoding = chardet.detect(self.content)['encoding']
            self.encoding = encoding
        else:
            encoding = self.encoding
            
        try:
            return str(self.content, encoding, errors='replace')
        except (LookupError, TypeError):
            return str(self.content, errors='replace')

    @property
    def json(self):
        return json.loads(self.text)


if not noRequests:
    class RequestsBase(object):
        session = requests.session()

        def __del__(self):
            self.session.close()

        def get(self, url, **kwargs):

            return self.session.get(url, **kwargs)

        def post(self, url, **kwargs):

            return self.session.post(url, **kwargs)


    BaseHttp = RequestsBase


if not noAiohttp:

    class AioRequestsBase(object):
        session = aiohttp.ClientSession()

        def __del__(self):
            if not self.session.closed:
                if self.session._connector_owner:
                    self.session._connector.close()
                self.session._connector = None

        async def request(self, method, url, **kwargs):
            cookies = kwargs.get('cookies')
            if cookies is not None:
                self.session._cookie_jar.update_cookies(cookies)
                kwargs.pop('cookies')

            content = b''
            method = method.upper()
            if method == 'GET':
                request = self.session.get
            elif method == 'POST':
                request = self.session.post
            else:
                raise(TypeError('Unknow method.'))

            if kwargs.get('timeout'):
                timeout = kwargs.pop('timeout')
                async with async_timeout.timeout(timeout):
                    async with request(url, **kwargs) as response:
                        content = await response.read()
            else:
                async with request(url, **kwargs) as response:
                    content = await response.read()

            if not content:
                return ErrorRequest(url=url,
                                                    text='',
                                                    content=content,
                                                    code='900',
                                                    error_info=str(response))

            return AioResult(url,
                content, 
                response.headers, 
                self.session.cookie_jar,
                response.status,
                encoding=kwargs.get('encoding'))

        def get(self, url, **kwargs):

            return self.request('GET', url, **kwargs)

        def post(self, url, **kwargs):
            return self.request('POST', url, **kwargs)


    BaseHttp = AioRequestsBase


class AsRequests(BaseHttp):
    """
    An async http requests.

    Accept parameters:

    :param callback: response callback. 
    :param callback default: lambda response: self.result.append(response)

    :param exceptionHandler: exception handling function. 
    :param exceptionHandler default: lambda exception: print(exception)
    
    :param callbackMode: The type of callback function.
    :param callbackMode accept:
        1(or != 2,3) : callback function is a normal function.
        2 : callback function has blocking codes.
        3 : callback function is an asynchronous function.

    Method and Coroutine Method:
        get
        post

    Usage::
        # normal.
        with AsRequests() as ar:
            for i in ['https://github.com']*5:
                ar.get(i)

        print(ar.result)
        
        # print error.
        with ar:
            for i in ['https://github.com']*5:
                ar.get(i, timeout=0.001)   

        print(ar.result)

        # with params.
        def showResponse(result):
            print(result)
            ....

        with AsRequests(callback=showResponse) as ar:
            for i in ['https://github.com']*5:
                ar.get(i)

        >>>
        # normal.
        [<Response [200]>, <Response [200]>, <Response [200]>, <Response [200]>, <Response [200]>]
        # error
        error information...
        [ErrorRequest(url='..', text='', ..), ErrorRequest(url='..', text='', ..), ...]
        # print result.
        <Response [200]>
        <Response [200]>
        <Response [200]>
        <Response [200]>
        <Response [200]>

    Coroutine Usage::
        import asyncio
        urls = ['https://github.com']*5
        
        arequests = AsRequests()
        
        # one.
        @asyncio.coroutine
        def getUrl(url, **kwargs):
            print('url: {0}'.format(url))
            result = yield from arequests.get(url, **kwargs)
            print('url: {0}, response: {1}'.format(url, result))

        eventLoop = asyncio.get_event_loop()
        # run.
        eventLoop.run_until_complete(asyncio.wait([getUrl(url) for url in urls]))
        
        # two.
        @asyncio.coroutine
        def getUrl(url, **kwargs):
            print('url: {0}'.format(url))
            result = yield from arequests.get(url, **kwargs)
            print('url: {0}, response: {1}'.format(url, result))
        
        for url in urls:
            # asyncio.ensure_future or eventLoop.create_task or asyncio.Task.
            asyncio.Task(getUrl(url))

        eventLoop = asyncio.get_event_loop()
        # run.
        eventLoop.run_forever()
        >>>
        url: https://github.com
        url: https://github.com
        ....
        url: https://github.com, response: <Response [200]>
        url: https://github.com, response: <Response [200]>
        ....
    """
    def __init__(self, callback=None, exceptionHandler=None, callbackMode=1):
        super().__init__()
        
        self.callbackMode = callbackMode

        # default callback result.
        self.tasks = []
        self.result = []

        self.callback = callback if callback else lambda response: self.result.append(response)

        # if callback function has blocking codes.
        self.blockingCallbackTasks = []

        self.blockingCallback = lambda response: self.result.append(response)

        # if callback function has asynchronous codes.
        self.asyncCallbackTasks = []
        
        self.asyncCallback = lambda response: self.asyncCallbackTasks.append(self.callback(response))
        
        # default exception handling function.
        self.exceptionHandler = exceptionHandler if exceptionHandler else lambda exception: logger.error('Get some error:', exc_info=True)

    def __enter__(self):

        # Initialize the tasks and result.
        self.tasks = []
        self.result = []

        # if callback function has blocking codes.
        self.blockingCallbackTasks = []

        # if callback function has asynchronous codes.
        self.asyncCallbackTasks = []

        return self

    def __exit__(self, except_type, value, tb):
        """
            Without manual setting.
        """
        self._executeTasks()

        return True

    def __repr__(self):
        """
            Return the session string and the tasks string.
        """

        return '<AsRequests: tasks: {tasks}>'.format(tasks=self.tasks)

    def _httpRequest(self, method, url, kwargs):
        method = method.upper()
        if method == 'GET':
            data = super().get(url, **kwargs)
        elif method == 'POST':
            data = super().post(url, **kwargs)

        return data

    @asyncio.coroutine
    def _aHttpRequest(self, method, url, kwargs):
        eventLoop = asyncio.get_event_loop()

        if not noAiohttp:
            future = self._httpRequest(method, url, kwargs)
        else:
            # it is still a thread. check out 'asyncio.base_event' getting more details.
            # check out this:
            # https://stackoverflow.com/questions/22190403/how-could-i-use-requests-in-asyncio
            # getting more explain.
            future = eventLoop.run_in_executor(None, self._httpRequest, method, url, kwargs)

        try:
            data = yield from future
        except Exception as e:
            data = ErrorRequest(url=url,
                                text='',
                                content=b'',
                                code='900',
                                error_info=e)
            self.exceptionHandler(e)
        finally:
            if self.callbackMode == 1:
                eventLoop.call_soon_threadsafe(self.callback, data)
            if self.callbackMode == 3:
                eventLoop.call_soon_threadsafe(self.asyncCallback, data)
            elif self.callbackMode == 2:
                eventLoop.call_soon_threadsafe(self.blockingCallback, data)

        return data       

    @asyncio.coroutine
    def _get(self, url, **kwargs):
        return self._aHttpRequest('GET', url, kwargs)

    @asyncio.coroutine
    def _post(self, url, **kwargs):
        return self._aHttpRequest('POST', url, kwargs)

    def _executeTasks(self):
        eventLoop = asyncio.get_event_loop()
        eventLoop.run_until_complete(asyncio.wait(self.tasks))

        newLoop = asyncio.new_event_loop()

        asyncio.set_event_loop(newLoop)
        if self.callbackMode == 3:
            newLoop.run_until_complete(asyncio.wait([asyncio.Task(_) for _ in self.asyncCallbackTasks]))
        elif self.callbackMode == 2:
            for i in self.result:
                future = newLoop.run_in_executor(None, self.callback, i)
                self.blockingCallbackTasks.append(asyncio.ensure_future(future))

            newLoop.run_until_complete(asyncio.wait(self.blockingCallbackTasks))

        asyncio.set_event_loop(eventLoop)

    def setCallback(self, func):
        self.callback = func

    def setExceptionHandler(self, func):
        self.exceptionHandler = func

    def get(self, url, **kwargs):
        """
        check out 'http://docs.python-requests.org/en/master/' getting help.
        """
        future = asyncio.ensure_future(self._get(url, **kwargs))
        self.tasks.append(future)

        return future

    def post(self, url, **kwargs):
        """
        check out 'http://docs.python-requests.org/en/master/' getting help.
        """
        future = asyncio.ensure_future(self._post(url, **kwargs))
        self.tasks.append(future)

        return future


asrequests = AsRequests()


if __name__ == '__main__':
    help(asrequests)
