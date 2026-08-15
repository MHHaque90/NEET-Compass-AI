#!/usr/bin/env python
import os
os.chdir('E:\\NEET Compass AI\\backend')

with open('alembic/versions/0001_initial_schema.py', 'r') as f:
    lines = f.readlines()

# Remove the stray ')' at line 701 (1-indexed) = index 700 (0-indexed)
# This is the leftover from the removed source_files block
del lines[700]  # 0-indexed line 700 = 1-indexed line 701

with open('alembic/versions/0001_initial_schema.py', 'w') as f:
    f.writelines(lines)

print("Removed stray closing paren")