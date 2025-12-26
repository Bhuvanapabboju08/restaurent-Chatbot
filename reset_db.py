"""
Reset ChromaDB Database
This script resets the ChromaDB collection to fix dimension mismatches
"""

import os
import shutil
from dotenv import load_dotenv

load_dotenv()

def reset_database():
    """Delete and recreate the ChromaDB database"""
    persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")

    print("=" * 60)
    print("RESETTING CHROMADB DATABASE")
    print("=" * 60)
    print(f"\nDatabase location: {persist_dir}")

    if os.path.exists(persist_dir):
        print(f"\n⚠ WARNING: This will delete all existing documents!")
        response = input("Are you sure you want to continue? (yes/no): ")

        if response.lower() != 'yes':
            print("\n❌ Operation cancelled")
            return

        print(f"\n🗑 Deleting {persist_dir}...")
        try:
            shutil.rmtree(persist_dir)
            print("✓ Database deleted successfully")
        except Exception as e:
            print(f"❌ Error deleting database: {e}")
            print("\nPlease:")
            print("1. Stop the Flask server (Ctrl+C)")
            print("2. Run this script again")
            return
    else:
        print("\n✓ Database directory doesn't exist (already clean)")

    print("\n✓ Database reset complete!")
    print("\nNext steps:")
    print("1. Restart the Flask server: python app.py")
    print("2. Upload documents again")
    print("\nThe new collection will use the correct embedding dimensions.")

if __name__ == "__main__":
    reset_database()
