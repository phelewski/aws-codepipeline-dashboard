MAKEFLAGS += --silent
include .env

## Bump Version
bump-version: bump2version automated-version-commit

bump2version:
	bump2version patch scripts/deploy.py

automated-version-commit:
	git add .bumpversion.cfg
	git add scripts/deploy.py
	git commit -m "Automated: Bumping lambda package version to $(shell bump2version --allow-dirty --dry-run --list patch | grep current_version | sed -r s,"^.*=",,)"

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
