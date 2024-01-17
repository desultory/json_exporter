from zenlib.logging import loggify


@loggify
class JSONEndpoint:
    """ Defines the JSON endpoint for the JSON exporter """
    def __init__(self, name, *args, **kwargs):
        """ Initializes the JSON endpoint """
        self.name = name
        self.metrics = []
        self.parse_kwargs(kwargs)

    def get_labels(self):
        """ Returns the labels for the JSON endpoint """
        return self.labels.copy() | self.json_labels

    def parse_kwargs(self, kwargs):
        """
        Parses the kwargs passed during initialization.
        Makes the intitial JSON request, to be used for json_labels.
        Adds all metrics to self.metrics.
        """
        from prometheus_exporter import Labels

        self.endpoint = kwargs.pop('endpoint')
        self.headers = kwargs.pop('headers', {})
        self.post_data = kwargs.pop('post_data', {})
        self.json_paths = kwargs.pop('json_labels', {})
        self.metric_definitions = kwargs.pop('metrics')
        self.labels = Labels(kwargs.pop('labels', {}), logger=self.logger, _log_init=False)
        self.labels['endpoint'] = self.name

    def populate_metrics(self):
        """
        Populates the metrics for the JSON endpoint.
        Resets the metrics list.
        """
        from .json_metric import JSONMetric
        from prometheus_exporter import Metric

        self.metrics = [Metric('json_request_time', value=self._request_time,
                               help_text="Time taken to get the JSON data from the endpoint",
                               labels=self.get_labels(), metric_type='gauge',
                               logger=self.logger, _log_init=False)]

        for metric, values in self.metric_definitions.items():
            metric_args = {'json_path': values['path'], 'metric_type': values['type']}
            self.metrics.append(JSONMetric(metric, labels=self.get_labels(), json_data=self.data,
                                           **metric_args, **values,
                                           _log_init=False, logger=self.logger))

    async def get_data(self, label_filter={}):
        """
        Gets the data from the endpoint.
        Updates the JSON labels.
        Populates the metrics using the new labels and data.
        """
        from aiohttp import ClientSession
        from json import loads
        from json.decoder import JSONDecodeError
        from time import time

        if self.metrics and not await self.labels.filter_metrics(self.metrics, label_filter):
            self.logger.info("[%s] All metrics were filtered: %s" % (self.name, label_filter))
            return

        self.logger.info("Getting data from endpoint: %s", self.endpoint)

        kwargs = {}
        if self.headers:
            kwargs['headers'] = self.headers

        start_time = time()
        async with ClientSession() as session:
            if self.post_data:
                async with session.post(self.endpoint, json=self.post_data, **kwargs) as request:
                    self.logger.debug("POST data: %s", self.post_data)
                    request_data = await request.text()
            else:
                async with session.get(self.endpoint, **kwargs) as request:
                    request_data = await request.text()
        self._request_time = time() - start_time
        self.logger.info("[%s] Request time: %s" % (self.endpoint, self._request_time))

        self.logger.debug("Got data: %s", request_data)

        try:
            self.data = loads(request_data)
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
        """
        Gets updated JSON data from the endpoint.
        Returns the value of all the metrics.
        """
        self.logger.info("[%s] Getting updated metric data", self.name)
        self.get_data()
        return '\n'.join(str(metric) for metric in self.metrics)



