
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
        self.logger.info("%s - - [%s] %s" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format % args))

    def do_GET(self):
        if self.path == '/metrics':
            self.logger.info("[%s:%d] Metrics request" % (*self.client_address,))
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(str(self.server).encode('utf-8'))
            return

        self.logger.warning("[%s:%d] Invalid url access attempt: %s" % (*self.client_address, self.path))
        self.send_response(404)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_POST(self):
        self.logger.warning("POST request attempted")
        self.send_response(501)
        self.send_header("Content-type", "text/html")
        self.end_headers()
