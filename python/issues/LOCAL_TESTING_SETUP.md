# Local Testing Setup: Agent Framework + AgentServer

How to set up and test the latest `agent-framework` (rc3) with `azure-ai-agentserver-agentframework` on a local machine.

## Prerequisites

- **Python** 3.12+
- **uv** (Python package manager) — install via `pip install uv` or https://docs.astral.sh/uv/
- **Azure CLI** — `az login` with access to an Azure AI Foundry project
- **Git**

### Azure Resources

You need an Azure AI Foundry project with:
- An OpenAI model deployment (e.g., `gpt-5.1`) that supports the Responses API
- `DefaultAzureCredential` access (your logged-in Azure CLI identity must have contributor/user roles on the project)

## 1. Clone Repositories

```powershell
# Agent Framework (main branch)
git clone https://github.com/microsoft/agent-framework.git
cd agent-framework/python

# In a separate directory, clone the agentserver fork with rc3 compat fixes
git clone https://github.com/1openwindow/azure-sdk-for-python.git
cd azure-sdk-for-python
git checkout zihch/agentserver-rc3-compat
```

> **Why the fork?** The official `azure-ai-agentserver-agentframework` (b15) is incompatible with
> `agent-framework-core` rc3 due to breaking API changes. The fork branch `zihch/agentserver-rc3-compat`
> patches all 20 affected files. See [Issue 003](issues/003-agentserver-agentframework-rc3-compat.md).

## 2. Set Up the Virtual Environment

From the `agent-framework/python` directory:

```powershell
cd <path-to>/agent-framework/python

# Create venv and install all agent-framework packages (editable)
uv venv --python 3.12
uv run poe setup --python=3.12
```

This installs all `agent-framework-*` packages as editable from source.

## 3. Install AgentServer Packages (Editable)

Install the patched agentserver packages into the same venv:

```powershell
# Activate the venv
.venv\Scripts\Activate.ps1    # Windows PowerShell
# source .venv/bin/activate   # Linux/macOS

# Install agentserver-core and agentserver-agentframework from the fork
uv pip install -e <path-to>/azure-sdk-for-python/sdk/agentserver/azure-ai-agentserver-core
uv pip install -e <path-to>/azure-sdk-for-python/sdk/agentserver/azure-ai-agentserver-agentframework
```

## 4. Configure Environment Variables

Create a `.env` file in `agent-framework/python/`:

```env
# Azure AI Foundry project endpoint (used by ResponsesClient)
AZURE_AI_PROJECT_ENDPOINT="https://<your-resource>.services.ai.azure.com/api/projects/<your-project>"

# Azure OpenAI endpoint (used by ChatClient — currently has 401 issues, see Issue 003)
AZURE_OPENAI_ENDPOINT="https://<your-resource>.openai.azure.com/"

# Model deployment names
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME="gpt-5.1"
AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME="gpt-5.1"
```

### How to find your endpoints

1. Go to [Azure AI Foundry](https://ai.azure.com) → your project → **Overview**
2. **Project endpoint:** Copy the "Project endpoint" — format: `https://<resource>.services.ai.azure.com/api/projects/<project>`
3. **OpenAI endpoint:** Go to your connected Azure OpenAI resource — format: `https://<resource>.openai.azure.com/`

## 5. Authenticate

```powershell
az login
```

`DefaultAzureCredential` will pick up your Azure CLI session. Make sure your identity has the appropriate RBAC roles on the AI Foundry project.

## 6. Verify Installation

```powershell
# Activate venv
.venv\Scripts\Activate.ps1

# Check key packages are installed
python -c "import agent_framework; print('agent-framework OK')"
python -c "from azure.ai.agentserver.agentframework import from_agent_framework; print('agentserver OK')"
python -c "from azure.identity import DefaultAzureCredential; print('azure-identity OK')"
```

## 7. Run the Unit Tests

```powershell
# Agent Framework tests
uv run poe test

# AgentServer tests
cd <path-to>/azure-sdk-for-python/sdk/agentserver/azure-ai-agentserver-agentframework
python -m pytest tests/unit_tests/ -v
```

All 12 agentserver unit tests should pass.

## 8. Run Samples

### Hello Agent (basic connectivity test)

```powershell
cd <path-to>/agent-framework/python
python samples/01-get-started/01-hello-agent/hello_agent.py
```

### Hosted Agent with MCP

```powershell
python samples/05-end-to-end/hosted_agents/agent_with_hosted_mcp/main.py
```

This starts a local HTTP server on port 8088. Test it:

```powershell
# In another terminal
$body = @{ message = "Hello" } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8088 -Method Post -Body $body -ContentType "application/json"
```

Stop the server with `Ctrl+C`.

## Known Issues

| Issue | Status | Workaround |
|---|---|---|
| `AzureOpenAIChatClient` returns 401 with `DefaultAzureCredential` | Open | Use `AzureOpenAIResponsesClient` with `project_endpoint` instead |
| agentserver b15 incompatible with agent-framework rc3 | Patched | Use fork branch `zihch/agentserver-rc3-compat` |

See the [issues folder](issues/) for full details.

## Package Versions (tested)

| Package | Version | Source |
|---|---|---|
| `agent-framework-core` | 1.0.0rc3 | Editable (local) |
| `agent-framework-azure-ai` | 1.0.0rc3 | Editable (local) |
| `azure-ai-agentserver-agentframework` | 1.0.0b1 (patched) | Editable (fork) |
| `azure-ai-agentserver-core` | 1.0.0b1 | Editable (fork) |
| `azure-identity` | 1.25.2 | PyPI |
| `openai` | 2.26.0 | PyPI |
| Python | 3.12.10 | — |
| uv | 0.10.9 | — |
