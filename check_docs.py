import os
import re

docs_dir = 'docs'
issues = []

for root, dirs, files in os.walk(docs_dir):
    for f in files:
        if f.endswith('.md'):
            path = os.path.join(root, f)
            with open(path) as fh:
                for i, line in enumerate(fh, 1):
                    if '22 tables' in line.lower() and 'historical' not in line.lower():
                        issues.append(f'{path}:{i}: Still says "22 tables": {line.strip()}')
                    if re_search := re.search(r'Sprint [3-5]\s+(implemented|completed|delivered)', line, re.I):
                        issues.append(f'{path}:{i}: Sprint presented as completed: {line.strip()}')

if issues:
    print(f'DOC ISSUES ({len(issues)}):')
    for i in issues:
        print(f'  {i}')
else:
    print('DOCUMENTATION: No issues found with "22 tables" or completed sprints')

if os.path.exists('docs/sprints/sprint-002.1.md'):
    print('sprint-002.1.md: EXISTS')
else:
    print('sprint-002.1.md: MISSING')

if os.path.exists('docs/decisions/0008-historical-cutoff-model.md'):
    print('0008-historical-cutoff-model.md: EXISTS')
else:
    print('0008-historical-cutoff-model.md: MISSING')