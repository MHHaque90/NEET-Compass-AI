import os
import re

print('=== SCOPE COMPLIANCE CHECK ===')
print()

# Check that Sprint 2.5, 3, 4, 5 are not presented as completed
docs_dir = 'docs'
issues = []

for root, dirs, files in os.walk(docs_dir):
    for f in files:
        if f.endswith('.md'):
            path = os.path.join(root, f)
            with open(path) as fh:
                for i, line in enumerate(fh, 1):
                    # Check for sprint 2.5 as completed
                    if re.search(r'Sprint 2\.5\s+(implemented|completed|delivered)', line, re.I):
                        issues.append(f'{path}:{i}: Sprint 2.5 presented as completed')
                    # Check for Sprint 3, 4, 5 as completed (but not as remediation/ref)
                    if re.search(r'Sprint [3-5]\s+(implemented|completed|delivered)', line, re.I):
                        # Skip if it's in a "Remaining Work" section or "not implemented" context
                        if not any(skip in line.lower() for skip in ['remaining work', 'not implemented', 'planned', 'roadmap', 'future']):
                            issues.append(f'{path}:{i}: Sprint presented as completed (no context)')

if issues:
    print('SCOPE ISSUES:')
    for i in issues:
        print(f'  {i}')
else:
    print('Sprint 2.5/3/4/5: No issues - future sprints not presented as completed')

# Check sprint-002.1.md exists and references remediation only
if os.path.exists('docs/sprints/sprint-002.1.md'):
    with open('docs/sprints/sprint-002.1.md') as f:
        content = f.read()
    # Check it doesn't claim future sprints
    if 'Sprint 2.5' in content:
        print('sprint-002.1.md: Contains Sprint 2.5 reference')
    else:
        print('sprint-002.1.md: No Sprint 2.5 reference')
    if 'Sprint 3' in content or 'Sprint 4' in content or 'Sprint 5' in content:
        # Check if they're presented as completed
        bad = re.search(r'Sprint [3-5]\s+(implemented|completed|delivered)', content, re.I)
        if bad:
            print('sprint-002.1.md: Future sprints presented as completed')
        else:
            print('sprint-002.1.md: Future sprints referenced as planned/future only')
else:
    print('sprint-002.1.md: MISSING')

# Check no ETL or prediction implementation in backend
print()
print('=== NO FORBIDDEN IMPLEMENTATION ===')
forbidden_dirs = ['etl/contracts/']
found_any = False
for fd in forbidden_dirs:
    if os.path.isdir(fd):
        print(f'FORBIDDEN: {fd} exists')
        found_any = True

# Check via grep patterns in backend code
code_patterns = [
    ('etl_runs', 'ETL run tracking'),
    ('prediction', 'prediction'),
    ('ml.train', 'ML training'),
    ('frontend', 'frontend'),
]
for pattern, desc in code_patterns:
    matches = []
    for root, dirs, files in os.walk('backend'):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                with open(filepath) as cf:
                    content = cf.read()
                    if pattern.lower() in content.lower() and 'test' not in filepath.lower():
                        matches.append(filepath)
            except:
                pass
    if matches:
        print(f'FORBIDDEN: {desc} found in {len(matches)} files')
        found_any = True
    else:
        print(f'OK: No {desc} in code')

if not found_any:
    print('All: No forbidden implementations found')
PYEOF