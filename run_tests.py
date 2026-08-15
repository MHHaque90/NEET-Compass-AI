import os
import sys
os.chdir('E:\\NEET Compass AI\\backend')

result = subprocess.run(
    [sys.executable, '-m', 'pytest', 'tests/', '-v', '--strict-markers'],
    capture_output=True, text=True
)
print('STDOUT:', result.stdout[-2000:])
print('STDERR:', result.stderr[-2000:])
print('Return code:', result.returncode)