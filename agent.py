from openai import OpenAI
from openai_agents import Agent, MCPServerSse
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def run_agent_with_mcp_servers():
    # Initialize remote SSE MCP server
    remote_server = MCPServerSse(
        url=os.getenv("MCP_SERVER_URL"),
        cache_tools_list=True
    )

    async with remote_server:
        # Create agent with proper configuration
        agent = Agent(
            name="WhatsApp Assistant",
            instructions="You are a helpful WhatsApp assistant. Use the available tools to accomplish tasks.",
            mcp_servers=[remote_server],
            client=client
        )

        # Run the agent
        result = await agent.run("Complete the requested task using appropriate tools.")
        return result
