"""Shared identifier normalization for parsing, lookup and matching."""
import re
from urllib.parse import unquote


def normalize_reference_id(value):
    match = re.fullmatch(r"\s*[\[(]?0*(\d+)[\]).]?\s*", str(value))
    return int(match.group(1)) if match and int(match.group(1)) > 0 else None


def normalize_doi(value):
    if not value:
        return None
    text = unquote(str(value)).strip().lower()
    text = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", text)
    text = text.rstrip(".,;")
    while text.endswith(")") and text.count(")") > text.count("("):
        text = text[:-1]
    return text
