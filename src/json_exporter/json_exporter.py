from prometheus_exporter import Exporter
from asyncio import TaskGroup


class JSONExporter(Exporter):
    """ JSON exporter class for prometheus metrics. """
    def __init__(self, *args, **kwargs):
        self.endpoints = []
        kwargs['listen_port'] = kwargs.pop('listen_port', 9809)
        super().__init__(*args, **kwargs)

    def read_config(self):
        """ Ensure JSON config is defined, use that to define endpoints, which will then read the config. """
        super().read_config()
        if 'json' not in self.config:
            raise ValueError("No json config defined.")

        from .json_endpoint import JSONEndpoint
        # Iterate over each defined endpoint
        for endpoint_name in self.config['json']:
            self.endpoints.append(JSONEndpoint(name=endpoint_name, config_file=self.config_file,
                                               logger=self.logger, _log_init=False))

    def get_labels(self):
        """ Get labels from each endpoint, add them together """
        labels = self.labels.copy()
        for endpoint in self.endpoints:
            labels |= endpoint.labels
        return labels

    async def get_metrics(self, label_filter={}):
        """ Get metrics list from each endpoint, add them together """
        metric_list = await super().get_metrics(label_filter=label_filter)

        async with TaskGroup() as tg:
            for endpoint in self.endpoints:
                self.logger.debug("Creating data task for: %s", endpoint.name)
                tg.create_task(endpoint.get_metrics(label_filter=label_filter))

        for endpoint in self.endpoints:
            if metrics := getattr(endpoint, 'metrics', None):
                metric_list += metrics

        self.logger.debug("Got %d metrics", len(metric_list))
        self.metrics = metric_list
        return metric_list
