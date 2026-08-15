import os
os.chdir('E:\\NEET Compass AI\\backend')
with open('alembic/versions/0001_initial_schema.py', 'r') as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    if 'op.create_table' in line:
        start = line.find('"') + 1
        end = line.find('"', start)
        table_name = line[start:end]
        print(f'{i}: {table_name}')