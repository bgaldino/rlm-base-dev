# Makefile — Scratch org creation with dev hub binding
#
# Branch context: 262-test targets internal pre-prod (sdb*) environments.
# DEFAULT_DEVHUB should be updated to devhub-usa794 when:
#   - merging to main at Summer '26 GA, OR
#   - SB0 is updated to Release 262
#
DEFAULT_DEVHUB := devhub-sdb27

.PHONY: help \
        scratch-beta scratch-dev scratch-dev-enhanced scratch-dev-preview scratch-dev-previous scratch-dev-datacloud \
        scratch-dev-sdb6 scratch-dev-sdb9 scratch-dev-sdb27 scratch-dev-sdb39 \
        scratch-dev-sb0 scratch-test-sb0 \
        scratch-tfid scratch-tfid-cdo scratch-tfid-cdo-rlm \
        scratch-tfid-ido-tech scratch-tfid-ido-tech-R2 \
        scratch-tfid-qb-tso scratch-tfid-sdo scratch-tfid-dev scratch-tfid-enable

help:
	@echo "Scratch org targets (devhub bindings):"
	@echo ""
	@echo "  Default devhub ($(DEFAULT_DEVHUB)):"
	@echo "    make scratch-beta"
	@echo "    make scratch-dev"
	@echo "    make scratch-dev-enhanced"
	@echo "    make scratch-dev-preview"
	@echo "    make scratch-dev-previous"
	@echo "    make scratch-dev-datacloud"
	@echo "    make scratch-dev-sdb9"
	@echo "    make scratch-tfid"
	@echo "    make scratch-tfid-cdo"
	@echo "    make scratch-tfid-cdo-rlm"
	@echo "    make scratch-tfid-ido-tech-R2"
	@echo "    make scratch-tfid-qb-tso"
	@echo "    make scratch-tfid-sdo"
	@echo "    make scratch-tfid-dev"
	@echo "    make scratch-tfid-enable"
	@echo ""
	@echo "  Instance-aligned devhubs:"
	@echo "    make scratch-dev-sdb6    (devhub-sdb6)"
	@echo "    make scratch-dev-sdb27   (devhub-sdb27)"
	@echo "    make scratch-dev-sdb39   (devhub-sdb39)"
	@echo ""
	@echo "  devhub-usa794 (SB0 orgs):"
	@echo "    make scratch-dev-sb0"
	@echo "    make scratch-test-sb0"
	@echo "    make scratch-tfid-ido-tech"

# -------------------------------------------------------
# Helper macro: set devhub then create scratch org
# Usage: $(call scratch,<devhub-alias>,<org-alias>)
# -------------------------------------------------------
define scratch
	cci service default devhub $(1) && cci org scratch $(2) --org $(2)
endef

# -------------------------------------------------------
# Default devhub (devhub-sdb27 on 262-test)
# -------------------------------------------------------
scratch-beta:
	$(call scratch,$(DEFAULT_DEVHUB),beta)

scratch-dev:
	$(call scratch,$(DEFAULT_DEVHUB),dev)

scratch-dev-enhanced:
	$(call scratch,$(DEFAULT_DEVHUB),dev_enhanced)

scratch-dev-preview:
	$(call scratch,$(DEFAULT_DEVHUB),dev_preview)

scratch-dev-previous:
	$(call scratch,$(DEFAULT_DEVHUB),dev_previous)

scratch-dev-datacloud:
	$(call scratch,$(DEFAULT_DEVHUB),dev_datacloud)

scratch-dev-sdb9:
	$(call scratch,$(DEFAULT_DEVHUB),dev-sdb9)

scratch-tfid:
	$(call scratch,$(DEFAULT_DEVHUB),tfid)

scratch-tfid-cdo:
	$(call scratch,$(DEFAULT_DEVHUB),tfid-cdo)

scratch-tfid-cdo-rlm:
	$(call scratch,$(DEFAULT_DEVHUB),tfid-cdo-rlm)

scratch-tfid-ido-tech-R2:
	$(call scratch,$(DEFAULT_DEVHUB),tfid-ido-tech-R2)

scratch-tfid-qb-tso:
	$(call scratch,$(DEFAULT_DEVHUB),tfid-qb-tso)

scratch-tfid-sdo:
	$(call scratch,$(DEFAULT_DEVHUB),tfid-sdo)

scratch-tfid-dev:
	$(call scratch,$(DEFAULT_DEVHUB),tfid-dev)

scratch-tfid-enable:
	$(call scratch,$(DEFAULT_DEVHUB),tfid-enable)

# -------------------------------------------------------
# Instance-aligned devhubs
# -------------------------------------------------------
scratch-dev-sdb6:
	$(call scratch,devhub-sdb6,dev-sdb6)

scratch-dev-sdb27:
	$(call scratch,devhub-sdb27,dev-sdb27)

scratch-dev-sdb39:
	$(call scratch,devhub-sdb39,dev-sdb39)

# -------------------------------------------------------
# SB0 orgs — devhub-usa794
# -------------------------------------------------------
scratch-dev-sb0:
	$(call scratch,devhub-usa794,dev-sb0)

scratch-test-sb0:
	$(call scratch,devhub-usa794,test-sb0)

scratch-tfid-ido-tech:
	$(call scratch,devhub-usa794,tfid-ido-tech)
