
from pathlib import Path
import py_compile
root=Path(__file__).resolve().parent
for f in root.rglob("*.py"):
    py_compile.compile(str(f),doraise=True)
print("All Python files compile successfully.")
