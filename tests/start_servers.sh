#!/bin/sh

mkdir -p /tmp/http8001 /tmp/http8002 /tmp/http8003
cd /tmp/http8001
uq -protocol http -port 8001 -admin-port 8101 &
cd /tmp/http8002
uq -protocol redis -port 8002 -admin-port 8102 &
cd /tmp/http8003
uq -protocol mc -port 8003 -admin-port 8103 &

mkdir -p /tmp/etcd4001
cd /tmp/etcd4001
etcd &
wait_etcd.sh

mkdir -p /tmp/http_cluster
cd /tmp/http_cluster
uq -port 8011 -admin-port 8111 -dir ./uq1 -etcd http://127.0.0.1:4001 -cluster uq -protocol http &
uq -port 8012 -admin-port 8112 -dir ./uq2 -etcd http://127.0.0.1:4001 -cluster uq -protocol http &
uq -port 8013 -admin-port 8113 -dir ./uq3 -etcd http://127.0.0.1:4001 -cluster uq -protocol http &
