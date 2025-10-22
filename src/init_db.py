"""Database initialization script"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_database


def main():
    """Initialize the database"""
    print("=" * 60)
    print("Medical Clinic Chatbot - Database Initialization")
    print("=" * 60)
    print()
    
    try:
        init_database()
        print()
        print("=" * 60)
        print("✅ Success! Database is ready to use.")
        print("=" * 60)
        print()
        print("Database file: clinic.db")
        print("Tables created:")
        print("  - appointments")
        print("  - todos")
        print("  - conversations")
        print("  - clinic_settings")
        print()
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Error initializing database: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
