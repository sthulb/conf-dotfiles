#!/usr/bin/env zsh
set -ex

declare -a services

services=(${(f)"$(
aws ssm get-parameters-by-path \
	--path /aws/service/global-infrastructure/regions/us-east-1/services \
	--query 'Parameters[].Name' \
	--output json \
	| jq -r '.[]' \
	| awk -F/ '{print $NF}'
)"})

for service in $services; do
	aws ssm get-parameters-by-path \
		--path "/aws/service/global-infrastructure/services/$service" \
		--query 'Parameters[?ends_with(Name, `longName`)].Value' \
		--output text
done
