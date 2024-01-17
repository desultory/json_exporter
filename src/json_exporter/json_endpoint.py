from prometheus_exporter import Exporter, cached_exporter


@cached_exporter
class JSONEndpoint(Exporter):
    """ Defines the JSON endpoint for the JSON exporter """
    def __init__(self, name, *args, **kwargs):
        """ Initializes the JSON endpoint """
        self.name = name
        super().__init__(*args, **kwargs)
        self.labels['endpoint'] = self.name

    def get_labels(self):
        """ Returns the labels for the JSON endpoint """
        return self.labels | self._json_labels

    def read_config(self):
        """ Reads the config file using the parent method, adds json specific config """
        super().read_config()
        if self.name not in self.config['json']:
            raise ValueError("Endpoint not defined in config: %s" % self.name)

        self.endpoint = self.config['json'][self.name]['endpoint']
        self.metric_definitions = self.config['json'][self.name]['metrics']

        for config_key in ['headers', 'post_data', 'json_labels']:
            setattr(self, config_key, self.config['json'][self.name].get(config_key, {}))

    def populate_metrics(self):
        """
        Populates the metrics for the JSON endpoint.
        Resets the metrics list.
        """
        from .json_metric import JSONMetric

        for metric, values in self.metric_definitions.items():
            metric_args = {'json_path': values['path'], 'metric_type': values['type']}
            self.metrics.append(JSONMetric(metric, labels=self.get_labels(), json_data=self.data,
                                           **metric_args, **values,
                                           _log_init=False, logger=self.logger))

    async def get_data(self):
        from aiohttp import ClientSession
        from time import time
        self.logger.info("Getting data from endpoint: %s", self.endpoint)

        kwargs = {}
        if self.headers:
            kwargs['headers'] = self.headers

        start_time = time()
        async with ClientSession() as session:
            if self.post_data:
                async with session.post(self.endpoint, json=self.post_data, **kwargs) as request:
                    self.logger.debug("[%s] POST data: %s" % (self.endpoint, self.post_data))
                    request_data = await request.text()
            else:
                async with session.get(self.endpoint, **kwargs) as request:
                    self.logger.debug("[%s] GET data: %s" % (self.endpoint, kwargs))
                    request_data = await request.text()
        self._request_time = time() - start_time
        self.logger.info("[%s] Request time: %s" % (self.endpoint, self._request_time))

        self.logger.debug("Got data: %s", request_data)
        return request_data

    async def get_metrics(self, label_filter={}, *args, **kwargs):
        """
        Gets the data from the endpoint.
        Updates the JSON labels.
        Populates the metrics using the new labels and data.
        """
        for key, value in label_filter.items():
            if key in self.labels and self.labels[key] == value:
                break
        else:
            if label_filter:
                self.logger.debug("Skipping data request because filter did not match: %s", label_filter)
                self.logger.debug("Labels: %s", self.labels)
                return

        from prometheus_exporter import Metric
        from json import loads
        from json.decoder import JSONDecodeError

        try:
            self.data = loads(await self.get_data())
        except JSONDecodeError as error:
            raise ValueError("Failed to decode JSON: %s" % error)

        self.update_json_labels()
        self.metrics = [Metric('json_request_time', value=self._request_time,
                               help_text="Time taken to get the JSON data from the endpoint",
                               metric_type='gauge', labels=self.get_labels(),
                               logger=self.logger, _log_init=False)]
        self.populate_metrics()
        return self.metrics

    def update_json_labels(self):
        """ Updates the JSON labels """
        from .json_labels import JSONLabels
        self.logger.debug("[%s] Updating JSON labels for: %s" % (self.name, self.json_labels))

        kwargs = {'json_paths': self.json_labels, 'json_data': self.data,
                  'logger': self.logger, '_log_init': False}

        self._json_labels = JSONLabels(**kwargs)

    def __str__(self):
        """
        Gets updated JSON data from the endpoint.
        Returns the value of all the metrics.
        """
        return '\n'.join(str(metric) for metric in self.metrics)



