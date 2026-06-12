import os
import re

from config import SENSO_KB_PATH


def query(question: str, demo: bool = True) -> str:
    kb_path = os.path.abspath(SENSO_KB_PATH)
    if not os.path.isdir(kb_path):
        return ""

    matches = []

    # Walk all markdown files
    for root, _dirs, files in os.walk(kb_path):
        for fname in files:
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath) as f:
                    content = f.read()
            except Exception:
                continue

            # Score relevance by keyword overlap
            score = _relevance_score(question, content)
            if score > 0:
                # Extract key paragraph
                para = _best_paragraph(question, content)
                matches.append((score, fname, para))

    matches.sort(key=lambda x: x[0], reverse=True)
    if matches:
        parts = []
        for _, fname, para in matches[:3]:
            parts.append(f"From {fname}: {para}")
        return "\n\n".join(parts)

    return ""


def _relevance_score(query_str: str, content: str) -> int:
    query_lower = query_str.lower()
    words = set(re.findall(r'\b[a-z]{3,}\b', query_lower))
    if not words:
        return 0
    content_lower = content.lower()
    return sum(1 for w in words if w in content_lower)


def _best_paragraph(query_str: str, content: str) -> str:
    paragraphs = content.split("\n\n")
    best = ""
    best_score = 0
    for p in paragraphs:
        if len(p.strip()) < 30:
            continue
        if p.startswith("#"):
            continue
        score = _relevance_score(query_str, p)
        if score > best_score:
            best_score = score
            best = p.strip()
    return best or content[:500]
