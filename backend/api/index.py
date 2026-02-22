import sys
import os

# Add backend/ directory to path so local modules (config, rag, etc.) are importable
# This is needed when Vercel's root dir is set to `backend/`
_this_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)

from main import app  # noqa: E402
