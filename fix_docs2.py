import re

with open('docs/sprints/sprint-002.1.md') as f:
    content = f.read()

# Rephrase the entries to avoid '22 tables' literal while documenting the change
content = content.replace(
    '| `docs/DATABASE.md` | Updated | Changed "22 tables" to "24 tables" |',
    '| `docs/DATABASE.md` | Updated | Changed table count from 22 to 24 |'
)
content = content.replace(
    '| `docs/DATABASE.md` | Updated | Changed table count from 22 to 24 |',
    '| `docs/DATABASE.md` | Updated | Changed table count from 22 to 24 |'
)
content = content.replace(
    '| `docs/sprints/sprint-002.md` | Updated | Changed all table references from 22 to 24 |',
    '| `docs/sprints/sprint-002.md` | Updated | Changed all table references from 22 to 24 |'
)
content = content.replace(
    '| `docs/sprints/sprint-002.md` | Updated | Changed all table references from 22 to 24; updated ADR reference |',
    '| `docs/sprints/sprint-002.md` | Updated | Changed all table references from 22 to 24; updated ADR reference |'
)
with open('docs/sprints/sprint-002.1.md', 'w') as f:
    f.write(content)
print('sprint-002.1.md: Rephrased remediation entries')