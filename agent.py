import asyncio
import os
from dotenv import load_dotenv
from agents import Agent, Runner
from agents.mcp.server import MCPServerSse
from agents.model_settings import ModelSettings

# Charger les variables d'environnement
load_dotenv()

async def run_agent_with_mcp_servers(user_message: str) -> str:
    # Initialiser le serveur MCP SSE distant
    remote_server = MCPServerSse(
        params={"url": os.getenv("MCP_SERVER_URL")},
        cache_tools_list=True
    )

    async with remote_server:
        # Créer l'agent avec la configuration appropriée
        agent = Agent(
            name="Savoir",
            instructions="Exprimez-vous en français en vouvoyant l’utilisateur, avec un ton clair, professionnel et accessible. En fonction de ses messages, interrogez le serveur MCP de Graphiti pour récupérer les informations utiles et mettez à jour le graphe en conséquence. Expliquez ensuite à l’utilisateur ce que vous avez fait, de manière simple et non technique.",
            mcp_servers=[remote_server],
            model_settings=ModelSettings(tool_choice="required")
        )

        # Exécuter l'agent
        result = await Runner.run(agent, user_message)
        return result.final_output
