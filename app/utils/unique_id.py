

import re
from datetime import datetime

def generate_safe_collection_name(base: str) -> str:
    # Keep only letters and numbers
    safe_base = re.sub(r'[^a-zA-Z0-9]', '', base)
    # Append a timestamp to ensure uniqueness (also only numbers)
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    return f"kapture_{safe_base}{timestamp}"

