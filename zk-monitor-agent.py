#!/usr/bin/env python
# encoding: utf-8

"""
Author: Rosen
Mail: rosenluov@gmail.com
File: zk-monitor-agent.py
Created Time: 1/11/17 14:42
"""

import json
import logging
import socket
import sys
from multiprocessing import Process, Queue
from os import getpid
from time import time, sleep
from copy import deepcopy
from traceback import print_exc

import requests
import statsd

from conf.settings import (
    STDERR,
    STATSD_FILE,
    OPEN_FALCON,
    ZK_FILE,
    PID_FILE,
    EXCEPT,
    COUNTER,
    HOSTNAME,
)
from utils.common import falcon_structure, ConfigHandlers
from utils.daemonize import Daemon

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

log = logging.getLogger('')
q = Queue(10)


class MyDaemon(Daemon):
    @staticmethod
    def run():
        log.info("Daemon started with pid %d! \n", getpid())
        try:
            url = ConfigHandlers(OPEN_FALCON).load_falcon_conf()
            statsd_host, statsd_port = ConfigHandlers(STATSD_FILE).load_common_conf()
            zk_host, zk_port, zk_cluster = ConfigHandlers(ZK_FILE).load_zk_conf()
            statsd_client = statsd.StatsClient(statsd_host, statsd_port, zk_cluster)
            zk = ZooKeeperServer(zk_host, zk_port)
            while True:
                if int(time()) % 10 == 0:
                    p = Process(target=main, args=(statsd_client, zk, url,))
                    p.start()
                    p.join()
                sleep(1)
        except Exception as e:
            log.error(e)
            print_exc()
            sys.exit(1)


class ZooKeeperServer(object):
    def __init__(self, host='127.0.0.1', port=2181, timeout=1):
        self._address = (host, int(port))
        self._timeout = timeout

    def get_stats(self):
        data = self._send_cmd('mntr')
        if data:
            return self._parse(data)

    def _send_cmd(self, cmd):
        s = socket.socket()
        s.settimeout(self._timeout)

        s.connect(self._address)
        s.send(cmd)

        data = s.recv(2048)
        s.close()

        return data

    @staticmethod
    def _parse(data):
        h = StringIO(data)
        result = {}
        for line in h.readlines():
            try:
                k, v = map(str.strip, line.split('\t'))
                k = k.replace('zk_', '')

                if v == 'leader':
                    v = 1
                elif v == 'follower':
                    v = 0

                if k in EXCEPT:
                    continue
                result[k] = int(v)
            except ValueError:
                raise ValueError("Found invalid line: {}".format(line))
        return result

    @staticmethod
    def counter_to_gauge(data=None):
        statsd_data = {}
        if q.empty():
            log.error('Queue is empty!')
        else:
            old_stats_data = q.get()
            log.info('Get a message from the Queue.')
            for count in COUNTER:
                for k in data:
                    if count in k:
                        data[k] = round((data[k] - old_stats_data[k]) / 10.0, 2)
            statsd_data = data
        return statsd_data


def send_to_statsd(statsd_client, data=None):
    try:
        if data:
            for k, v in data.items():
                metric = HOSTNAME + '.' + k
                statsd_client.gauge(metric, v)
        log.info("Successfully send %d metrics to StatsD!", len(data))
    except Exception as e:
        log.error(e)
        print_exc()


def send_to_falcon(url=None, data=None):
    finally_data = []
    if data and url:
        for k, v in data.items():
            finally_data.append(falcon_structure(HOSTNAME, k, int(time()), v))

        res = requests.post(url, data=json.dumps(finally_data))
        return res


def main(statsd_client, zk, url):
    try:
        zk_data = zk.get_stats()
        put_data = deepcopy(zk_data)
        zk_counter_data = zk.counter_to_gauge(zk_data)
        if q.empty():
            q.put(put_data)
            log.info("Data has been put to the Queue.")

        if zk_counter_data:
            send_to_statsd(statsd_client, zk_counter_data)
            send_to_falcon(url, zk_counter_data)

    except [
        requests.exceptions.ReadTimeout,
        requests.exceptions.ConnectTimeout,
    ] as e:
        log.error(e)

    except Exception as e:
        log.error(e)
        print_exc()


if __name__ == '__main__':
    myDaemon = MyDaemon(pidfile=PID_FILE,
                        stderr=STDERR,
                        )
    args = sys.argv
    if len(args) == 2:
        if 'start' == args[1]:
            myDaemon.start()
        elif 'stop' == args[1]:
            myDaemon.stop()
        elif 'restart' == args[1]:
            myDaemon.restart()
        else:
            log.error('*** Unknown command')
            sys.exit(2)
        sys.exit(0)
    else:
        print('Usage: {} start|stop|restart'.format(args[0]))
        sys.exit(2)
