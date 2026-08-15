#!/usr/bin/env python
import os
os.chdir('E:\\NEET Compass AI\\backend')

with open('alembic/versions/0001_initial_schema.py', 'r') as f:
    lines = f.readlines()

# Remove the duplicate source_files block (lines 701-770, 0-indexed: 700-769)
# and keep the first source_files block that was moved earlier

# Delete lines 701-770 (1-indexed) which is 700-769 (0-indexed)
# These lines contain the second "op.create_table("source_files"...) block

del lines[700:770]  # 0-indexed: remove indices 700 through 769 inclusive

with open('alembic/versions/0001_initial_schema.py', 'w') as f:
    f.writelines(lines)

print("Removed duplicate source_files block from 0001")