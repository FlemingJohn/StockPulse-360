
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
    
    # 1. Strip comments
    content = re.sub(r'--.*', '', content)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # 2. Split statements manually by tracking block depth
    statements = []
    buffer = []
    depth = 0
    
    lines = content.split('\n')
    for line in lines:
        line_strip = line.strip()
        if not line_strip:
            continue
            
        buffer.append(line)
        line_upper = line_strip.upper()
        
        # Track block depth (Snowflake Tasks/Procedures use BEGIN ... END;)
        if "BEGIN" in line_upper:
            depth += 1
        
        # Semicolon outside of a block marks completion
        # OR if it's the specific END; of a block
        if ";" in line_strip:
            if depth == 0:
                statements.append("\n".join(buffer).strip())
                buffer = []
            elif "END;" in line_upper or "END ;" in line_upper:
                depth = max(0, depth - 1)
                if depth == 0:
                    statements.append("\n".join(buffer).strip())
                    buffer = []

    # Final buffer
    if buffer:
        statements.append("\n".join(buffer).strip())
            
    # 3. Execution
    for stmt in statements:
        if not stmt or len(stmt) < 5:
            continue
            
        try:
            session.sql(stmt).collect()
        except Exception as e:
            # Ignore harmless errors
            if "already exists" in str(e).lower() or "does not exist" in str(e).lower():
                pass
            else:
                print(f"⚠️  Error executing statement in {os.path.basename(file_path)}: {e}")
                print(f"   >>> Statement causing error: {stmt[:250]}...")

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
