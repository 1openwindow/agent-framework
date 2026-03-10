# Copyright (c) Microsoft. All rights reserved.

from agent_framework.azure import AzureOpenAIResponsesClient
from azure.ai.agentserver.agentframework import from_agent_framework  # pyright: ignore[reportUnknownVariableType]
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


def main():
    # Create MCP tool configuration as dict
    mcp_tool = {
        "type": "mcp",
        "server_label": "Microsoft_Learn_MCP",
        "server_url": "https://learn.microsoft.com/api/mcp",
    }

    # Create an Agent using the Azure OpenAI Responses Client with a MCP Tool that connects to Microsoft Learn MCP
    agent = AzureOpenAIResponsesClient(
        project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
        deployment_name=os.environ["AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME"],
        credential=DefaultAzureCredential(),
    ).as_agent(
        name="DocsAgent",
        instructions="You are a helpful assistant that can help with microsoft documentation questions.",
        tools=mcp_tool,
    )

    # Run the agent as a hosted agent
    from_agent_framework(agent).run()


if __name__ == "__main__":
    main()
