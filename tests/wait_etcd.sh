#!/bin/sh

etcd_host="127.0.0.1"
etcd_port=4001

while true; do
    port_test=$(nc -vz $etcd_host $etcd_port 2>&1|grep "Connection refused")
    if [ "$port_test" != "" ]; then
        echo "$(date) - waiting for etcd start up..."
        sleep 1
    else
        echo "Connection with etcd $etcd_host:$etcd_port successfully..."
        break
    fi
done
