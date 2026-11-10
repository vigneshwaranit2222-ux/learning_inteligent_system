import re
from typing import List, Dict, Any, Optional
import spacy
from ai_engine.normalization.canonical_skills import (
    normalize_skill_name,
    CANONICAL_SKILL_CATALOG,
    ALIAS_TO_CANONICAL
)

# Load spaCy pipeline
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = spacy.blank("en")

class SkillExtractor:
    def __init__(self):
        # Precompile regex word boundaries for all canonical skills and aliases for instant deterministic matching
        # Sort by length descending to match multi-word phrases first (e.g., 'Large Language Models' before 'Model')
        sorted_keys = sorted(ALIAS_TO_CANONICAL.keys(), key=len, reverse=True)
        # Escape regex special characters like C++, C#, .NET
        escaped_keys = [re.escape(k) for k in sorted_keys]
        self.pattern = re.compile(r'\b(' + '|'.join(escaped_keys) + r')\b', re.IGNORECASE)

    def extract_snippet(self, text: str, start: int, end: int, window: int = 60) -> str:
        snippet_start = max(0, start - window)
        snippet_end = min(len(text), end + window)
        snippet = text[snippet_start:snippet_end].strip()
        # Clean up whitespace and line breaks
        snippet = re.sub(r'\s+', ' ', snippet)
        return snippet

    def extract_skills_from_text(self, text: str, source_type: str = "text") -> List[Dict[str, Any]]:
        """
        Extracts verified canonical skills with verbatim evidence text snippets and confidence scores.
        """
        if not text:
            return []

        results: Dict[str, Dict[str, Any]] = {}

        # 1. Deterministic Dictionary & Alias Regex Scan
        for match in self.pattern.finditer(text):
            matched_text = match.group(0).lower()
            canonical = ALIAS_TO_CANONICAL.get(matched_text)
            if canonical and canonical not in results:
                start_char, end_char = match.span()
                snippet = self.extract_snippet(text, start_char, end_char)
                category = CANONICAL_SKILL_CATALOG[canonical]["category"]
                results[canonical] = {
                    "canonical_name": canonical,
                    "category": category,
                    "evidence_snippet": snippet,
                    "confidence": 1.0,
                    "extraction_method": "canonical_regex",
                    "start_char": start_char,
                    "end_char": end_char
                }

        # 2. NLP Noun Chunk Extraction for multi-word or non-standard technical phrases
        try:
            doc = nlp(text[:15000]) # Cap NLP parse at 15k chars for instant processing
            for chunk in doc.noun_chunks:
                chunk_text = chunk.text.strip()
                if len(chunk_text) < 3 or len(chunk_text) > 40:
                    continue
                norm_res = normalize_skill_name(chunk_text, threshold=90.0)
                if norm_res:
                    canonical, category, conf = norm_res
                    if canonical not in results:
                        start_char = chunk.start_char
                        end_char = chunk.end_char
                        snippet = self.extract_snippet(text, start_char, end_char)
                        results[canonical] = {
                            "canonical_name": canonical,
                            "category": category,
                            "evidence_snippet": snippet,
                            "confidence": conf,
                            "extraction_method": "spacy_noun_chunk_fuzzy",
                            "start_char": start_char,
                            "end_char": end_char
                        }
        except Exception:
            pass

        return list(results.values())

extractor = SkillExtractor()
