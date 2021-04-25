MAKEFLAGS += --silent
include .env

## Bump Version
bump-patch: bump-patch-version automated-version-git-add automated-patch-version-commit

bump-minor: bump-minor-version automated-version-git-add automated-minor-version-commit

bump-major: bump-major-version automated-version-git-add automated-major-version-commit

bump-patch-version:
	bump2version patch scripts/deploy.py

bump-minor-version:
	bump2version minor scripts/deploy.py

bump-major-version:
	bump2version major scripts/deploy.py

automated-version-git-add:
	git add .bumpversion.cfg
	git add scripts/deploy.py
	
automated-patch-version-commit:
	git commit -m "Automated: Bumping lambda package version to $(shell bump2version --allow-dirty --dry-run --list patch | grep current_version | sed -r s,"^.*=",,)"

automated-minor-version-commit:
	git commit -m "Automated: Bumping lambda package version to $(shell bump2version --allow-dirty --dry-run --list minor | grep current_version | sed -r s,"^.*=",,)"

automated-major-version-commit:
	git commit -m "Automated: Bumping lambda package version to $(shell bump2version --allow-dirty --dry-run --list major | grep current_version | sed -r s,"^.*=",,)"

## Deploy Stack
deploy: validate deployment-script

deploy-patch: validate bump-patch deployment-script

deploy-minor: validate bump-minor deployment-script

deploy-major: validate bump-major deployment-script

deployment-script:
	python scripts/deploy.py $(STACK_NAME) $(BUCKET) $(CFN_TEMPLATE) $(PIPELINE_PATTERN)

## Tests
cfn-nag:
	cfn_nag_scan --input-path $(CFN_TEMPLATE)

test:
	python -m pytest --cov=src --cov-report term-missing tests

validate: validate-profile validate-stack cfn-nag

validate-profile:
	aws sts get-caller-identity > /dev/null

validate-stack:
	aws cloudformation validate-template --template-body file://$(CFN_TEMPLATE) > /dev/null
