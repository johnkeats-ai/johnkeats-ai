_current_user_id = None

def set_current_user(user_id: str):
    """Called by main.py when a new WebSocket session starts."""
    global _current_user_id
    _current_user_id = user_id


def save_to_passage(
    uncertainty_text: str,
    theme: str,
    status: str = "open"
) -> dict:
    """Saves a key uncertainty to the user's Dark Passage constellation.
    Call silently whenever the user mentions something they are thinking about,
    working through, or uncertain about. Save generously — even casual mentions
    of what is on their mind are worth preserving for future sessions.
    uncertainty_text: 10-20 word summary in user's own language.
    theme: one of career, relationship, identity, health, creative,
           financial, existential, family, other.
    status: one of open, holding, resolved."""
    from google.cloud import firestore
    db = firestore.Client(project="johnkeats-ai")
    doc_ref = db.collection("passages").document()
    doc_ref.set({
        "text": uncertainty_text,
        "theme": theme,
        "status": status,
        "user_id": _current_user_id,
        "created_at": firestore.SERVER_TIMESTAMP
    })
    return {"saved": True, "id": doc_ref.id}


def get_passage_history(
    theme_filter: str = "",
    limit: int = 5
) -> dict:
    """Retrieves recent uncertainties from the user's Dark Passage.
    Use at the start of sessions or when user references past conversations.
    Do NOT read results back to user. Use to inform your listening.
    theme_filter: optional, one of career, relationship, identity, etc.
    limit: number of entries to return, default 5."""
    from google.cloud import firestore
    db = firestore.Client(project="johnkeats-ai")
    query = db.collection("passages").order_by(
        "created_at", direction=firestore.Query.DESCENDING
    ).limit(limit)
    if _current_user_id:
        query = query.where("user_id", "==", _current_user_id)
    if theme_filter:
        query = query.where("theme", "==", theme_filter)
    results = []
    for doc in query.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    return {"passages": results}


def resolve_uncertainty(
    uncertainty_id: str,
    resolution_note: str = ""
) -> dict:
    """Marks a saved uncertainty as resolved.
    Use when user says 'I decided', 'it worked out', 'I'm past that'.
    Confirm with user before calling: 'Sounds like that one found its shape.'
    uncertainty_id: the document ID of the uncertainty.
    resolution_note: optional 10-20 word note on how it resolved."""
    from google.cloud import firestore
    db = firestore.Client(project="johnkeats-ai")
    doc_ref = db.collection("passages").document(uncertainty_id)
    doc_ref.update({
        "status": "resolved",
        "resolution_note": resolution_note,
        "resolved_at": firestore.SERVER_TIMESTAMP
    })
    return {"resolved": True, "id": uncertainty_id}


def crisis_resources(locale: str = "en-AU") -> dict:
    """Provides localised crisis support information.
    ONLY call when user explicitly expresses self-harm or suicidal thoughts.
    Never call preemptively.
    locale: ISO locale string, default en-AU."""
    resources = {
        "en-AU": {
            "name": "Lifeline Australia",
            "phone": "13 11 14",
            "available": "24 hours, 7 days"
        },
        "en-US": {
            "name": "988 Suicide and Crisis Lifeline",
            "phone": "988",
            "available": "24 hours, 7 days"
        },
        "en-GB": {
            "name": "Samaritans",
            "phone": "116 123",
            "available": "24 hours, 7 days"
        }
    }
    default = {
        "name": "International Association for Suicide Prevention",
        "url": "https://www.iasp.info/resources/Crisis_Centres/",
        "available": "Directory of crisis centres worldwide"
    }
    return resources.get(locale, default)
