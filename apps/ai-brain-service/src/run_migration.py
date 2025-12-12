"""
Run database migration for pgvector setup
"""
import asyncio
import asyncpg
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

async def run_migration():
    """Execute pgvector setup migration"""
    
    if not DATABASE_URL:
        print("✗ ERROR: DATABASE_URL not found in .env file")
        sys.exit(1)
    
    print(f"Connecting to database...")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        print("✓ Connected to PostgreSQL")
        
        # Read migration file
        migration_file = Path(__file__).parent / "database" / "migrations" / "001_pgvector_setup.sql"
        sql = migration_file.read_text()
        
        print(f"\nRunning migration: {migration_file.name}")
        print("-" * 60)
        
        # Execute migration (split by semicolons for multiple statements)
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        
        for i, statement in enumerate(statements, 1):
            if statement:
                try:
                    await conn.execute(statement)
                    if 'CREATE TABLE' in statement:
                        table_name = statement.split('CREATE TABLE')[1].split('(')[0].strip().split()[0]
                        print(f"  ✓ Created table: {table_name}")
                    elif 'CREATE INDEX' in statement:
                        print(f"  ✓ Created index")
                    elif 'CREATE EXTENSION' in statement:
                        print(f"  ✓ Enabled pgvector extension")
                except Exception as e:
                    # Ignore "already exists" errors
                    if 'already exists' not in str(e):
                        print(f"  ⚠ Warning: {e}")
        
        print("-" * 60)
        print("\n✓ Migration complete!")
        
        # Verify tables were created
        tables = await conn.fetch("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename IN ('task_embeddings', 'user_behavior_embeddings', 'conversation_context', 'voice_interactions', 'user_ai_preferences')
            ORDER BY tablename
        """)
        
        print(f"\n✓ Verified {len(tables)} tables:")
        for table in tables:
            print(f"  - {table['tablename']}")
        
        # Check pgvector extension
        has_vector = await conn.fetchval("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')")
        if has_vector:
            print(f"\n✓ pgvector extension is enabled")
        else:
            print(f"\n✗ WARNING: pgvector extension not found!")
        
        await conn.close()
        print("\n✓ Database setup complete and ready for AI Brain Service!")
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_migration())
