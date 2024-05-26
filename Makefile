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
