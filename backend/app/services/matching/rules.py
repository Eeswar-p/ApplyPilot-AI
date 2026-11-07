from typing import List, Dict, Optional
from pydantic import BaseModel

class ScannedField(BaseModel):
    id: str
    name: str
    type: str
    label: str
    options: Optional[List[str]] = None
    value: str

class MatchProposal(BaseModel):
    field_id: str
    profile_key: str
    proposed_value: str
    match_method: str = "rules"
    confidence_category: str = "high"
    requires_review: bool = True

# Canonical rules mapping for MVP
# Maps profile keys to a list of possible label/name aliases
RULES_MAPPING = {
    "first_name": ["first name", "given name", "fname"],
    "last_name": ["last name", "surname", "lname"],
    "email": ["email", "e-mail", "email address"],
    "phone": ["phone", "telephone", "mobile", "cell phone"],
    "linkedin": ["linkedin", "linked in url", "linkedin profile"],
    "github": ["github", "git hub url", "portfolio"],
}

def clean_string(s: str) -> str:
    return s.lower().replace("_", " ").strip()

def rule_based_match(fields: List[ScannedField], profile_facts: Dict[str, str]) -> List[MatchProposal]:
    proposals = []
    
    for field in fields:
        clean_label = clean_string(field.label)
        clean_name = clean_string(field.name)
        
        matched_key = None
        for key, aliases in RULES_MAPPING.items():
            if any(alias in clean_label or alias in clean_name for alias in aliases):
                matched_key = key
                break
                
        if matched_key and matched_key in profile_facts:
            proposals.append(MatchProposal(
                field_id=field.id,
                profile_key=matched_key,
                proposed_value=profile_facts[matched_key],
                match_method="rules",
                confidence_category="high",
                requires_review=True
            ))
            
    return proposals
