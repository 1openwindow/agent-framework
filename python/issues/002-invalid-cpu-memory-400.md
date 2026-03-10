# Issue 002: Invalid CPU/memory combination causes 400 on deploy

| | |
|---|---|
| **Status** | Open |
| **Date** | 2026-03-10 |
| **Component** | Foundry Extension (VS Code) |

## Description

When deploying a hosted agent via the Foundry Extension, it generates a local `.foundry/.deployment.json` file (not committed to git) containing CPU, memory, and path configuration. If a team member clones the repo and selects different CPU/memory values during deployment, the hosted agent creation API rejects the payload with `400: Invalid payload`.

The Foundry Extension lets users pick CPU and memory settings but does not validate whether the chosen combination is acceptable by the API before sending the request. Certain CPU/memory combinations (or formats) are rejected server-side with no actionable error detail.

## Steps to Reproduce

1. Team member A clones the repo and deploys via Foundry Extension. The extension generates `.foundry/.deployment.json` locally:
   ```json
   {
     "projectId": "2888901f-6d25-4fcc-a81b-c4e751390d7b",
     "hostedAgentDeployOptions": {
       "dockerContextPath": "c:\\Users\\memberA\\repos\\foundry-claw",
       "dockerfilePath": "c:\\Users\\memberA\\repos\\foundry-claw\\Dockerfile",
       "cpu": "1.0",
       "memory": "2.0Gi"
     }
   }
   ```
   Deployment succeeds.
2. Team member B clones the same repo, runs deploy via Foundry Extension, and selects **different** CPU/memory values (e.g. a different combination or tier).
3. The container image builds and pushes to ACR successfully.
4. Deployment fails at the "Creating hosted agent" step with `400: Invalid payload`.

## Error

```
2026-03-09 18:51:22.795 [info] Step 3: Creating hosted agent...
2026-03-09 18:51:22.795 [info] Starting hosted agent creation...
2026-03-09 18:51:22.795 [info] Agent name: foundry-claw, Image: 1756abczihchprojectacr.azurecr.io/foundryclaw:3hyltpzmah7
2026-03-09 18:51:22.795 [info] Using environment variables from agent.yaml
2026-03-09 18:51:24.394 [error] Error: Failed to create hosted agent: 400: Invalid payload
```

The container image builds and pushes to ACR successfully — the failure occurs only at the hosted agent creation step, where the CPU/memory payload is sent to the API.

## Root Cause

The Foundry Extension presents CPU and memory as free-choice options, but the hosted agent creation API only accepts specific valid combinations. When a user selects an unsupported combination:

- The extension does **not** validate the values before calling the API.
- The API returns a generic `400: Invalid payload` with **no detail** about which field is invalid or what the valid options are.

Additionally, `.deployment.json` contains **absolute local paths** (`dockerContextPath`, `dockerfilePath`) which are machine-specific but only affect local build behavior.

## Impact

- Team members selecting different (but seemingly valid) CPU/memory options get a cryptic `400` error after waiting for the full ACR build to complete
- No way to know which CPU/memory combinations are valid without trial and error
- The error message provides zero guidance on what to fix

## Possible Solutions

1. **Foundry Extension should validate CPU/memory combinations** before sending the request — only present valid options in the UI picker.
2. **API should return a descriptive error** — e.g., `"cpu 2.0 with memory 1.0Gi is not a valid combination. Valid combinations are: ..."` instead of generic `400: Invalid payload`.
3. **Foundry Extension should document valid CPU/memory tiers** — show allowed combinations in the selection UI or in documentation.
4. **Fail fast before ACR build** — validate the deployment payload before starting the expensive container build step, so users don't wait minutes only to fail at the end.
