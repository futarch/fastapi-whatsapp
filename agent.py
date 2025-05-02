import asyncio
import os
from dotenv import load_dotenv
from openai import OpenAI
from agents import Agent
from agents.mcp.server import MCPServerSse

# Charger les variables d'environnement
load_dotenv()

# Initialiser le client OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def run_agent_with_mcp_servers():
    # Initialiser le serveur MCP SSE distant
    remote_server = MCPServerSse(
        params={"url": os.getenv("MCP_SERVER_URL")},
        cache_tools_list=True
    )

    async with remote_server:
        # Créer l'agent avec la configuration appropriée
        agent = Agent(
            name="WhatsApp Assistant",
            instructions="You are a helpful WhatsApp assistant. Use the available tools to accomplish tasks.",
            mcp_servers=[remote_server],
            client=client
        )

        # Exécuter l'agent
        result = await agent.run("Complete the requested task using appropriate tools.")
        return result

# Exécuter la fonction principale
if __name__ == "__main__":
    asyncio.run(run_agent_with_mcp_servers())
