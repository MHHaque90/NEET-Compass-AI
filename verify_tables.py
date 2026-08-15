import os
os.chdir('E:\\NEET Compass AI\\backend')

from sqlalchemy import create_engine, text

engine = create_engine('postgresql+psycopg://neet:neet_dev_password@localhost:5432/neet_compass')
with engine.connect() as conn:
    r = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"))
    tables = [row[0] for row in r]
    print('Tables:', len(tables))
    for t in tables:
        print(' ', t)
    
    r2 = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
    print('Count:', r2.scalar())
    
    # Check alembic version
    r3 = conn.execute(text("SELECT version_num FROM alembic_version"))
    print('Alembic version:', [row[0] for row in r3])
engine.close()