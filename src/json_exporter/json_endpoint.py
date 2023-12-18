"""
Defines the JSON endpoint for the JSON exporter
"""

from zenlib.logging import loggify


@loggify
class JSONEndpoint:
    """
    Defines the JSON endpoint for the JSON exporter
    """
    def __init__(self, name, *args, **kwargs):
        """
        Initializes the JSON endpoint
        """
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
        from .json_labels import JSONLabels
        from .json_metric import JSONMetric

        self.endpoint = kwargs.pop('endpoint')
        self.headers = kwargs.pop('headers', {})

        common_args = {'logger': self.logger, '_log_init': False}
        labels = kwargs.pop('labels', {})
        self.labels = Labels(labels, **common_args)

        self.get_data()
        common_args.update({'json_data': self.data})

        json_paths = kwargs.pop('json_labels', {})
        self.json_labels = JSONLabels(json_paths=json_paths, **common_args)

        for metric, values in kwargs.pop('metrics').items():
            metric_args = {'json_path': values.pop('path'), 'metric_type': values.pop('type')}
            self.metrics.append(JSONMetric(metric, labels=self.get_labels(),
                                           **common_args, **metric_args, **values))

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

    def __str__(self):
        """ Returns the value of all the metrics """
        return ''.join(str(metric) for metric in self.metrics)



