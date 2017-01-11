#!/usr/bin/env python
# -*- coding=utf-8 -*-

"""
Author: Rosen
Mail: rosenluov@gmail.com
File: common.py
Created Time: Mon Dec 26 15:28:28 2016
"""

from traceback import print_exc

import yaml


def load_yaml_data(filename=None):
    try:
        with open(filename, 'r') as f:
            data = yaml.load(f)
            return data
    except IOError:
        print_exc()


def falcon_structure(endpoint, metric, timestamp, value, counter_type='GAUGE', tags=None):
    structure = {
        'endpoint': endpoint,
        'metric': metric,
        'timestamp': timestamp,
        'step': 10,
        'value': value,
        'counterType': counter_type,
        'tags': tags
    }
    return structure


class ConfigHandlers(object):

    def __init__(self, filename):
        self.filename = filename

    def load_falcon_conf(self):
        if self.filename:
            data = load_yaml_data(self.filename)
            url = data.get('url', '')
            return url

    def load_common_conf(self):
        if self.filename:
            data = load_yaml_data(self.filename)
            host = data.get('host', '')
            port = data.get('port', '')
            return host, port

    def load_zk_conf(self):
        if self.filename:
            data = load_yaml_data(self.filename)
            host = data.get('host', '127.0.0.1')
            port = data.get('port', 2181)
            cluster = data.get('cluster', 'zk-cluster')
            return host, port, cluster
