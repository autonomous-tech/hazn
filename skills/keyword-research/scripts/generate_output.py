#!/usr/bin/env python3
"""
Keyword Research JSON Output Generator & Validator

Provides helper functions for:
- Generating the standard keyword research JSON structure
- Validating output against the schema
- Merging web search and API data

Usage:
    # As a module
    from generate_output import KeywordResearchOutput
    
    output = KeywordResearchOutput(seed_keyword="email marketing", mode="standard")
    output.add_keyword(keyword="email marketing automation", intent="informational", ...)
    output.add_question(question="What is email marketing automation?", ...)
    output.add_content_opportunity(title="Complete Guide to Email Marketing Automation", ...)
    output.save("./outputs/keyword-research.json")
    
    # CLI validation
    python3 generate_output.py validate /path/to/keyword-research.json
"""

import json
import sys
from datetime import date
from typing import Optional


class KeywordResearchOutput:
    """Builder for keyword research JSON output."""

    VALID_INTENTS = {"informational", "navigational", "commercial", "transactional"}
    VALID_VOLUME_BUCKETS = {"very_low", "low", "medium", "high", "very_high"}
    VALID_DIFFICULTIES = {"easy", "medium", "hard", "very_hard"}
    VALID_SOURCES = {"web_search", "semrush", "ahrefs", "google_ads", "mixed"}
    VALID_SERP_FEATURES = {
        "featured_snippet", "people_also_ask", "ads", "video",
        "images", "knowledge_panel", "local_pack", "shopping", "news"
    }

    def __init__(
        self,
        seed_keyword: str,
        mode: str = "standard",
        industry: Optional[str] = None,
        target_audience: Optional[str] = None,
        geographic_target: Optional[str] = None,
        data_sources: Optional[list] = None,
    ):
        self.data = {
            "meta": {
                "seed_keyword": seed_keyword,
                "industry": industry,
                "target_audience": target_audience,
                "geographic_target": geographic_target,
                "research_date": date.today().isoformat(),
                "mode": mode,
                "data_sources": data_sources or ["web_search"],
                "total_keywords": 0,
            },
            "keywords": [],
            "questions": [],
            "content_opportunities": [],
            "competitive_insights": {
                "top_competitors": [],
                "content_gaps": [],
                "weak_spots": [],
            },
        }
        if mode == "topical-authority":
            self.data["topical_authority"] = {
                "pillars": [],
                "content_creation_order": [],
            }

    def add_keyword(
        self,
        keyword: str,
        search_intent: str,
        volume_bucket: str,
        estimated_monthly_volume: str,
        difficulty: str,
        difficulty_score: int,
        opportunity_score: float,
        content_angle: str,
        serp_features: Optional[list] = None,
        parent_topic: Optional[str] = None,
        source: str = "web_search",
        exact_monthly_volume: Optional[int] = None,
        cpc: Optional[float] = None,
        competition_level: Optional[str] = None,
    ):
        """Add a keyword to the research output."""
        entry = {
            "keyword": keyword,
            "search_intent": search_intent,
            "volume_bucket": volume_bucket,
            "estimated_monthly_volume": estimated_monthly_volume,
            "difficulty": difficulty,
            "difficulty_score": difficulty_score,
            "opportunity_score": round(opportunity_score, 1),
            "serp_features": serp_features or [],
            "content_angle": content_angle,
            "parent_topic": parent_topic,
            "source": source,
        }
        # Add API-enriched fields if present
        if exact_monthly_volume is not None:
            entry["exact_monthly_volume"] = exact_monthly_volume
        if cpc is not None:
            entry["cpc"] = cpc
        if competition_level is not None:
            entry["competition_level"] = competition_level

        self.data["keywords"].append(entry)
        self.data["meta"]["total_keywords"] = len(self.data["keywords"])

    def add_question(
        self,
        question: str,
        parent_keyword: str,
        opportunity_score: float,
        search_intent: str = "informational",
    ):
        """Add a PAA / question keyword."""
        self.data["questions"].append({
            "question": question,
            "parent_keyword": parent_keyword,
            "search_intent": search_intent,
            "opportunity_score": round(opportunity_score, 1),
        })

    def add_content_opportunity(
        self,
        title: str,
        target_keyword: str,
        supporting_keywords: list,
        search_intent: str,
        estimated_difficulty: str,
        rationale: str,
    ):
        """Add a content opportunity recommendation."""
        self.data["content_opportunities"].append({
            "title": title,
            "target_keyword": target_keyword,
            "supporting_keywords": supporting_keywords,
            "search_intent": search_intent,
            "estimated_difficulty": estimated_difficulty,
            "rationale": rationale,
        })

    def set_competitive_insights(
        self,
        top_competitors: list,
        content_gaps: list,
        weak_spots: list,
    ):
        """Set competitive intelligence data."""
        self.data["competitive_insights"] = {
            "top_competitors": top_competitors,
            "content_gaps": content_gaps,
            "weak_spots": weak_spots,
        }

    def add_pillar(
        self,
        pillar_topic: str,
        pillar_keyword: str,
        pillar_content_type: str,
        volume_bucket: str,
        clusters: Optional[list] = None,
    ):
        """Add a pillar topic (topical-authority mode only)."""
        if "topical_authority" not in self.data:
            self.data["topical_authority"] = {"pillars": [], "content_creation_order": []}

        self.data["topical_authority"]["pillars"].append({
            "pillar_topic": pillar_topic,
            "pillar_keyword": pillar_keyword,
            "pillar_content_type": pillar_content_type,
            "volume_bucket": volume_bucket,
            "clusters": clusters or [],
        })

    def set_content_creation_order(self, steps: list):
        """Set the recommended content creation order (topical-authority mode)."""
        if "topical_authority" not in self.data:
            self.data["topical_authority"] = {"pillars": [], "content_creation_order": []}
        self.data["topical_authority"]["content_creation_order"] = steps

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.data, indent=indent, ensure_ascii=False)

    def save(self, path: str):
        """Save JSON output to file."""
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())
        print(f"✅ Saved keyword research to {path}")
        print(f"   {self.data['meta']['total_keywords']} keywords, "
              f"{len(self.data['questions'])} questions, "
              f"{len(self.data['content_opportunities'])} content opportunities")


def validate(filepath: str) -> bool:
    """Validate a keyword research JSON file against the expected schema."""
    with open(filepath, "r") as f:
        data = json.load(f)

    errors = []

    # Check required top-level keys
    required_keys = {"meta", "keywords", "questions", "content_opportunities", "competitive_insights"}
    missing = required_keys - set(data.keys())
    if missing:
        errors.append(f"Missing top-level keys: {missing}")

    # Validate meta
    meta = data.get("meta", {})
    if not meta.get("seed_keyword"):
        errors.append("meta.seed_keyword is required")
    if meta.get("mode") not in ("standard", "topical-authority"):
        errors.append(f"meta.mode must be 'standard' or 'topical-authority', got '{meta.get('mode')}'")

    # Validate keywords
    valid_intents = {"informational", "navigational", "commercial", "transactional"}
    valid_buckets = {"very_low", "low", "medium", "high", "very_high"}
    valid_difficulties = {"easy", "medium", "hard", "very_hard"}

    for i, kw in enumerate(data.get("keywords", [])):
        if not kw.get("keyword"):
            errors.append(f"keywords[{i}].keyword is required")
        if kw.get("search_intent") not in valid_intents:
            errors.append(f"keywords[{i}].search_intent '{kw.get('search_intent')}' invalid")
        if kw.get("volume_bucket") not in valid_buckets:
            errors.append(f"keywords[{i}].volume_bucket '{kw.get('volume_bucket')}' invalid")
        if kw.get("difficulty") not in valid_difficulties:
            errors.append(f"keywords[{i}].difficulty '{kw.get('difficulty')}' invalid")

    # Validate topical authority if present
    if meta.get("mode") == "topical-authority":
        if "topical_authority" not in data:
            errors.append("topical-authority mode requires 'topical_authority' key")

    if errors:
        print(f"❌ Validation failed with {len(errors)} error(s):")
        for e in errors:
            print(f"   - {e}")
        return False
    else:
        print(f"✅ Valid keyword research JSON")
        print(f"   {len(data.get('keywords', []))} keywords")
        print(f"   {len(data.get('questions', []))} questions")
        print(f"   {len(data.get('content_opportunities', []))} content opportunities")
        return True


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] != "validate":
        print("Usage: python3 generate_output.py validate <path-to-json>")
        sys.exit(1)
    
    success = validate(sys.argv[2])
    sys.exit(0 if success else 1)
