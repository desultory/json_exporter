"""
Basic exporter class
"""

from http.server import ThreadingHTTPServer
from pathlib import Path

from zenlib.logging import loggify

from .labels import Labels
from .prometheus_request import PrometheusRequest


@loggify
class Exporter(ThreadingHTTPServer):
    """
    Basic prometheus metric exporter class.
    Extends the ThreadingHTTPServer class.
    """
    def __init__(self, config_file='config.toml', labels=Labels(), *args, **kwargs):
        self.labels = Labels(dict_items=labels, logger=self.logger, _log_init=False)
        self.config_file = Path(config_file)
        self.read_config()

        kwargs['RequestHandlerClass'] = PrometheusRequest
        kwargs['server_address'] = (self.config['listen_ip'], self.config['listen_port'])
        super().__init__(*args, **kwargs)

    def __setattr__(self, name, value):
        if name == 'labels' and not isinstance(value, dict):
            raise ValueError("Labels must be a dict.")

        super().__setattr__(name, value)

    def read_config(self):
        """ Reads the config file defined in self.config_file """
        from tomllib import load
        with open(self.config_file, 'rb') as config:
            self.config = load(config)

        self.logger.info("Read config file: %s", self.config_file)
        self.labels.update(self.config.get('labels', {}))

    def __str__(self):
        """ Go through all metrics, turn them into a metric string for prometheus """
        from .metric import Metric
        return '\n'.join(str(metric) for metric in Metric.metrics.values())
