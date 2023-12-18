"""
JSON exporter class
"""

from .exporter import Exporter


class JSONExporter(Exporter):
    """
    JSON exporter class for prometheus metrics.
    """
    endpoints = []

    def read_config(self):
        """ Override to read json.headers and json_endpoint from the config """
        super().read_config()
        if 'json' not in self.config:
            raise ValueError("No json config defined.")

        from .json_endpoint import JSONEndpoint
        # Iterate over each defined endpoint
        for endpoint_name, config in self.config['json'].items():
            self.endpoints.append(JSONEndpoint(name=endpoint_name,
                                               **config, logger=self.logger, _log_init=False))

    def __str__(self):
        """ Return a string representation of the exporter """
        for endpoint in self.endpoints:
            endpoint.get_data()
        return super().__str__()
