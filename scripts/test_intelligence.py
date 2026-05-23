import asyncio
import sys
import os

# Dans le container, le code est dans /app et app/ est un package
sys.path.append("/app")

from app.core.database import AsyncSessionLocal
from app.engine.intelligence_monitor import IntelligenceMonitor
from app.core.config import settings

async def test_watch():
    print(f"--- Test de la Veille Numérique pour : {settings.target_domain} ---")
    
    async with AsyncSessionLocal() as db:
        monitor = IntelligenceMonitor(db)
        print("Lancement de la collecte (RSS + GitHub)...")
        
        try:
            await monitor.run_all()
            print("Collecte terminée avec succès.")
        except Exception as e:
            print(f"ERREUR lors de la collecte : {e}")
        finally:
            await monitor.close()

if __name__ == "__main__":
    asyncio.run(test_watch())
