BP_DIR := kit_crafting_bp
RP_DIR := kit_crafting_rp
BP_MANIFEST := $(BP_DIR)/manifest.json
RP_MANIFEST := $(RP_DIR)/manifest.json
DIST_DIR := dist
PACK_NAME := Kit-Crafting
MINECRAFT_DATA_DIR ?= /Users/$(shell id -un)/Library/Application Support/minecraftpe/games/com.mojang
DEV_BP_DIR := $(MINECRAFT_DATA_DIR)/development_behavior_packs/KitCrafting
DEV_RP_DIR := $(MINECRAFT_DATA_DIR)/development_resource_packs/KitCrafting-Resources

VERSION = $(shell jq -er '.header.version | map(tostring) | join(".")' "$(BP_MANIFEST)")
BP_PACKAGE = $(DIST_DIR)/$(PACK_NAME)-BP-$(VERSION).mcpack
RP_PACKAGE = $(DIST_DIR)/$(PACK_NAME)-RP-$(VERSION).mcpack
ADDON = $(DIST_DIR)/$(PACK_NAME)-$(VERSION).mcaddon
BP_PACKAGE_ABS = $(abspath $(BP_PACKAGE))
RP_PACKAGE_ABS = $(abspath $(RP_PACKAGE))

.DEFAULT_GOAL := package

.PHONY: package site publish install-dev validate version bump-patch bump-minor bump-major release-patch release-minor release-major

package: validate
	@mkdir -p "$(DIST_DIR)"
	@cd "$(BP_DIR)" && zip -qFSr "$(BP_PACKAGE_ABS)" . -x '*.DS_Store' '*.tmp'
	@cd "$(RP_DIR)" && zip -qFSr "$(RP_PACKAGE_ABS)" . -x '*.DS_Store' '*.tmp'
	@zip -qjFS "$(ADDON)" "$(BP_PACKAGE)" "$(RP_PACKAGE)"
	@unzip -tq "$(ADDON)"
	@echo "Built $(ADDON)"

site: package
	@python3 scripts/build_site.py

publish: site
	@test -z "$$(git status --porcelain)" || { echo 'Commit your changes before publishing.'; exit 1; }
	@test "$$(git branch --show-current)" = main || { echo 'Publish from main.'; exit 1; }
	@git tag "v$(VERSION)"
	@git push --atomic origin main "v$(VERSION)"
	@echo "Publishing v$(VERSION): https://github.com/stuartleigh/kit-crafting/actions"

install-dev: validate
	@mkdir -p "$(DEV_BP_DIR)" "$(DEV_RP_DIR)"
	@rsync -a --delete "$(BP_DIR)/" "$(DEV_BP_DIR)/"
	@rsync -a --delete "$(RP_DIR)/" "$(DEV_RP_DIR)/"
	@echo "Installed development packs at $(DEV_BP_DIR) and $(DEV_RP_DIR)"

validate:
	@find "$(BP_DIR)" "$(RP_DIR)" -type f -name '*.json' -print0 | xargs -0 -n1 jq empty

version:
	@echo "$(VERSION)"

bump-patch:
	@tmp="$(BP_MANIFEST).tmp"; \
	jq '.header.version[2] += 1 | .modules[].version = .header.version | .dependencies[].version = .header.version' "$(BP_MANIFEST)" > "$$tmp" && \
	mv "$$tmp" "$(BP_MANIFEST)"
	@tmp="$(RP_MANIFEST).tmp"; \
	jq '.header.version[2] += 1 | .modules[].version = .header.version' "$(RP_MANIFEST)" > "$$tmp" && \
	mv "$$tmp" "$(RP_MANIFEST)"
	@echo "Version bumped to $$(jq -r '.header.version | join(".")' "$(BP_MANIFEST)")"

bump-minor:
	@tmp="$(BP_MANIFEST).tmp"; \
	jq '.header.version = [.header.version[0], (.header.version[1] + 1), 0] | .modules[].version = .header.version | .dependencies[].version = .header.version' "$(BP_MANIFEST)" > "$$tmp" && \
	mv "$$tmp" "$(BP_MANIFEST)"
	@tmp="$(RP_MANIFEST).tmp"; \
	jq '.header.version = [.header.version[0], (.header.version[1] + 1), 0] | .modules[].version = .header.version' "$(RP_MANIFEST)" > "$$tmp" && \
	mv "$$tmp" "$(RP_MANIFEST)"
	@echo "Version bumped to $$(jq -r '.header.version | join(".")' "$(BP_MANIFEST)")"

bump-major:
	@tmp="$(BP_MANIFEST).tmp"; \
	jq '.header.version = [(.header.version[0] + 1), 0, 0] | .modules[].version = .header.version | .dependencies[].version = .header.version' "$(BP_MANIFEST)" > "$$tmp" && \
	mv "$$tmp" "$(BP_MANIFEST)"
	@tmp="$(RP_MANIFEST).tmp"; \
	jq '.header.version = [(.header.version[0] + 1), 0, 0] | .modules[].version = .header.version' "$(RP_MANIFEST)" > "$$tmp" && \
	mv "$$tmp" "$(RP_MANIFEST)"
	@echo "Version bumped to $$(jq -r '.header.version | join(".")' "$(BP_MANIFEST)")"

release-patch: bump-patch
	@$(MAKE) package

release-minor: bump-minor
	@$(MAKE) package

release-major: bump-major
	@$(MAKE) package
