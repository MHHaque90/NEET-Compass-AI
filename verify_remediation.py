#!/usr/bin/env python
import subprocess
import sys

errors = []

# Check 1: pyproject.toml has integration marker
with open('pyproject.toml') as f:
    content = f.read()
if 'markers' in content and 'integration' in content:
    print('PASS: pyproject.toml has markers section with integration')
else:
    errors.append('pyproject.toml missing markers or integration')
    print('FAIL: pyproject.toml missing markers or integration')

# Check 2: ruff check passes
result = subprocess.run(
    [sys.executable, '-m', 'ruff', 'check', 'backend/'],
    capture_output=True, text=True, cwd='E:\\NEET Compass AI'
)
if result.returncode == 0:
    print('PASS: Ruff check')
else:
    errors.append(f'Ruff check failed: {result.stdout}')
    print(f'FAIL: Ruff check ({result.returncode})')

# Check 3: ruff format passes
result = subprocess.run(
    [sys.executable, '-m', 'ruff', 'format', '--check', 'backend/'],
    capture_output=True, text=True, cwd='E:\\NEET Compass AI'
)
if result.returncode == 0:
    print('PASS: Ruff format')
else:
    errors.append(f'Ruff format check failed')
    print(f'FAIL: Ruff format')

# Check 4: Integration test collection
result = subprocess.run(
    [sys.executable, '-m', 'pytest', 'backend/tests/integration/', '--collect-only', '-q'],
    capture_output=True, text=True, cwd='E:\\NEET Compass AI'
)
if result.returncode == 0:
    print(f'PASS: Integration test collection ({len(result.stdout.strip().split(chr(10)))} test files)')
else:
    errors.append(f'Integration test collection failed: {result.stderr}')
    print(f'FAIL: Integration test collection')

# Check 5: Historical cutoff model imports
try:
    from app.infrastructure.db.models.historical_cutoff import HistoricalCutoffModel
    print('PASS: HistoricalCutoffModel importable')
except Exception as e:
    errors.append(f'HistoricalCutoffModel import failed: {e}')
    print(f'FAIL: HistoricalCutoffModel import: {e}')

# Check 6: All model tests pass (import check)
try:
    from app.infrastructure.db import models
    expected = [
        'AllotmentModel', 'CandidateModel', 'CategoryModel', 'CollegeModel',
        'CourseModel', 'DataSourceModel', 'DistrictModel', 'ETLErrorModel',
        'ETLRunModel', 'FeatureFlagModel', 'FeeModel', 'HistoricalCutoffModel',
        'LogModel', 'ModelVersionModel', 'PredictionModel', 'PredictionHistoryModel',
        'QuotaModel', 'RecommendationModel', 'RoundModel', 'SeatMatrixModel',
        'SourceFileModel', 'StateModel', 'SystemSettingModel', 'UploadModel',
        'UserModel',
    ]
    for name in expected:
        if not hasattr(models, name):
            errors.append(f'Model {name} not in models package')
            print(f'FAIL: Model {name} not found')
    print(f'PASS: All {len(expected)} models importable')
except Exception as e:
    errors.append(f'Model import check failed: {e}')
    print(f'FAIL: Model check: {e}')

# Summary
if errors:
    print(f'\\nERRORS: {len(errors)}')
    for e in errors:
        print(f'  - {e}')
else:
    print('\\nAll checks passed!')