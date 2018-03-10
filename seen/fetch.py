from .asrequests import ErrorRequest

from .logger import logger


async def fetch_content(url, session, **kwargs):
    method = kwargs.get('method') or 'GET'
    if method == 'GET':
        response = await session.get(url, **kwargs)
    else:
        response = await session.post(url, **kwargs)
        
    if isinstance(response, ErrorRequest):
        logger.error("url {} is an error url, error information: {}".format(url, response.error_info))
        return None
        
    return response

