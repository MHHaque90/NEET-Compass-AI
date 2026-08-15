#!/usr/bin/env python
import os
os.chdir('E:\\NEET Compass AI\\backend')

from sqlalchemy import create_engine, text

engine = create_engine('postgresql+psycopg://neet:neet_dev_password@localhost:5432/neet_compass')
with engine.connect() as conn:
    # Get all table names
    result = conn.execute(text("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"""))
    tables = [row[0] for row in result]
    print('Tables to drop:', tables)
    
    # Drop all tables
    for table in reversed(tables):
        try:
            conn.execute(text(f'DROP INDEX IF EXISTS {table}_d CASCADE'))
            conn.execute(text(f'DROP TABLE IF EXISTS {table} CASCADE'))
            print(f'Dropped {table}')
        except Exception as e:
            print(f'Error dropping {table}: {e}')
    
    # Verify no tables remain
    result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
    count = result.scalar()
    print('Remaining tables:', count)
engine.dispose()