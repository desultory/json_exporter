from prometheus_exporter import Exporter, cached_exporter


@cached_exporter
class JSONExporter(Exporter):
    """ JSON exporter class for prometheus metrics. """
    def __init__(self, *args, **kwargs):
        kwargs['port'] = kwargs.pop('port', 9809)
        super().__init__(*args, **kwargs)

    def read_config(self):
        """ Override to read json.headers and json_endpoint from the config """
        super().read_config()
        if 'json' not in self.config:
            raise ValueError("No json config defined.")

        from .json_endpoint import JSONEndpoint
        self.endpoints = []
        # Iterate over each defined endpoint
        for endpoint_name, config in self.config['json'].items():
            self.endpoints.append(JSONEndpoint(name=endpoint_name,
                                               **config, logger=self.logger, _log_init=False))

    def get_labels(self):
        labels = super().get_labels()
        for endpoint in self.endpoints:
            labels |= endpoint.labels
        return labels

    def get_metrics(self, label_filter={}):
        """ Get metrics list from each endpoint, add them together """
        metric_list = []
        for endpoint in self.endpoints:
            self.logger.debug("Getting metrics from endpoint: %s", endpoint.name)
            endpoint.get_data(label_filter=label_filter)
            metric_list.extend(endpoint.metrics)
        return metric_list + super().get_metrics(label_filter=label_filter)
