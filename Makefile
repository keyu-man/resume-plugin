SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

OPENCLAW ?= openclaw
PLUGIN_ID ?= resume-plugin
SKILL_NAME ?= resume-pdf-import
PROJECT_ROOT := $(CURDIR)
SKILL_SOURCE_DIR := $(PROJECT_ROOT)/skills/$(SKILL_NAME)
SKILL_REQUIREMENTS := $(SKILL_SOURCE_DIR)/scripts/requirements.txt
INSTALL_SKILL_SCRIPT := $(PROJECT_ROOT)/scripts/install_openclaw_skill.py

.PHONY: install-openclaw install-openclaw-restart install-openclaw-plugin install-openclaw-skill install-openclaw-skill-deps npm-deps openclaw-status

install-openclaw: npm-deps install-openclaw-plugin install-openclaw-skill install-openclaw-skill-deps openclaw-status
	@echo "OpenClaw plugin and skill are synced."
	@echo "Run 'make install-openclaw-restart' if the gateway is already running."

install-openclaw-restart: install-openclaw
	$(OPENCLAW) gateway restart

npm-deps:
	npm install

install-openclaw-plugin:
	$(OPENCLAW) plugins install -l "$(PROJECT_ROOT)"

install-openclaw-skill:
	python3 "$(INSTALL_SKILL_SCRIPT)" \
		--openclaw "$(OPENCLAW)" \
		--skill-name "$(SKILL_NAME)" \
		--source "$(SKILL_SOURCE_DIR)"

install-openclaw-skill-deps:
	python3 -m pip install --user -r "$(SKILL_REQUIREMENTS)"

openclaw-status:
	$(OPENCLAW) plugins info "$(PLUGIN_ID)"
	$(OPENCLAW) skills info "$(SKILL_NAME)"
