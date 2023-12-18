"""
Basic exporter class
"""

from http.server import ThreadingHTTPServer
from pathlib import Path

from zenlib.logging import loggify

from .labels import Labels
from .prometheus_request import PrometheusRequest


DEFAULT_IP = '127.0.0.1'
DEFAULT_PORT = 9809


@loggify
class Exporter(ThreadingHTTPServer):
    """
    Basic prometheus metric exporter class.
    Extends the ThreadingHTTPServer class.
    Forces use of the PrometheusRequest RequestHandlerClass.
    Reads a config.toml file to read the server port and ip.
    If 'ip' and 'port' are passed as kwargs, they will override the config file.
    """
    def __init__(self, config_file='config.toml', labels=Labels(), *args, **kwargs):
        self.labels = Labels(dict_items=labels, logger=self.logger, _log_init=False)
        self.config_file = Path(config_file)
        self.read_config()

        kwargs['RequestHandlerClass'] = PrometheusRequest
        ip = self.config['listen_ip'] if 'ip' not in kwargs else kwargs.pop('ip', DEFAULT_IP)
        port = self.config['listen_port'] if 'port' not in kwargs else kwargs.pop('port', DEFAULT_PORT)
        kwargs['server_address'] = (ip, port)

        super().__init__(*args, **kwargs)

    def __setattr__(self, name, value):
        if name == 'labels' and not isinstance(value, Labels):
            raise ValueError("Labels must be a dict.")
        super().__setattr__(name, value)

    def read_config(self):
        """ Reads the config file defined in self.config_file """
        from tomllib import load
        with open(self.config_file, 'rb') as config:
            self.config = load(config)

        self.logger.info("Read config file: %s", self.config_file)
        self.labels.update(self.config.get('labels', {}))

    def export(self):
        """ Go through ALL DEFINED metrics, turn them into a metric string for prometheus."""
        from .metric import Metric
        return '\n'.join(str(metric) for metric in Metric.metrics.values())
