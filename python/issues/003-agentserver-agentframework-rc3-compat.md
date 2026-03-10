# Issue 003: azure-ai-agentserver-agentframework incompatible with agent-framework rc3

| | |
|---|---|
| **Status** | In Progress (workaround available) |
| **Date** | 2026-03-10 |
| **Component** | `azure-ai-agentserver-agentframework` (b15) + `agent-framework-core` (rc3) |

## Description

`azure-ai-agentserver-agentframework` v1.0.0b15 uses agent-framework APIs that were removed or renamed in rc3. Installing both packages together fails at runtime with `ImportError` and `AttributeError` across 20 source/test files due to breaking API changes in the core framework.

## Breaking API Changes (rc3)

The following renames/removals in `agent-framework-core` rc3 break agentserver-agentframework b15:

| b15 (old API) | rc3 (new API) |
|---|---|
| `AgentProtocol` | `SupportsAgentRun` |
| `AgentThread` | `AgentSession` |
| `get_new_thread()` | `create_session()` |
| `ChatMessage` | `Message` |
| `Role` enum (`Role.USER`, `Role.ASSISTANT`) | String literals (`"user"`, `"assistant"`) |
| `AgentRunResponse` | `AgentResponse` |
| `AgentRunResponseUpdate` | `AgentResponseUpdate` |
| `AIFunction` | `FunctionTool` |
| `RequestInfoEvent` | `WorkflowEvent` |
| `TextContent`, `FunctionCallContent`, `FunctionResultContent` | `Content` class with `.type` field + factory methods |
| `DataContent`, `HostedFileContent`, `UriContent` | `Content.from_data()`, `Content.from_hosted_file()`, `Content.from_uri()` |
| `run_stream(msg, thread=)` | `run(msg, stream=True, session=)` |
| `get_checkpoint_summary` | Removed (use direct attribute/metadata) |
| `WorkflowBuilder()` | Requires `start_executor` param |

## Workaround

A compatibility branch is available at:

- **Repo:** `1openwindow/azure-sdk-for-python`
- **Branch:** `zihch/agentserver-rc3-compat`
- **Commit:** `cc0193e5d6`

This branch updates all 20 affected files (14 source + 6 test) to use rc3 APIs. All 12 unit tests pass.

For the hosted agent sample, use `AzureOpenAIResponsesClient` with `project_endpoint` instead of `AzureOpenAIChatClient`:

```python
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential

agent = AzureOpenAIResponsesClient(
    project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    deployment_name=os.environ["AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME"],
    credential=DefaultAzureCredential(),
).as_agent(name="DocsAgent", instructions="...", tools=mcp_tool)
```

## Files Changed (rc3 compat)

Full diff (20 files, 14 source + 6 test + config): https://github.com/1openwindow/azure-sdk-for-python/commit/cc0193e5d6ff00558b2efeb1f3bd3c99f3cb4170

## Impact

- Cannot use latest agent-framework (rc3) with the agentserver runtime without manual patching
- Blocks local development and testing of hosted agent samples

## Resolution

`azure-ai-agentserver-agentframework` needs a new release that:
1. Updates all imports/types to match agent-framework rc3 APIs
2. Relaxes version pins to accept `>=1.0.0rc3`
