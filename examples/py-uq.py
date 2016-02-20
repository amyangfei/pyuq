# coding: utf-8

import logging
import datetime
import argparse

from uq.client import UqClient, UqClusterClient


def _strip(value):
    return value.strip('\r\n') if hasattr(value, 'strip') else value


def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', default='127.0.0.1', help='uq server ip address')
    parser.add_argument('--port', type=int, default=8808, help='uq server port')
    parser.add_argument('--protocol', default='http', choices=['redis', 'http', 'mc'], help='fronent interface')
    parser.add_argument('--etcd', default='', help='etcd service location')
    parser.add_argument('--cluster', default='uq', help='cluster name in etcd')
    parser.add_argument('--topic', default='foo', help='topic name')
    parser.add_argument('--line', default='x', help='line name')
    return parser.parse_args()


def main(args):
    if args.etcd == '':
        cli = UqClient(args.protocol, args.ip, args.port)
    else:
        kwargs = {}
        if args.etcd.startswith('http'):
            kwargs['_etcd_protocol'] = args.etcd[:args.etcd.index(':')]
            netloc = args.etcd[args.etcd.index('://')+3:]
        else:
            netloc = args.etcd
        if ':' in netloc:
            etcd_host = netloc[:netloc.index(':')]
            etcd_port = int(netloc[netloc.index(':')+1:])
        else:
            etcd_host = netloc
            etcd_port = 4001
        cli = UqClusterClient(
            args.protocol, etcd_host, etcd_port, args.cluster, **kwargs)

    recycle = datetime.timedelta(seconds=10)
    success, info = cli.add(args.topic, '', 0)
    if not success:
        if 'Existed' not in info:
            logging.error('add error: {}'.format(_strip(info)))
            return
    logging.info('add topic: {}'.format(_strip(info)))

    success, info = cli.add(args.topic, args.line, recycle)
    if not success:
        if 'Existed' not in info:
            logging.error('add error: {}'.format(_strip(info)))
            return
    logging.info('add topic: {}'.format(_strip(info)))

    value = 'hello'.encode()
    success, info = cli.push(args.topic, value)
    if not success:
        logging.error('push error: {}'.format(_strip(info)))
        return
    logging.info('push to topic: {}'.format(_strip(info)))

    key = args.topic + '/' + args.line
    success, cid, data = cli.pop(key)
    if not success:
        logging.error('pop error: {}'.format(_strip(data)))
        return
    logging.info('pop from topic: {} {}'.format(cid, _strip(data)))

    success, info = cli.remove(cid)
    if not success:
        logging.error('del error: {}'.format(_strip(info)))
        return
    logging.info('del from topic: {}'.format(_strip(info)))

    logging.info('all test finished')

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(module)s/%(funcName)s %(levelname)s "%(message)s"', level=logging.INFO)
    logging.getLogger("requests").setLevel(logging.WARNING)
    args = parseargs()
    main(args)
