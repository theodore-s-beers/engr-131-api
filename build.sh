#! /usr/bin/env bash

set -Eeuo pipefail

TAG=$(date +%s)

docker buildx build \
	--progress=plain \
	--platform linux/amd64,linux/arm64 \
	--tag katomyomachia/engr-131-api:$TAG \
	--tag katomyomachia/engr-131-api:latest \
	--push .
