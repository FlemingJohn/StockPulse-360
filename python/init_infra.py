
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
        # Remove comments
        content = re.sub(r'--.*', '', content)
        # Split by semicolon
        statements = content.split(';')
        
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                try:
                    session.sql(stmt).collect()
                except Exception as e:
                    # Some errors (like DROP IF NOT EXISTS) can be ignored
                    if "does not exist" in str(e).lower() or "already exists" in str(e).lower():
                        pass
                    else:
                        print(f"⚠️  Error executing statement: {e}")
                        # print(f"SQL: {stmt[:100]}...")

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
            'ai_ml_views.sql'
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
