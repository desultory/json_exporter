
from http.server import BaseHTTPRequestHandler
from zenlib.logging import loggify


@loggify
class PrometheusRequest(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        """ Pull logger from the server if it exists """
        from logging import Logger
        server = kwargs.get('server') if 'server' in kwargs else args[-1]
        if hasattr(server, 'logger') and isinstance(server.logger, Logger):
            self.logger = server.logger.getChild(self.__class__.__name__)

        super().__init__(*args, **kwargs)

    def log_message(self, format, *args):
        """
        Overriding the default log_message method to use the class logger
        """
        self.logger.debug("%s - - [%s] %s" %
                          (self.address_string(),
                           self.log_date_time_string(),
                           format % args))

    def _extract_params(self):
        """ Extracts the parameters from the request path """
        if '?' not in self.path:
            raise ValueError("No parameters in request path.")
        return dict([p.split('=') for p in self.path.split('?')[1].split('&')])

    def do_GET(self):
        if self.path != '/metrics' and not self.path.startswith('/metrics?'):
            self.send_error(404, '404')
            raise ValueError("[%s:%d] Invalid url access attempt: %s" % (*self.client_address, self.path))

        try:
            if self.path == '/metrics':
                self.logger.info("[%s:%d] Metrics request" % (*self.client_address,))
                response = self.server.export().encode('utf-8')

            if self.path.startswith('/metrics?'):
                params = self._extract_params()
                self.logger.info("[%s:%d] Metrics request with parameters: %s " % (*self.client_address, params))
                response = self.server.export(params).encode('utf-8')
        except ValueError as e:
            self.send_error(501, str(e))
            raise ValueError("Failed to fetch metrics: %s" % (e))

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-Length", len(response))
        self.end_headers()
        self.wfile.write(response)

    def do_POST(self):
        self.logger.warning("POST request attempted")
        self.send_response(501)
        self.send_header("Content-type", "text/html")
        self.end_headers()
