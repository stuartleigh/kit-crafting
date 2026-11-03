MOD ?= kit-crafting
MINECRAFT_DATA_DIR ?= /Users/$(shell id -un)/Library/Application Support/minecraftpe/games/com.mojang

.DEFAULT_GOAL := package
.PHONY: package site publish install-dev validate chaos test version tag bump-patch bump-minor bump-major release-patch release-minor release-major

package:
	@python3 scripts/packs.py package

site: package
	@python3 scripts/build_site.py

publish: test site
	@test -z "$$(git status --porcelain)" || { echo 'Commit your changes before publishing.'; exit 1; }
	@test "$$(git branch --show-current)" = main || { echo 'Publish from main.'; exit 1; }
	@git tag "$$(python3 scripts/packs.py tag --mod "$(MOD)")"
	@git push --atomic origin main "$$(python3 scripts/packs.py tag --mod "$(MOD)")"
	@echo "Publishing $(MOD): https://github.com/stuartleigh/kit-crafting/actions"

install-dev: validate
	@python3 scripts/packs.py install-dev --data-dir "$(MINECRAFT_DATA_DIR)"

validate:
	@python3 scripts/generate_chaos.py --check
	@python3 scripts/packs.py validate

chaos:
	@python3 scripts/generate_chaos.py

test:
	@node --test tests/*.test.mjs
	@python3 -m unittest discover -s tests -p 'test_*.py'

version tag:
	@python3 scripts/packs.py $@ --mod "$(MOD)"

bump-patch bump-minor bump-major:
	@python3 scripts/packs.py $@ --mod "$(MOD)"

release-patch: bump-patch
	@$(MAKE) package

release-minor: bump-minor
	@$(MAKE) package

release-major: bump-major
	@$(MAKE) package
