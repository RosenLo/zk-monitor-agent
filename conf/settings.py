#!/usr/bin/env python
# encoding: utf-8

"""
Author: Rosen
Mail: rosenluov@gmail.com
File: settings.py
Created Time: 12/28/16 11:53
"""

import logging.config
from socket import gethostname
from os import path

HOSTNAME = gethostname()
BASE_DIR = path.dirname(path.abspath(__file__))
STATSD_FILE = BASE_DIR + '/statsd.yaml'
OPEN_FALCON = BASE_DIR + '/open-falcon.yaml'
ZK_FILE = BASE_DIR + '/zk.yaml'

PID_FILE = '/var/run/zk-monitor-agent/zk-monitor-agent.pid'
STDOUT = '/data/log/zk-monitor-agent/zk-agent.log'
STDERR = '/data/log/zk-monitor-agent/zk-agent.err'

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] [%(name)s] %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'cloghandler.ConcurrentRotatingFileHandler',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 50,
            # If delay is true,
            # then file opening is deferred until the first call to emit().
            'delay': True,
            'filename': STDOUT,
            'formatter': 'verbose'
        }
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    }
})

EXCEPT = [
    'version',
]

COUNTER = [
    'sent',
    'received',
]