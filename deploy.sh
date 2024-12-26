#! /usr/bin/env bash

set -Eeuo pipefail

if ! kubectl get pods -n fastapi &>/dev/null; then
	echo "Error: Are you properly connected to the cluster?"
	exit 1
fi

kubectl apply -f ./k8s-az/ -n fastapi
