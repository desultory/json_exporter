from prometheus_exporter import Exporter, Metric, cached_exporter


@cached_exporter
class JSONEndpoint(Exporter):
    """ Defines the JSON endpoint for the JSON exporter """
    def __init__(self, name, *args, **kwargs):
        """ Initializes the JSON endpoint """
        self.name = name
        super().__init__(*args, **kwargs)
        self.labels['endpoint'] = self.name

    def get_labels(self):
        if getattr(self, 'json_labels', None):
            return self.labels | self.json_labels
        return self.labels

    async def update_json_labels(self):
        """ Updates the JSON labels """
        from .json_labels import JSONLabels
        self.logger.debug("[%s] Updating JSON labels for: %s" % (self.name, self.json_label_paths))

        kwargs = {'json_paths': self.json_label_paths, 'json_data': self.json_data,
                  'logger': self.logger, '_log_init': False}

        self.json_labels = JSONLabels(**kwargs)

    def read_config(self):
        """ Reads the config file using the parent method, adds json specific config """
        super().read_config()
        if self.name not in self.config['json']:
            raise ValueError("Endpoint not defined in config: %s" % self.name)

        self.endpoint = self.config['json'][self.name]['endpoint']
        self.metric_definitions = self.config['json'][self.name]['metrics']

        for config_key in ['headers', 'post_data']:
            setattr(self, config_key, self.config['json'][self.name].get(config_key, {}))

        if json_labels := self.config['json'][self.name].get('json_labels', {}):
            self.json_label_paths = json_labels

    async def populate_metrics(self):
        """
        Populates the metrics for the JSON endpoint.
        Uses cached data, does not get fresh data.
        """
        from .json_metric import JSONMetric
        self.metrics = [Metric('json_request_time', value=self.request_time,
                               help_text="Time taken to get the JSON data from the endpoint",
                               metric_type='gauge', labels=self.get_labels(),
                               logger=self.logger, _log_init=False)]

        for metric, values in self.metric_definitions.items():
            metric_args = {'json_path': values['path'], 'metric_type': values['type']}
            self.metrics += [JSONMetric(metric, labels=self.get_labels(), json_data=self.json_data,
                                        **metric_args, **values,
                                        _log_init=False, logger=self.logger)]

    async def get_data(self):
        """ Get fresh json_data """
        from aiohttp import ClientSession
        from json import loads
        from time import time

        self.logger.info("[%s] Getting data from endpoint: %s" % (self.name, self.endpoint))
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
        self.request_time = time() - start_time
        self.logger.info("[%s] Request time: %s" % (self.endpoint, self.request_time))

        self.logger.debug("Got data: %s", request_data)
        self.json_data = loads(request_data)

    async def get_metrics(self, label_filter={}):
        """
        Gets the data from the endpoint.
        Populates the metrics using the new labels and data.
        """
        from json.decoder import JSONDecodeError
        for label, value in label_filter.items():
            labels = self.get_labels()
            if label not in labels or labels[label] != value:
                self.logger.debug("[%s] Label filter does not match existing label: %s=%s" % (self.name, label, value))
                return
        try:
            await self.get_data()
        except JSONDecodeError:
            self.logger.error("[%s] Failed to decode JSON data: %s" % (self.name, self.json_data))
            return
        await self.update_json_labels()
        await self.populate_metrics()
        self.logger.debug("[%s] Got %d metrics" % (self.name, len(self.metrics)))
        return self.metrics
