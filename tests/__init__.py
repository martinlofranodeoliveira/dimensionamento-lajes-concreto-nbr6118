import sys
from pathlib import Path

# Garantir que src esteja no PYTHONPATH durante a execução dos testes
_src = Path(__file__).parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))
