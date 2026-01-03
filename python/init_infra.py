
import os
import sys
import re
from config import get_snowflake_session

def execute_sql_file(session, file_path):
    print(f"📄 Executing {os.path.basename(file_path)}...")
    if not os.path.exists(file_path):
        print(f"⚠️  File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # 1. First, strip out comments to avoid semicolon issues inside comments
        content = re.sub(r'--.*', '', content)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # 2. Split by semicolon for actual statements
        statements = content.split(';')
        
        for stmt in statements:
            stmt = stmt.strip()
            if not stmt:
                continue
                
            try:
                # Basic check to avoid running empty blocks
                if stmt.lower().startswith('use') or stmt.lower().startswith('create') or stmt.lower().startswith('insert') or stmt.lower().startswith('drop') or stmt.lower().startswith('update') or stmt.lower().startswith('delete'):
                    session.sql(stmt).collect()
                elif len(stmt) > 5: # Fallback for other commands
                    session.sql(stmt).collect()
            except Exception as e:
                # Some errors can be ignored
                if "does not exist" in str(e).lower() or "already exists" in str(e).lower():
                    pass
                else:
                    print(f"⚠️  Error executing statement in {os.path.basename(file_path)}: {e}")

def init_infra():
    print("=" * 60)
    print("StockPulse 360 - Infrastructure Initialization")
    print("=" * 60)
    
    try:
        session = get_snowflake_session()
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        sql_dir = os.path.join(project_dir, 'sql')
        
        # Order of execution
        sql_files = [
            'create_tables.sql',
            'dynamic_tables.sql',
            'views.sql',
            'advanced_analytics.sql',
            'supplier_integration.sql',
            'ai_ml_views.sql',
            'streams_tasks.sql'  # Added this
        ]
        
        for sql_file in sql_files:
            file_path = os.path.join(sql_dir, sql_file)
            execute_sql_file(session, file_path)
            
        print("\n✅ Infrastructure initialization complete!")
        session.close()
        
    except Exception as e:
        print(f"\n❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    init_infra()
