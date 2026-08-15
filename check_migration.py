import os
wd = r'E:\NEET Compass AI\backend'
os.chdir(wd)

from alembic.config import Config
from alembic.script import ScriptDirectory

config = Config('alembic.ini')
script = ScriptDirectory.from_config(config)

# Just get heads
heads = script.get_heads()
print('Heads:', heads)

# List using walk_revisions properly
for r in script.walk_revisions():
    print('Walk rev:', r)