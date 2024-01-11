#!/usr/bin/env python3

from signal import signal
from json_exporter import JSONExporter
from zenlib.util import init_logger, init_argparser, process_args


def main():
    logger = init_logger(__package__)
    argparser = init_argparser(prog=__package__, description='JSON Exporter for Prometheus')
    argparser.add_argument('-p', '--port', type=int, nargs='?', help='Port to listen on.')
    argparser.add_argument('-a', '--address', type=str, nargs='?', help='Address to listen on.')

    args = process_args(argparser, logger=logger)

    kwargs = {'logger': logger}

    if args.port:
        kwargs['port'] = args.port
    if args.address:
        kwargs['ip'] = args.address

    exporter = JSONExporter(**kwargs)

    def handle_shutdown_signal(sig, frame):
        logger.info(f"Received signal: {sig}. Shutting down...")
        if hasattr(exporter, '__is_shut_down') and not exporter.__is_shut_down.is_set():
            exporter.shutdown()
        exit(0)

    # Handle SIGINT, SIGTERM, SIGQUIT, SIGABRT
    for sig in [2, 15, 3, 6]:
        signal(sig, handle_shutdown_signal)

    exporter.serve_forever()


if __name__ == '__main__':
    main()
