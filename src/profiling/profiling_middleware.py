import io
import logging
import random
from pstats import Stats
from typing import Callable, List, Dict, Any, Union

from flask import Flask
from werkzeug.wsgi import ClosingIterator

try:
    from cProfile import Profile
except ImportError:
    from profile import Profile  # type: ignore


class ProfilingMiddleware(object):
    """
    Middleware that profiles each request with the cProfile.
    """
    logger = logging.getLogger(__name__)

    def __init__(self, app: Flask, rate: float, sort_by: Union[List[str], str]) -> None:
        """
        :param app: Flask application
        :param rate: Sampling rate, should be greater than 0.0
        :param sort_by: Sort ordering, valid options: 'stdname', 'calls', 'time', 'cumulative'
        """
        self.wsgi_app: Callable[..., ClosingIterator] = app.wsgi_app
        if isinstance(sort_by, str):
            sort_by = [sort_by]
        self.sort_by: List[str] = sort_by
        self.range = int(1 / rate)

    def __call__(self, environ: Dict[Any, Any], start_response: Callable[..., Any]) -> List[bytes]:
        response_body: List[bytes] = []

        def catching_start_response(status: str, headers: List[Any], exc_info: Any = None) -> Callable[..., None]:
            start_response(status, headers, exc_info)
            return response_body.append

        def runapp() -> None:
            app_iter = self.wsgi_app(environ, catching_start_response)
            response_body.extend(app_iter)

            if hasattr(app_iter, 'close'):
                app_iter.close()

        # check request headers contains "profile=1" header
        # or profile with sampling rate
        if environ.get('HTTP_PROFILE', '0') == '1' or random.randrange(0, self.range) == 0:
            with io.StringIO() as stream:
                method = environ.get('REQUEST_METHOD')
                path = environ.get('PATH_INFO') or '/'
                stream.write(f'Profile result of: {method} {path}\n')

                profile = Profile()
                profile.runcall(runapp)

                Stats(profile, stream=stream) \
                    .sort_stats(*self.sort_by) \
                    .print_stats(40)  # print only first 40 lines
                self.logger.warning(stream.getvalue())
        else:
            runapp()

        body = b''.join(response_body)
        return [body]
