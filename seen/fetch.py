from .asrequests import ErrorRequest

from .logger import logger


async def fetch_content(url, session, **kwargs):
    method = kwargs.get('method') or 'GET'
    response = await session.get(url, **kwargs)

    if isinstance(response, ErrorRequest):
        logger.error("url {} error, error information: {}".format(url, response.error_info))
        return None
        
    return response

