#!/usr/bin/python2.7
import sys
from bottle import Bottle
import datetime
import json
import base64


DEBUG = True


class Utils:

    def __init__(self):
        pass

    @staticmethod
    def extract_args(arg_prefix, error_if_not_found=True):
        """
        This method extracts command line arguments to help get configuration from the command line.
        The command line arguments should be in this format:
        python metrics_analyzer.py --conn-backlog=20 --listen-port=3000 ...
        :param arg_prefix: Indicates the argument prefix that this method should look for in the command line (i.e.
        conn-backlog)
        :param error_if_not_found: Whether or not to raise an exception if the requested argument was not found in the
        command line
        :return: The value of the requested command line argument (if found) and None (or an exception) otherwise.
        """
        for arg in sys.argv:
            if arg.startswith("--" + arg_prefix + "="):
                return arg.split("=")[1]
        if error_if_not_found:
            raise Exception("Argument not found.")
        else:
            return None

class SmartOnionConfigurator:
    config = {
        "smart-onion.config.architecture.external_services.security-onion-elk.host": "127.0.0.1",
        "smart-onion.config.architecture.external_services.security-onion-elk.port": 9200,
        "smart-onion.config.architecture.external_services.security-onion-elk.protocol": "http",
        "smart-onion.config.architecture.internal_services.backend.pipeline.statsd.host": "127.0.0.1",
        "smart-onion.config.architecture.internal_services.backend.pipeline.statsd.port": 8125,
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.listening-host": "127.0.0.1",
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.listening-port": 9000,
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.protocol": "http",
        "smart-onion.config.architecture.internal_services.backend.anomaly-detector.listening-host": "127.0.0.1",
        "smart-onion.config.architecture.internal_services.backend.anomaly-detector.listening-port": 9001,
        "smart-onion.config.architecture.internal_services.backend.anomaly-detector.protocol": "http",
        "smart-onion.config.architecture.internal_services.backend.metrics-analyzer.listening-host": "127.0.0.1",
        "smart-onion.config.architecture.internal_services.backend.metrics-analyzer.listening-port": 9002,
        "smart-onion.config.architecture.internal_services.backend.metrics-analyzer.protocol": "TCP",
        "smart-onion.config.architecture.internal_services.backend.metrics-analyzer.connection-backlog": 10,
        "smart-onion.config.architecture.internal_services.backend.metrics-analyzer.save_interval": 10,
        "smart-onion.config.architecture.internal_services.backend.configurator.listening-host": "127.0.0.1",
        "smart-onion.config.architecture.internal_services.backend.configurator.listening-port": 9003,
        "smart-onion.config.architecture.internal_services.backend.configurator.protocol": "http",
        "smart-onion.config.architecture.internal_services.backend.alerter.listening-host": "127.0.0.1",
        "smart-onion.config.architecture.internal_services.backend.alerter.listening-port": 9004,
        "smart-onion.config.architecture.internal_services.backend.alerter.protocol": "http",
        "smart-onion.config.architecture.internal_services.frontend.ui.listening-host": "0.0.0.0",
        "smart-onion.config.architecture.internal_services.frontend.ui.listening-port": 8080,
        "smart-onion.config.architecture.internal_services.frontend.ui.protocol": "http",
        "smart-onion.config.architecture.internal_services.frontend.service.listening-host": "127.0.0.1",
        "smart-onion.config.architecture.internal_services.frontend.service.listening-port": 9005,
        "smart-onion.config.architecture.internal_services.frontend.service.protocol": "http",
        "smart-onion.config.dynamic.learned.networks.lan-network": ["10.253.*"],
        "smart-onion.config.dynamic.learned.networks.servers-network": ["10.253.0.*"],
        "smart-onion.config.dynamic.learned.networks.workstations-network": ["10.253.33.*","10.253.31.*", "10.253.32.*"],
        "smart-onion.config.dynamic.learned.networks.public-ips": ["193.16.147.*"],
        "smart-onion.config.dynamic.learned.networks.crown-jewels-ips": ["10.253.*"],
        "smart-onion.config.dynamic.learned.ports.websites": [80, 8080],
        "smart-onion.config.dynamic.learned.ports.ssh": [22],
        "smart-onion.config.dynamic.learned.ports.dhcp": [67],
        "smart-onion.config.dynamic.learned.ports.ldap": [389],
        "smart-onion.config.dynamic.learned.ports.pgsql": [5432],
        "smart-onion.config.dynamic.learned.ports.mssql": [1433],
        "smart-onion.config.dynamic.learned.ports.mysql": [3306],
        "smart-onion.config.dynamic.learned.ports.ftp": [21],
        "smart-onion.config.dynamic.learned.ports.tftp": [69],
        "smart-onion.config.dynamic.learned.ports.dns": [53],
        "smart-onion.config.dynamic.metric_htm_anomaly_likelihood_threshold": 0.9,
        "smart-onion.config.dynamic.metric_htm_anomaly_score_threshold": 0.9,
        "smart-onion.config.dynamic.metric_statistical_anomaly_score_threshold": 90
    }

    def __init__(self, listen_ip, listen_port):
        self._host = listen_ip
        self._port = listen_port
        self._app = Bottle()
        self._route()

    def _route(self):
        self._app.route('/smart-onion/configurator/get_config/<config_name>', method="GET", callback=self.get_config)
        self._app.route('/smart-onion/configurator/update_config/<config_name>', method="GET", callback=self.update_config)

    def run(self):
        if DEBUG:
            self._app.run(host=self._host, port=self._port)
        else:
            self._app.run(host=self._host, port=self._port, server="gunicorn", workers=32)

    def get_config(self, config_name):
        if not '*' in config_name:
            return json.dumps(self.config[config_name])
        elif not config_name.endswith('*') or config_name.count('*') > 1:
            return "ERROR: Pattern not supported."
        else:
            res = {}
            for key in self.config.keys():
                if key.startswith(config_name.replace("*", "")):
                    res[key] = self.config[key]
            return res

    def update_config(self, config_name):
        #This method should expect to receive the requested config value and a proof of an authentication
        pass

ip = '127.0.0.1'
port = 9003
utils = Utils()

try:
    ip = utils.extract_args("listen-ip")
except:
    pass
try:
    if int(utils.extract_args("listen-port")) >= 1:
        port = int(utils.extract_args("listen-port"))
except:
    pass

SmartOnionConfigurator(listen_ip=ip, listen_port=port).run()