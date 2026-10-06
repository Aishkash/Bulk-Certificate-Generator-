import pandas as pd

MAX_ROWS = 1000


class ParseError(Exception):
    """Raised when the whole file is unusable."""


def read_names(file) -> list[str]:
    """Read the CSV and return the names from the 'name' column."""
    try:
        df = pd.read_csv(file, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    except Exception:
        raise ParseError("Could not read the file. Make sure it is a valid CSV")

    df.columns = [c.strip().lower() for c in df.columns]
    if "name" not in df.columns:
        raise ParseError("File must have a 'name' column")

    names = [n.strip() for n in df["name"]]
    if not names:
        raise ParseError("File has no data rows")
    if len(names) > MAX_ROWS:
        raise ParseError(f"Too many rows (max {MAX_ROWS})")
    return names


def validate_names(names: list[str]) -> tuple[list[str], list[dict]]:
    """Split names into valid names and rejected entries (with the reason)."""
    valid, rejected = [], []

    for name in names:
        if not name:
            rejected.append({"name": name, "error": "Name is required"})
        elif len(name) > 100:
            rejected.append({"name": name, "error": "Name is too long (max 100 characters)"})
        else:
            valid.append(name)

    return valid, rejected