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

stage:
	@echo "Staging files added or modified by rsync..."
	@cd $(EXAMPLES) && \
		(cd $(LANGROID) && git ls-files) | $(SYNC_CMD_AI) $(LANGROID)/ $(EXAMPLES)/ | grep '^>f' | \
		sed -n 's/^>f[^ ]* *//p' | xargs -r git add

stage-dry:
	@echo "Files that would be staged:"
	@cd $(EXAMPLES) && \
		(cd $(LANGROID) && git ls-files) | $(SYNC_CMD_AI) $(LANGROID)/ $(EXAMPLES)/ | grep '^>f' | \
		sed -n 's/^>f[^ ]* *//p'