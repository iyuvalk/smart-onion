#!/usr/bin/python2.7
from __future__ import print_function
import sys
from bottle import Bottle
import datetime
import json
import base64
import os
import hashlib
import time
from multiprocessing import Value



DEBUG = False
config_file_name = "queries.json"
config_file_default_path = "/etc/smart-onion/"
config_file = os.path.join(config_file_default_path, config_file_name)


class ConfigFileCannotBeRead_Exception(Exception):

    def __init__(self, message, base_exception = None):
        self.message = message
        self.base_exception = base_exception


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
        "smart-onion.config.common.logging_format": "timestamp=%s;module=smart-onion_%s;method=%s;severity=%s;state=%s;metric/metric_family=%s;exception_msg=%s;exception_type=%s;message=%s",
        "smart-onion.config.architecture.external_services.security-onion-elk.host": "127.0.0.1",
        "smart-onion.config.architecture.external_services.security-onion-elk.port": 9200,
        "smart-onion.config.architecture.external_services.security-onion-elk.protocol": "http",
        "smart-onion.config.architecture.internal_services.backend.pipeline.statsd.host": "127.0.0.1",
        "smart-onion.config.architecture.internal_services.backend.pipeline.statsd.port": 8125,
        "smart-onion.config.architecture.internal_services.backend.queue.kafka.bootstrap_servers": "10.253.0.141",
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.similarity_test_fonts_path": "/opt/smart-onion/resources/similarity-test-fonts/",
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.published-listening-host": "127.0.0.1",
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.published-listening-port": 9000,
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.published-listening-protocol": "http",
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.listening-host": "127.0.0.1",
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.listening-port": 9000,
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.protocol": "http",
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.max_timeout_to_elastic": 120,
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.base_urls.similarity_test": "/smart-onion/test-similarity/",
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.base_urls.query_count": "/smart-onion/query-count/",
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.base_urls.field_query": "/smart-onion/field-query/",
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.base_urls.list_hash": "/smart-onion/list-hash/",
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.base_urls.lld": "/smart-onion/discover/",
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.sampling_interval_ms": 600000,
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.task_base_ttl": 8640, # Number of sampling cycles (every 5 mins) in 30 days
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.sampling_tasks_gc_interval": 604800,
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.keep_lost_items_for_days": 30,
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.poller_threads_per_cpu": 3,
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.tinyfy_urls": False,
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.metric_items_max_length": 20,
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.metric_items_tokenizer_dbtype": "postgres",
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.metric_items_tokenizer_dbhost": "localhost",
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.metric_items_tokenizer_dbport": 5432,
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.metric_items_tokenizer_dbname": "smart_onion_metric_collector",
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.metric_items_tokenizer_dbuser": "smart_onion_metric_collector",
        "smart-onion.config.architecture.internal_services.backend.metrics-collector.metric_items_tokenizer_dbpassword": "vindeta11",
        "smart-onion.config.architecture.internal_services.backend.anomaly-detector.published-listening-host": "127.0.0.1",
        "smart-onion.config.architecture.internal_services.backend.anomaly-detector.published-listening-port": 9001,
        "smart-onion.config.architecture.internal_services.backend.anomaly-detector.published-listening-protocol": "http",
        "smart-onion.config.architecture.internal_services.backend.anomaly-detector.base_urls.get-anomaly-score": "/smart-onion/get-anomaly-score/",
        "smart-onion.config.architecture.internal_services.backend.anomaly-detector.listening-host": "127.0.0.1",
        "smart-onion.config.architecture.internal_services.backend.anomaly-detector.listening-port": 9001,
        "smart-onion.config.architecture.internal_services.backend.anomaly-detector.protocol": "http",
        "smart-onion.config.architecture.internal_services.backend.anomaly-detector.metrics_to_work_on_pattern": "^(?!(stats\.gauges\.smart\-onion\.anomaly_))[^ ]+[A-Za-z0-9\-_](( [0-9]+(\.[0-9]+|) [0-9]+)|)$",
        "smart-onion.config.architecture.internal_services.backend.anomaly-detector.metrics_physical_path": "/data/metrics/whisper/",
        "smart-onion.config.architecture.internal_services.backend.anomaly-detector.reference_past_sample_periods": "7,14,21",
        "smart-onion.config.architecture.internal_services.backend.anomaly-detector.reference_timespan_in_seconds": 86400,
        "smart-onion.config.architecture.internal_services.backend.anomaly-detector.anomalies_check_interval": 300,
        "smart-onion.config.architecture.internal_services.backend.anomaly-detector.anomaly_score_threshold_for_reporting": 90,
        "smart-onion.config.architecture.internal_services.backend.anomaly-detector.reported_anomalies_topic": "detected-anomalies",
        "smart-onion.config.architecture.internal_services.backend.metrics-analyzer.metrics_to_work_on_pattern": "^(?!(stats\.gauges\.smart\-onion\.anomaly_))[^ ]+[A-Za-z0-9\-_](( [0-9]+(\.[0-9]+|) [0-9]+)|)$",
        "smart-onion.config.architecture.internal_services.backend.metrics-analyzer.published-listening-host": "127.0.0.1",
        "smart-onion.config.architecture.internal_services.backend.metrics-analyzer.published-listening-port": 9002,
        "smart-onion.config.architecture.internal_services.backend.metrics-analyzer.listening-host": "127.0.0.1",
        "smart-onion.config.architecture.internal_services.backend.metrics-analyzer.listening-port": 9002,
        "smart-onion.config.architecture.internal_services.backend.metrics-analyzer.protocol": "TCP",
        "smart-onion.config.architecture.internal_services.backend.metrics-analyzer.connection-backlog": 10,
        "smart-onion.config.architecture.internal_services.backend.metrics-analyzer.save_interval": 10,
        "smart-onion.config.architecture.internal_services.backend.metrics-analyzer.ping-listening-host": "127.0.0.1",
        "smart-onion.config.architecture.internal_services.backend.metrics-analyzer.ping-listening-port": 9007,
        "smart-onion.config.architecture.internal_services.backend.metrics-analyzer.ping-protocol": "http",
        "smart-onion.config.architecture.internal_services.backend.metrics-analyzer.max-allowed-models": 400,
        "smart-onion.config.architecture.internal_services.backend.metrics-analyzer.metrics_topic_name": "metrics",
        "smart-onion.config.architecture.internal_services.backend.metrics-analyzer.minimum_seconds_between_model_over_quota_log_messages": 3600,
        "smart-onion.config.architecture.internal_services.backend.metrics-analyzer.reported_anomalies_topic": "detected-anomalies",
        "smart-onion.config.architecture.internal_services.backend.metrics-analyzer.anomaly_score_threshold_for_reporting": 0.9,
        "smart-onion.config.architecture.internal_services.backend.metrics-analyzer.anomaly_likelihood_threshold_for_reporting": 0.9,
        "smart-onion.config.architecture.internal_services.backend.configurator.published-listening-host": "127.0.0.1",
        "smart-onion.config.architecture.internal_services.backend.configurator.published-listening-port": 9003,
        "smart-onion.config.architecture.internal_services.backend.configurator.published-listening-protocol": "http",
        "smart-onion.config.architecture.internal_services.backend.configurator.listening-host": "127.0.0.1",
        "smart-onion.config.architecture.internal_services.backend.configurator.listening-port": 9003,
        "smart-onion.config.architecture.internal_services.backend.configurator.protocol": "http",
        "smart-onion.config.architecture.internal_services.backend.alerter.metrics_to_work_on_pattern": "^(stats\.gauges\.smart\-onion\.anomaly_)[^ \\n]+[A-Za-z0-9\-_]$",
        "smart-onion.config.architecture.internal_services.backend.alerter.published-listening-host": "127.0.0.1",
        "smart-onion.config.architecture.internal_services.backend.alerter.published-listening-port": 9004,
        "smart-onion.config.architecture.internal_services.backend.alerter.published-listening-protocol": "http",
        "smart-onion.config.architecture.internal_services.backend.alerter.listening-host": "127.0.0.1",
        "smart-onion.config.architecture.internal_services.backend.alerter.listening-port": 9004,
        "smart-onion.config.architecture.internal_services.backend.alerter.protocol": "http",
        "smart-onion.config.architecture.internal_services.backend.timer.published-listening-protocol": "http",
        "smart-onion.config.architecture.internal_services.backend.timer.published-listening-host": "127.0.0.1",
        "smart-onion.config.architecture.internal_services.backend.timer.published-listening-port": 9999,
        "smart-onion.config.architecture.internal_services.backend.timer.protocol": "http",
        "smart-onion.config.architecture.internal_services.backend.timer.listening-host": "127.0.0.1",
        "smart-onion.config.architecture.internal_services.backend.timer.listening-port": 9006,
        "smart-onion.config.architecture.internal_services.backend.timer.discover-interval": 3600,
        "smart-onion.config.architecture.internal_services.backend.timer.max_items_in_batch": 10,
        "smart-onion.config.architecture.internal_services.backend.timer.metrics_collection_tasks_topic": "metric-collection-tasks",
        "smart-onion.config.architecture.internal_services.backend.tiny_url.published-listening-protocol": "http",
        "smart-onion.config.architecture.internal_services.backend.tiny_url.published-listening-host": "127.0.0.1",
        "smart-onion.config.architecture.internal_services.backend.tiny_url.published-listening-port": 9999,
        "smart-onion.config.architecture.internal_services.backend.tiny_url.protocol": "http",
        "smart-onion.config.architecture.internal_services.backend.tiny_url.listening-host": "127.0.0.1",
        "smart-onion.config.architecture.internal_services.backend.tiny_url.listening-port": 9999,
        "smart-onion.config.architecture.internal_services.backend.tiny_url.backup_file": "/tmp/tiny_url.json.db",
        "smart-onion.config.architecture.internal_services.backend.tiny_url.backup_interval": 30,
        "smart-onion.config.architecture.internal_services.backend.tiny_url.base_urls.tiny2url": '/so/tiny2url/',
        "smart-onion.config.architecture.internal_services.backend.tiny_url.base_urls.url2tiny": '/so/url2tiny',
        "smart-onion.config.architecture.internal_services.backend.tiny_url.base_urls.proxy_by_tiny": '/so/tiny/',
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

    def __init__(self, listen_ip, listen_port, config_filename):
        self._time_loaded = time.time()
        self._host = listen_ip
        self._port = listen_port
        self._app = Bottle()
        self._route()
        try:
            with open(config_filename, 'r') as config_file_obj:
                self.config["smart-onion.config.queries"] = json.load(config_file_obj)
        except Exception as ex:
            raise ConfigFileCannotBeRead_Exception(message="Config file could not be read. CANNOT CONTINUE!", base_exception=ex)

    def _route(self):
        self._app.route('/smart-onion/configurator/get_config/<config_name>', method="GET", callback=self.get_config)
        self._app.route('/smart-onion/configurator/update_config/<config_name>', method="GET", callback=self.update_config)
        self._app.route('/ping', method="GET", callback=self._ping)

    def _file_as_bytes(self, filename):
        with open(filename, 'rb') as file:
            return file.read()

    def _ping(self):
        return {
            "response": "PONG",
            "file": __file__,
            "hash": hashlib.md5(self._file_as_bytes(__file__)).hexdigest(),
            "uptime": time.time() - self._time_loaded
        }

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
config_filename = '/etc/smart-onion/queries.json'
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
try:
    config_filename = utils.extract_args("config-file")
except:
    pass

sys.argv = [sys.argv[0]]
SmartOnionConfigurator(listen_ip=ip, listen_port=port, config_filename=config_filename).run()