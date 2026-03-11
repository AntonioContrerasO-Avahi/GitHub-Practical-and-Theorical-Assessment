.PHONY: help setup infra-up infra-down run clean

TERRAFORM_DIR := terraform
export PATH := /opt/homebrew/opt/util-linux/bin:$(PATH)

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "  setup       Copy .env.example → .env (edit it before continuing)"
	@echo "  infra-up    Terraform init + apply — provision S3 bucket"
	@echo "  infra-down  Terraform destroy — tear down S3 bucket"
	@echo "  run         Source .env and execute nightly_eval.sh"
	@echo "  clean       Remove logs/ and any leftover /tmp/nightly_eval_* dirs"

setup:
	@if [ -f .env ]; then \
		echo ".env already exists — edit it directly if needed"; \
	else \
		cp .env.example .env; \
		echo "Created .env from .env.example — fill in S3_BUCKET and SLACK_WEBHOOK_URL, then run: make infra-up"; \
	fi

infra-up:
	@[ -f .env ] || { echo "ERROR: .env not found. Run: make setup"; exit 1; }
	$(eval include .env)
	$(eval export)
	cd $(TERRAFORM_DIR) && tofu init -input=false
	cd $(TERRAFORM_DIR) && set -a && . ../.env && set +a && \
		tofu apply -auto-approve \
		  -var="bucket_name=$$S3_BUCKET" \
		  -var="aws_region=$$AWS_REGION" \
		  -var="environment=$${PIPELINE_ENV:-dev}"
	@echo ""
	@echo "Done. Bucket name:"
	@cd $(TERRAFORM_DIR) && tofu output -raw bucket_name

infra-down:
	@[ -f .env ] || { echo "ERROR: .env not found. Run: make setup"; exit 1; }
	cd $(TERRAFORM_DIR) && set -a && . ../.env && set +a && \
		tofu destroy -auto-approve \
		  -var="bucket_name=$$S3_BUCKET" \
		  -var="aws_region=$$AWS_REGION" \
		  -var="environment=$${PIPELINE_ENV:-dev}"

run:
	@[ -f .env ] || { echo "ERROR: .env not found. Run: make setup"; exit 1; }
	set -a && . ./.env && set +a && bash nightly_eval.sh

clean:
	rm -rf logs/
	rm -f /tmp/nightly_eval.lock
