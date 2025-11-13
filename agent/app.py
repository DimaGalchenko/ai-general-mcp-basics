import asyncio
import json
import os

from mcp import Resource
from mcp.types import Prompt

from agent.constants import OPENAI_API_KEY
from agent.mcp_client import MCPClient
from agent.openai_client import OpenAIClient
from agent.models.message import Message, Role
from agent.prompts import SYSTEM_PROMPT


# https://remote.mcpservers.org/fetch/mcp
# Pay attention that `fetch` doesn't have resources and prompts

async def main():
    #TODO:
    # 1. Create MCP client and open connection to the MCP server (use `async with {YOUR_MCP_CLIENT} as mcp_client`),
    #    mcp_server_url="http://localhost:8005/mcp"
    # 2. Get Available MCP Resources and print them
    # 3. Get Available MCP Tools, assign to `tools` variable, print tool as well
    # 4. Create OpenAIClient
    # 5. Create list with messages and add there SYSTEM_PROMPT with instructions to LLM
    # 6. Add to messages Prompts from MCP server as User messages
    # 7. Create console chat (infinite loop + ability to exit from chat + preserve message history after the call to OpenAIClient client)
    async with MCPClient(mcp_server_url="http://localhost:8005/mcp") as mcp_client:

        resources = await mcp_client.get_resources()
        print("Available MCP Resources:")
        for r in resources:
            print(f"  - {r.uri}")

        tools = await mcp_client.get_tools()
        print("Available MCP Tools:")
        for t in tools:
            print(f"  - {t['function']['name']}: {t['function'].get('description', '')}")

        openai_client = OpenAIClient(
            model="gpt-4o-mini",
            api_key=OPENAI_API_KEY,
            tools=tools,
            mcp_client=mcp_client
        )

        messages = [Message(role="system", content=SYSTEM_PROMPT)]

        for prompt in await mcp_client.get_prompts():
            content = await mcp_client.get_prompt(prompt.name)
            messages.append(Message(role="user", content=content))

        print("\n--- Console Chat (type 'exit' to quit) ---")
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                break

            messages.append(Message(role="user", content=user_input))

            ai_response = await openai_client.get_completion(messages)
            print(f"AI: {ai_response.content}")

            messages.append(Message(role="assistant", content=ai_response.content))


if __name__ == "__main__":
    asyncio.run(main())
