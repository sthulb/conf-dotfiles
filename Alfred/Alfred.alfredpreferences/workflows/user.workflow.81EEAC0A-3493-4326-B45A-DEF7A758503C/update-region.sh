#!/usr/bin/env bash

set -ex

rm -f regional-product-services.html
http --download 'https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/'
pipenv run python parse-regions.py
