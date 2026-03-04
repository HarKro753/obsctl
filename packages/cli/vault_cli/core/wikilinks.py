"""Wikilink extraction from Obsidian note content."""

import re


def extract_wikilinks(text):
    """Extract wikilink targets from text, ignoring code blocks and inline code.

    Returns a list of note names (strings). Handles:
    - [[Note]]
    - [[Note|Display]]
    - [[Note#Heading]]
    - [[Note#Heading|Display]]
    - Ignores wikilinks inside fenced code blocks and inline code
    - Ignores empty [[]] and whitespace-only wikilinks
    """
    # Step 1: Remove fenced code blocks
    # Match ``` ... ``` (with optional language)
    text_no_fenced = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

    # Step 2: Remove inline code
    text_clean = re.sub(r"`[^`]+`", "", text_no_fenced)

    # Step 3: Extract wikilinks
    # Match [[...]] but not empty or whitespace-only
    pattern = re.compile(r"\[\[([^\]]+?)\]\]")
    matches = pattern.findall(text_clean)

    results = []
    for match in matches:
        # Strip display text (after |)
        note_part = match.split("|")[0]
        # Strip heading (after #)
        note_name = note_part.split("#")[0]
        # Strip whitespace
        note_name = note_name.strip()
        # Skip empty or whitespace-only
        if note_name:
            results.append(note_name)

    return results
