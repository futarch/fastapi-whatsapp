import asyncio
import os
import httpx
import logging
from dotenv import load_dotenv
from agents import Agent, Runner
from agents.mcp.server import MCPServerSse

# Charger les variables d'environnement
load_dotenv()

logger = logging.getLogger(__name__)

async def run_agent_with_mcp_servers(user_message: str) -> str:
    # Initialiser le serveur MCP SSE distant
    remote_server = MCPServerSse(
        params={"url": os.getenv("MCP_SERVER_URL")},
        cache_tools_list=True
    )
    try:
        async with remote_server:
            # Créer l'agent avec la configuration appropriée
            agent = Agent(
                name="Savoir",
                instructions="Exprimez-vous en français en vouvoyant l’utilisateur, avec un ton clair, professionnel et accessible. Utilisez les outils à votre disposition pour répondre à l'utilisateur.",
                mcp_servers=[remote_server],
                model='gpt-4.1-mini', 
                temperature=0
            )
            
            # Exécuter l'agent
            result = await Runner.run(agent, user_message)
            return result.final_output
            
    except httpx.HTTPStatusError as e:
        logger.error(f"Connexion au serveur MCP échouée (HTTP {e.response.status_code})")
        return {"error": "Le serveur d'agent ne répond pas (timeout)."}
    except Exception as e:
        logger.exception("Erreur inattendue lors de la connexion au serveur MCP")
        return {"error": "Impossible de traiter votre message pour le moment."}

