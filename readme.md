# JSON Exporter

This is a simple Prometheus exporter using:

* [Prometheus exporter](https://github.com/desultory/prometheus_exporter)
* [aiohttp](https://github.com/aio-libs/aiohttp)
* [zenlib](https://github.com/desultory/zenlib)


## Features

* Automatic query caching
* Full async
* Robust logging
* POST/GET
* Automatic label creation from JSON values

## Installation

This project is on pypi and can be installed with:

`pip install --user json_exporter`

## Usage

Configuration is required and is specified in the following format:


```
#listen_ip = '127.0.0.1'
#listen_port = 9809

cache_life = 900

# GET request example
[json.website]
endpoint = "https://api.example.com"

[json.website.headers]
auth_key = 'g5s9ZyklWpY/wRf6gai2DtC0GKUO9qsNYON+rkQzzbeD7Nmvn9UCg5hQMdtPN49x'

[json.website.metrics.test]
path = "result.path.test"
type = "counter"
help = "Test counter"

[json.website.metrics.example]
path = "result.another.path.example"
type = "gauge"
help = "Example gauge"

[json.website.json_labels]
api_user = "response.user"

# POST example

[json.website2]
endpoint = "https://api.example2.com"

[json.website2.post_data]
method = 'get_data'
api_key = 'aVDZvzwuT86KhFF33VkS95Ui/D1E37PDoShc6Wy9w1uTVMP776CP6AZHp5eyzcij'

[json.website2.metrics.example]
path = "results.path.example"
type = "gauge"
help = "Example gauge"

```

> GET requests are used unless a `post_data` config section is specified.
