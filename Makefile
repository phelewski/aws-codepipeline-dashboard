MAKEFLAGS += --silent
include .env

## Bump Version
bump-version:
	bump2version patch scripts/deploy.py

## Deploy Stack
deploy: validate bump-version
	python scripts/deploy.py $(STACK_NAME) $(BUCKET) $(CFN_TEMPLATE) $(PIPELINE_PATTERN)

## Tests
cfn-nag:
	cfn_nag_scan --input-path $(CFN_TEMPLATE)

validate: validate-profile validate-stack cfn-nag

validate-profile:
	aws sts get-caller-identity > /dev/null

validate-stack:
	aws cloudformation validate-template --template-body file://$(CFN_TEMPLATE) > /dev/null
