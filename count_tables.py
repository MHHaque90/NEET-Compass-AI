#!/usr/bin/env python
import os
os.chdir('E:\\NEET Compass AI\\backend')

from sqlalchemy import create_engine, text

engine = create_engine('postgresql+psycopg://neet:neet_dev_password@localhost:5432/neet_compass')
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
    count = result.scalar()
    print('Table count:', count)
    
    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"))
    tables = [row[0] for row in result]
    print('Tables:', sorted(tables))
engine.dispose()