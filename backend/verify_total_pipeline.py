import asyncio
import json
import sys
import os

# Ultimate path fixing
# Add the current working directory (backend) to the front of sys.path
sys.path.insert(0, os.getcwd())

# Debug: Print path to see what is happening
print(f"DEBUG: sys.path[0] = {sys.path[0]}")
print(f"DEBUG: Current Dir = {os.getcwd()}")
print(f"DEBUG: Files in CWD = {os.listdir('.')}")

from app.services.pipeline_orchestrator import orchestrator
from app.core.sqlite_client import init_database

async def final_proof():
    init_database()
    print('--- 🚀 RuleScribe Games ULTIMATE PIPELINE PROOF ---')
    print(' (Official Artifacts via notebooklm-py)')
    
    try:
        # Run the full conductor
        game = await orchestrator.execute_full_pipeline('Azul')
        
        print('\n' + '='*80)
        print(f'🏆 TOTAL PIPELINE SUCCESS: {game["title"]}')
        print('='*80)
        
        info = game['infographics']
        if isinstance(info, str):
            import json
            info = json.loads(info)
            
        for key, val in info.items():
            preview = val[:150].replace('\n', ' ') + '...'
            print(f'   - {key.upper()}: {preview}')
            
        print('='*80)
        print('\n✨ VERIFIED: Fully operational!')
        
    except Exception as e:
        print(f'\n❌ Proof Failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(final_proof())
