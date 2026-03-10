# Issue 001: Hosted agents sample cannot run locally

**Status:** Open
**Date:** 2026-03-10
**Sample:** `samples/05-end-to-end/hosted_agents/agent_with_hosted_mcp`

## Description

The hosted agent sample (`agent_with_hosted_mcp`) fails to run locally due to dependency conflicts between `azure-ai-agentserver-agentframework` and the local development version of `agent-framework-core` / `agent-framework-azure-ai`.

## Steps to Reproduce

1. Activate the local `.venv`
2. Run:
   ```powershell
   cd samples/05-end-to-end/hosted_agents/agent_with_hosted_mcp
   uv run --with azure-ai-agentserver-agentframework --with python-dotenv python main.py
   ```

## Error

```
File "agent_framework_azure_ai/_client.py", line 21, in <module>
    from azure.ai.projects.models import (
ImportError: cannot import name 'PromptAgentDefinitionText' from 'azure.ai.projects.models'
```

## Root Cause

`azure-ai-agentserver-agentframework` (v1.0.0b13) depends on an older version of `agent-framework` from PyPI (v1.0.0b260107), which expects `PromptAgentDefinitionText` in `azure.ai.projects.models`. The local development version (v1.0.0rc3) has moved beyond this API.

When using `uv run --with`, an isolated environment is created that pulls the PyPI version instead of the local editable install, causing the mismatch.

Installing `azure-ai-agentserver-agentframework` directly into the local `.venv` via `uv pip install` also breaks the environment by downgrading `agent-framework-core` and `agent-framework-azure-ai` to older PyPI versions.

## Impact

- Cannot test hosted agent samples locally during development
- The `from_agent_framework(agent).run()` call requires the AgentServer runtime, which is only available in Azure-hosted environments

## Possible Solutions

1. Update `azure-ai-agentserver-agentframework` to be compatible with the latest `agent-framework-core` rc3
2. Provide a local AgentServer emulator for development
3. Add documentation clarifying that hosted agent samples are deploy-only and cannot run locally
