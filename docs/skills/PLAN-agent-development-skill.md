# Plan: Reusable Salesforce Agent Development Skill

## Executive Summary

This plan outlines how to make Salesforce Agentforce agent development knowledge reusable for future AI-assisted development sessions. The goal is to enable Claude (or other AI assistants) to effectively help with agent development tasks without requiring manual command lookups or workflow discovery.

## Current State

**What We Have:**
- Comprehensive documentation of `sf agent` commands in `salesforce-agent-development.md`
- Complete command reference with flags, examples, and use cases
- Common workflows for agent development lifecycle
- Troubleshooting guide for known issues

**What's Missing:**
- Skill definition that AI can invoke
- Integration with project-specific workflows
- Templates for common agent patterns
- Automated validation and testing helpers

## Implementation Plan

### Phase 1: Core Skill Definition ✅ COMPLETE

**Status:** Complete - `salesforce-agent-development.md` created

**Deliverables:**
- [x] Command reference documentation
- [x] Common workflows
- [x] Troubleshooting guide
- [x] Quick reference section

**Usage:** AI can read this file to understand available commands and workflows when helping with agent development tasks.

### Phase 2: Project Integration (Recommended Next Steps)

**Goal:** Integrate agent development commands into existing CumulusCI workflows and project structure.

**Tasks:**

1. **Add CumulusCI Tasks for Agent Development**
   
   Add to `cumulusci.yml`:
   ```yaml
   tasks:
     validate_agent:
       description: Validate an Agent Script file compiles successfully
       class_path: cumulusci.tasks.command.SalesforceCommand
       group: Agentforce Development
       options:
         command: sf agent validate authoring-bundle --api-name {api_name}
     
     publish_agent:
       description: Publish an authoring bundle to create/update an agent
       class_path: cumulusci.tasks.command.SalesforceCommand
       group: Agentforce Development
       options:
         command: sf agent publish authoring-bundle --api-name {api_name}
     
     activate_agent:
       description: Activate an agent version
       class_path: cumulusci.tasks.command.SalesforceCommand
       group: Agentforce Development
       options:
         command: sf agent activate --api-name {api_name} --version {version}
     
     deactivate_agent:
       description: Deactivate an agent
       class_path: cumulusci.tasks.command.SalesforceCommand
       group: Agentforce Development
       options:
         command: sf agent deactivate --api-name {api_name}
     
     preview_agent:
       description: Start interactive agent preview session
       class_path: cumulusci.tasks.command.SalesforceCommand
       group: Agentforce Development
       options:
         command: sf agent preview --authoring-bundle {authoring_bundle} --use-live-actions
     
     test_agent:
       description: Run agent tests and output results
       class_path: cumulusci.tasks.command.SalesforceCommand
       group: Agentforce Development
       options:
         command: sf agent test run --api-name {test_name} --wait 10 --result-format json --output-dir test-results
   
   flows:
     validate_and_publish_agent:
       description: Validate and publish an agent (deactivate if needed)
       steps:
         1:
           task: deactivate_agent
           options:
             api_name: $${agent_api_name}
           ignore_failure: True
         2:
           task: validate_agent
           options:
             api_name: $${agent_api_name}
         3:
           task: publish_agent
           options:
             api_name: $${agent_api_name}
         4:
           task: activate_agent
           options:
             api_name: $${agent_api_name}
             version: $${agent_version}
   ```

2. **Update `.forceignore` for Agent Development**
   
   Ensure Agent Script files and authoring bundles are NOT ignored:
   ```
   # Allow aiAuthoringBundles
   !**/aiAuthoringBundles/**
   ```

3. **Document Project-Specific Agent Conventions**
   
   Add to `CLAUDE.md`:
   ```markdown
   ## Agentforce Agent Development
   
   This project uses Agent Script-based development for Agentforce agents.
   
   ### Directory Structure
   - Agent Scripts: `force-app/main/default/aiAuthoringBundles/`
   - Agent Specs: `specs/agents/`
   - Test Specs: `specs/agent-tests/`
   - Published Bots: `force-app/main/default/bots/`
   
   ### Naming Conventions
   - Authoring Bundle API Names: Use RLM_ prefix (e.g., `RLM_Revenue_Quote_Management`)
   - Agent Script Files: `{api_name}.agent`
   - Metadata Files: `{api_name}.bundle-meta.xml`
   
   ### Common Commands
   - Validate: `cci task run validate_agent -o api_name RLM_Revenue_Quote_Management`
   - Publish: `cci flow run validate_and_publish_agent -o agent_api_name RLM_Revenue_Quote_Management -o agent_version 2`
   - Preview: `sf agent preview --authoring-bundle RLM_Revenue_Quote_Management --use-live-actions --target-org dev`
   
   ### Agent Development Workflow
   1. Edit Agent Script file in `aiAuthoringBundles/{api_name}/{api_name}.agent`
   2. Run `cci task run validate_agent -o api_name {api_name}` to check syntax
   3. Preview interactively: `sf agent preview --authoring-bundle {api_name} --use-live-actions`
   4. Publish: `cci flow run validate_and_publish_agent -o agent_api_name {api_name} -o agent_version {num}`
   5. Test: `sf agent preview` or `cci task run test_agent -o test_name {test_api_name}`
   
   ### Reference
   See `docs/skills/salesforce-agent-development.md` for comprehensive sf agent command reference.
   ```

### Phase 3: Agent Templates and Scaffolding (Future)

**Goal:** Provide reusable templates for common agent patterns.

**Tasks:**

1. **Create Agent Template Repository**
   ```
   templates/agents/
   ├── basic-crud-agent/
   │   ├── spec.yaml
   │   └── authoring-bundle/
   │       ├── Agent.bundle-meta.xml
   │       └── Agent.agent
   ├── revenue-cloud-agent/
   │   └── ...
   └── service-agent/
       └── ...
   ```

2. **Create Agent Scaffolding Script**
   ```bash
   # scripts/create_agent.sh
   #!/bin/bash
   # Usage: ./scripts/create_agent.sh <agent-name> <template>
   # Example: ./scripts/create_agent.sh "My Sales Agent" revenue-cloud
   ```

3. **Add Agent Generation Task**
   ```yaml
   tasks:
     create_agent:
       description: Create a new agent from template
       class_path: cumulusci.tasks.command.Command
       options:
         command: ./scripts/create_agent.sh "{agent_name}" "{template}"
   ```

### Phase 4: Automated Testing Integration (Future)

**Goal:** Integrate agent testing into CI/CD pipeline.

**Tasks:**

1. **Create Agent Test Runner Script**
   ```python
   # scripts/run_agent_tests.py
   # - Discovers all agent test specs
   # - Runs tests via sf agent test run
   # - Parses results and fails CI on test failures
   ```

2. **Add GitHub Actions Workflow**
   ```yaml
   # .github/workflows/test-agents.yml
   name: Test Agents
   on: [push, pull_request]
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Authenticate to Salesforce
           run: sf org login jwt ...
         - name: Deploy Agent Actions
           run: cci flow run deploy_agents
         - name: Run Agent Tests
           run: python scripts/run_agent_tests.py
   ```

3. **Add Pre-Commit Hook for Agent Validation**
   ```yaml
   # .pre-commit-config.yaml
   repos:
     - repo: local
       hooks:
         - id: validate-agent-scripts
           name: Validate Agent Scripts
           entry: scripts/validate_agents.sh
           language: script
           files: '\.agent$'
   ```

### Phase 5: AI Assistant Skill Integration (Future)

**Goal:** Make this knowledge directly invokable by Claude Code or other AI assistants.

**Option A: Claude Code Skill Definition**

If Claude Code supports custom skills, create:
```yaml
# .claude/skills/agent-development.yaml
name: agent-development
description: Salesforce Agentforce agent development commands and workflows
documentation: docs/skills/salesforce-agent-development.md
commands:
  - name: validate_agent
    description: Validate an Agent Script file
    command: sf agent validate authoring-bundle --api-name {api_name}
  - name: preview_agent
    description: Preview an agent interactively
    command: sf agent preview --authoring-bundle {api_name} --use-live-actions
  # ... additional commands
```

**Option B: Natural Language Invocation**

When user requests agent development tasks, Claude should:
1. Read `docs/skills/salesforce-agent-development.md` for command reference
2. Check `CLAUDE.md` for project-specific conventions
3. Execute appropriate `sf agent` commands via Bash tool
4. Follow documented workflows for multi-step operations

**User Request Patterns to Recognize:**
- "validate the agent" → `sf agent validate authoring-bundle`
- "preview the agent" → `sf agent preview --authoring-bundle`
- "publish the agent" → deactivate → validate → publish → activate flow
- "test the agent" → `sf agent test run`
- "what agents do we have" → list authoring bundles and published bots

## Success Criteria

### Phase 1 ✅
- [x] Comprehensive command reference documentation exists
- [x] Common workflows are documented
- [x] AI can reference documentation when helping with agent tasks

### Phase 2
- [ ] CumulusCI tasks exist for common agent operations
- [ ] Project documentation includes agent development conventions
- [ ] AI can use `cci` commands for agent operations

### Phase 3
- [ ] Agent templates exist for common patterns
- [ ] Scaffolding script can generate new agents from templates
- [ ] AI can create new agents from templates on request

### Phase 4
- [ ] Agent tests run automatically in CI/CD
- [ ] Pre-commit hooks validate Agent Scripts
- [ ] AI can trigger test runs and interpret results

### Phase 5
- [ ] AI automatically recognizes agent development requests
- [ ] AI follows documented workflows without manual prompting
- [ ] AI provides context-aware suggestions based on project conventions

## Usage Examples

### Current Usage (Phase 1)

**User:** "How do I validate my agent?"

**Claude:** 
```bash
sf agent validate authoring-bundle --api-name <your-agent-api-name> --target-org <org>
```
Reference: `docs/skills/salesforce-agent-development.md` - Validate Commands section.

### After Phase 2

**User:** "Publish the RLM Revenue Quote Management agent"

**Claude:**
```bash
cci flow run validate_and_publish_agent \
  -o agent_api_name RLM_Revenue_Quote_Management \
  -o agent_version 2 \
  --org dev
```
This will deactivate, validate, publish, and activate the agent automatically.

### After Phase 3

**User:** "Create a new sales agent using the revenue cloud template"

**Claude:**
```bash
cci task run create_agent \
  -o agent_name "My Sales Agent" \
  -o template revenue-cloud \
  --org dev
```
Agent created at `force-app/main/default/aiAuthoringBundles/My_Sales_Agent/`

### After Phase 4

**User:** "Run agent tests"

**Claude:**
```bash
python scripts/run_agent_tests.py --org dev
```
All agent tests discovered and executed. Results saved to `test-results/agents/`.

## Maintenance

**Regular Updates:**
- Update `salesforce-agent-development.md` when new `sf agent` commands are added
- Add new workflow examples as team develops new patterns
- Update troubleshooting section with newly discovered issues

**Quarterly Review:**
- Review sf CLI release notes for agent command changes
- Update command syntax if flags change
- Add new features to documentation

**When Onboarding New Team Members:**
- Point them to `docs/skills/salesforce-agent-development.md`
- Review project-specific conventions in `CLAUDE.md`
- Demonstrate common workflows

## Next Steps

1. **Immediate (After Phase 1):**
   - Use `docs/skills/salesforce-agent-development.md` as reference when working with agents
   - When AI helps with agent tasks, it should read this file for command syntax

2. **Short Term (1-2 weeks):**
   - Implement Phase 2: Add CumulusCI tasks and update CLAUDE.md
   - Test the `validate_and_publish_agent` flow with existing agents

3. **Medium Term (1 month):**
   - Create 2-3 agent templates based on common patterns in the project
   - Implement agent scaffolding script

4. **Long Term (2-3 months):**
   - Integrate agent testing into CI/CD pipeline
   - Add pre-commit hooks for agent validation
   - Evaluate AI assistant skill integration options

## Conclusion

This plan establishes a foundation for reusable Salesforce agent development knowledge. Phase 1 provides immediate value through comprehensive documentation. Future phases will progressively enhance automation and AI assistant integration, making agent development faster and more consistent across the team.

The modular approach allows implementation at your own pace while ensuring each phase builds on the previous one. The documentation-first approach ensures knowledge is captured even if advanced automation is never implemented.
