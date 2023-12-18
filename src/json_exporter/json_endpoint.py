"""
Defines the JSON endpoint for the JSON exporter
"""

from zenlib.logging import loggify


@loggify
class JSONEndpoint:
    """
    Defines the JSON endpoint for the JSON exporter
    """
    endpoints = {}

    def __init__(self, name, *args, **kwargs):
        """
        Initializes the JSON endpoint
        """
        if name in self.endpoints:
            raise ValueError("JSON endpoint already exists: %s" % name)
        self.name = name
        self.metrics = []
        self.parse_kwargs(kwargs)

    def get_labels(self):
        """ Returns the labels for the JSON endpoint """
        labels = self.labels.copy()
        labels.update(self.json_labels)
        return labels

    def parse_kwargs(self, kwargs):
        """
        Parses the kwargs passed during initialization.
        Makes the intitial JSON request, to be used for json_labels.
        Adds all metrics to self.metrics.
        """
        from .labels import Labels

        self.endpoint = kwargs.pop('endpoint')
        self.headers = kwargs.pop('headers', {})
        self.json_paths = kwargs.pop('json_labels', {})
        self.metric_definitions = kwargs.pop('metrics')
        self.labels = Labels(kwargs.pop('labels', {}), logger=self.logger, _log_init=False)
        self.labels['endpoint'] = self.name

        self.get_data()

    def populate_metrics(self):
        """ Populates the metrics for the JSON endpoint """
        from .json_metric import JSONMetric
        for metric in self.metrics.copy():
            self.logger.debug("Removing stale metric: %s", metric)
            self.metrics.remove(metric)  # Remove the old metric
            del metric

        for metric, values in self.metric_definitions.items():
            metric_args = {'json_path': values['path'], 'metric_type': values['type']}
            self.metrics.append(JSONMetric(metric, labels=self.get_labels(), json_data=self.data,
                                           **metric_args, **values,
                                           _log_init=False, logger=self.logger))

    def get_data(self):
        """ Returns the data for the JSON endpoint """
        from requests import get
        from json import loads
        from json.decoder import JSONDecodeError

        self.logger.info("Getting data from endpoint: %s", self.endpoint)

        kwargs = {}
        if self.headers:
            kwargs['headers'] = self.headers

        request = get(self.endpoint, **kwargs)

        if request.status_code != 200:
            raise ValueError("[%s] Request failed: %s" % (request.status_code, request.text))

        self.logger.debug("Got data: %s", request.text)

        try:
            self.data = loads(request.text)
        except JSONDecodeError as error:
            raise ValueError("Failed to decode JSON: %s" % error)

        self.update_json_labels()
        self.populate_metrics()

    def update_json_labels(self):
        """ Updates the JSON labels """
        from .json_labels import JSONLabels
        self.logger.debug("[%s] Updating JSON labels", self.name)

        kwargs = {'json_paths': self.json_paths, 'json_data': self.data,
                  'logger': self.logger, '_log_init': False}

        self.json_labels = JSONLabels(**kwargs)

    def __str__(self):
        """ Returns the value of all the metrics """
        self.logger.info("[%s] Getting updated metric data", self.name)
        self.get_data()
        return '\n'.join(str(metric) for metric in self.metrics)



