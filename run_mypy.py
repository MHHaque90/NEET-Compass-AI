import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "mypy"],
    capture_output=True, text=True, cwd="E:\\NEET Compass AI"
)
print("Install stdout:", result.stdout[-100:])
print("Install returncode:", result.returncode)

result = subprocess.run(
    [sys.executable, "-m", "mypy", "backend/app/"],
    capture_output=True, text=True, cwd="E:\\NEET Compass AI"
)
print("Mypy stdout:", result.stdout[-500:])
print("Mypy returncode:", result.returncode)