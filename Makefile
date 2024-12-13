# Path Definitions
LANGROID := ~/Git/langroid/examples/
EXAMPLES := ~/Git/langroid-examples/examples/

# Base rsync command
SYNC_CMD := rsync -avc --files-from=-

# Command with itemized changes for rsync
SYNC_CMD_AI := rsync -aivcn --files-from=-

.PHONY: sync sync-dry stage

sync:
	@(cd $(LANGROID) && git ls-files) | $(SYNC_CMD) $(LANGROID)/ $(EXAMPLES)/


sync-dry:
	@echo "Files that would be added or modified by rsync..."
	@(cd $(LANGROID) && git ls-files) | $(SYNC_CMD_AI) $(LANGROID)/ $(EXAMPLES)/ | grep '^>f'


stage-dry:
	@echo "Would add the following modified and newly tracked files to stage:"
	@cd $(EXAMPLES) && echo "Modified files:" && git ls-files -m --exclude-standard
	@cd $(EXAMPLES) && echo "Newly tracked files:" && bash -c "comm -23 <(cd $(LANGROID) && git ls-files | sort) <(cd $(EXAMPLES) && git ls-files | sort)"


stage:
	@echo "Staging modified files..."
	@cd $(EXAMPLES) && git ls-files -m --exclude-standard | xargs -r git add
	@echo "Staging newly tracked files..."
	@cd $(EXAMPLES) && bash -c "comm -23 <(cd $(LANGROID) && git ls-files | sort) <(cd $(EXAMPLES) && git ls-files | sort)" | xargs -r git add

.PHONY: patch minor major

current_version := $(shell grep '^version = ' pyproject.toml | cut -d'"' -f2)

patch:
	@echo "Current version: ${current_version}"
	@new_version=$$(python -c "import semver; print(semver.VersionInfo.parse('${current_version}').bump_patch())") && \
	sed -i '' "s/^version = .*/version = \"$$new_version\"/" pyproject.toml && \
	git add pyproject.toml && \
	git commit -m "Bump version to $$new_version" && \
	git tag -a "v$$new_version" -m "Version $$new_version" && \
	git push && git push --tags

minor:
	@echo "Current version: ${current_version}"
	@new_version=$$(python -c "import semver; print(semver.VersionInfo.parse('${current_version}').bump_minor())") && \
	sed -i '' "s/^version = .*/version = \"$$new_version\"/" pyproject.toml && \
	git add pyproject.toml && \
	git commit -m "Bump version to $$new_version" && \
	git tag -a "v$$new_version" -m "Version $$new_version" && \
	git push && git push --tags

major:
	@echo "Current version: ${current_version}"
	@new_version=$$(python -c "import semver; print(semver.VersionInfo.parse('${current_version}').bump_major())") && \
	sed -i '' "s/^version = .*/version = \"$$new_version\"/" pyproject.toml && \
	git add pyproject.toml && \
	git commit -m "Bump version to $$new_version" && \
	git tag -a "v$$new_version" -m "Version $$new_version" && \
	git push && git push --tags

setup:
	pip install semver