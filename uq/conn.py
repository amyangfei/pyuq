# coding: utf-8

import random
import logging
import functools

import etcd
import requests

from .exceptions import UqError, UqNotImplementedError
from .consts import MaxRetry
from .utils import timedetla_to_str


def query_addrs(etcd_cli, etcd_key):
    try:
        resp = etcd_cli.read('/{}/servers'.format(etcd_key), sorted=True, recursive=False)
    except etcd.EtcdKeyNotFound:
        raise
    if not resp.dir:
        raise UqError('invalid etcd key')
    for child in resp.children:
        yield child.key.split('/')[-1]


class Conn(object):
    '''
    Base class of connection from uq client to uq server.
    '''

    def __init__(self, addr, etcd_cli, etcd_key):
        self.addr = addr
        self.etcd_cli = etcd_cli
        self.etcd_key = etcd_key
        self.addrs = None
        self._update_conn_pool()

    def _update_conn_pool(self):
        raise UqNotImplementedError

    def _add(addr, data):
        raise UqNotImplementedError

    def _push(addr, data):
        raise UqNotImplementedError

    def _pop(addr, data):
        raise UqNotImplementedError

    def _remove(addr, data):
        raise UqNotImplementedError

    def add(self, topic, line, recycle):
        if not topic:
            raise UqError('topic is empty')
        updated = False
        while True:
            retry = 0
            while retry < MaxRetry:
                addr = self._choose()
                data = {
                    'topic': topic,
                    'line': line,
                    'recycle': timedetla_to_str(recycle),
                }
                if addr is None:
                    logging.error('no uq server available')
                else:
                    result = self._add(addr, data)
                if result is None:
                    retry += 1
                else:
                    return result

            if not updated:
                self._update_conn_pool()
                updated = True
            else:
                break

        return False, 'all conn add failed after retry'

    def push(self, key, value):
        updated = False
        while True:
            retry = 0
            while retry < MaxRetry:
                addr = self._choose()
                if addr is None:
                    logging.error('no uq server available')
                else:
                    data = {
                        'key': key,
                        'value': value,
                    }
                    result = self._push(addr, data)
                    if result is None:
                        retry += 1
                    else:
                        return result
                retry += 1

            if not updated:
                self._update_conn_pool()
                updated = True
            else:
                break

        return False, 'all conn push failed after retry'

    def pop(self, key):
        updated = False
        while True:
            retry = 0
            while retry < MaxRetry:
                data = {'key': key}
                result = self._pop(self.addrs, data)
                if result is None:
                    retry += 1
                else:
                    return result

            if not updated:
                self._update_conn_pool()
                updated = True
            else:
                break

        return False, '', 'all conn pop failed after retry'

    def remove(self, key):
        values = key.split('/', 1)
        if len(values) != 2:
            return False, 'key illegal'
        addr, cid = values

        retry = 0
        while retry < MaxRetry:
            data = {'cid': cid}
            result = self._remove(addr, data)
            if result is None:
                retry += 1
            else:
                return result
            retry += 1

        return False, 'all conn del failed after retry'


def catch_requests_error(func):
    @functools.wraps(func)
    def wrap_f(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.RequestException, e:
            logging.error('requests error: {}'.format(e))
            return None
    return wrap_f


class HttpConn(Conn):
    '''
    Http protocol based connection between uq client and uq server
    '''

    def __init__(self, addr, etcd_cli, etcd_key):
        super(HttpConn, self).__init__(addr, etcd_cli, etcd_key)

    def _choose(self):
        if len(self.addrs) == 0:
            return None
        return random.choice(self.addrs)

    def _update_conn_pool(self):
        if self.etcd_cli is None:
            self.addrs = [self.addr]
        else:
            self.addrs = [x for x in query_addrs(self.etcd_cli, self.etcd_key)]

    @catch_requests_error
    def _add(self, addr, data):
        url = 'http://{0}/v1/queues'.format(addr)
        r = requests.put(url, data)
        if r.status_code == requests.codes.created:
            return True, ''
        else:
            if 'Existed' in r.text:
                return False, r.text
            logging.error('add error: {}'.format(r.text))
            return None

    @catch_requests_error
    def _push(self, addr, data):
        key = data.pop('key')
        url = 'http://{0}/v1/queues/{1}'.format(addr, key)
        r = requests.post(url, data)
        if r.status_code == requests.codes.no_content:
            return True, ''
        else:
            logging.error('push error: {}'.format(r.text))
            return None

    @catch_requests_error
    def _pop(self, addrs, data):
        nomsg = 0
        for addr in self.addrs:
            url = 'http://{0}/v1/queues/{1}'.format(addr, data['key'])
            r = requests.get(url)
            if r.status_code == requests.codes.not_found:
                nomsg += 1
            elif r.status_code == requests.codes.ok:
                cid = '{}/{}'.format(addr, r.headers.get('X-UQ-ID'))
                value = r.text
                return True, cid, value
            else:
                logging.error('pop error: {}'.format(r.text))
        if nomsg == len(self.addrs):
            return False, '', 'no message'
        return None

    @catch_requests_error
    def _remove(self, addr, data):
        url = 'http://{0}/v1/queues/{1}'.format(addr, data['cid'])
        r = requests.delete(url)
        if r.status_code == requests.codes.no_content:
            return True, ''
        else:
            logging.error('del error: {}'.format(r.text))
            return None


class RedisConn(Conn):
    '''
    RESP protocol based connection between uq client and uq server
    '''

    def __init__(self, addr, etcd_cli, etcd_key):
        super(RedisConn, self).__init__(addr, etcd_cli, etcd_key)

    def add(self, topic, line, recycle):
        pass

    def push(self, key, value):
        pass

    def pop(self, key):
        pass

    def remove(self, key):
        pass


class MemcacheConn(Conn):
    '''
    Memcache protocol based connection between uq client and uq server
    '''

    def __init__(self, addr, etcd_cli, etcd_key):
        super(MemcacheConn, self).__init__(addr, etcd_cli, etcd_key)

    def add(self, topic, line, recycle):
        pass

    def push(self, key, value):
        pass

    def pop(self, key):
        pass

    def remove(self, key):
        pass
