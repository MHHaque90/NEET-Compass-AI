# Check alembic revision chain
import sys
sys.path.insert(0, 'backend')

with open('backend/alembic/versions/0001_initial_schema.py') as f:
    content1 = f.read()

with open('backend/alembic/versions/0002_create_historical_cutoffs.py') as f:
    content2 = f.read()

# Check that 0002 depends on 0001
if '0001_initial_schema' in content2:
    print('0002 references 0001: OK')
else:
    print('0002 references 0001: ISSUE')

# Check that 0001 has create_table operations
tables_0001 = content1.count('op.create_table(')
print(f'0001 creates {tables_0001} tables')

# Check that 0002 has create_table
tables_0002 = content2.count('op.create_table(')
print(f'0002 creates {tables_0002} table')

# Verify 0001 has the deleted_at reference for colleges
if 'college_id' in content2 and 'deleted_at' in content2:
    print('0002 has historical_cutoffs with college FK: OK')
else:
    print('0002 has historical_cutoffs with college FK: ISSUE')

# Verify 0001 mentions colleges with deleted_at
if 'colleges' in content1:
    print('0001 mentions colleges: OK')

print('Migration chain check complete')