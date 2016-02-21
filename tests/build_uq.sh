#!/bin/sh -e

ORG_PATH="github.com/buaazp"
REPO_PATH="${ORG_PATH}/uq"

export GOPATH=${PWD}/gopath

go get -u $REPO_PATH

cd /tmp
git clone https://$REPO_PATH
cd uq
go build
cp uq /tmp/bin/
