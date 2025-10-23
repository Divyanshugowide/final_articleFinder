
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from app.arabert_integration import prepare_arabert_index

if __name__ == "__main__":
    print("Creating AraBERT FAISS index...")
    success = prepare_arabert_index()
    if success:
        print("✅ AraBERT index created successfully")
    else:
        print("❌ Failed to create AraBERT index")
