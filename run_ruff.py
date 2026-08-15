import subprocess
import sys

# Install ruff
result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "ruff"],
    capture_output=True, text=True, cwd="E:\\NEET Compass AI"
)
print("Install stdout:", result.stdout[-200:] if result.stdout else "")
print("Install stderr:", result.stderr[-200:] if result.stderr else "")

# Run ruff check
result = subprocess.run(
    [sys.executable, "-m", "ruff", "check", "backend/"],
    capture_output=True, text=True, cwd="E:\\NEET Compass AI"
)
print("Ruff stdout:", result.stdout)
print("Ruff stderr:", result.stderr)
print("Return code:", result.returncode)