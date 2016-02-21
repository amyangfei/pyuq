# coding: utf-8

import unittest
import datetime

import uq


class TestUqClientApi(unittest.TestCase):

    def check_default_resp(self, resp):
        self.assertIsInstance(resp, tuple)
        self.assertEqual(len(resp), 2)
        self.assertEqual(resp[0], True)
        self.assertEqual(resp[1], '')

    def test_http_api(self):
        cli = uq.UqClient(protocol='http', ip='localhost', port='8001')
        r = cli.add('foo')
        self.check_default_resp(r)
        r = cli.add('foo', 'x', datetime.timedelta(seconds=10))
        self.check_default_resp(r)
        r = cli.push('foo', 'hello')
        self.check_default_resp(r)
        r = cli.pop('foo/x')
        self.assertEqual(r[2], 'hello')
        r = cli.remove(r[1])
        self.check_default_resp(r)
