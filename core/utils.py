import re

# Database constants
DB_PATH = "./epfl_cours_db"
COLLECTION_NAME = "cours_epfl"
TOP_K_RETRIEVAL = 20  # How many candidates each retrieval pass (BM25 + semantic) returns

# Allowlist for sections (separate Bachelor and Master lists)
BACHELOR_SECTIONS = [
    'Architecture', 'Chimie', 'Chimie et génie chimique', 'Génie chimique',
    'Génie civil', 'Génie mécanique', 'Génie électrique et électronique',
    'Informatique', 'Ingénierie des sciences du vivant', 'Mathématiques',
    'Microtechnique', 'Physique', 'Science et génie des matériaux',
    'Sciences et ingénierie de l\'environnement', 'Systèmes de communication'
]

MASTER_SECTIONS = [
    'Architecture', 'Chimie moléculaire et biologique', 'Data Science',
    'Génie chimique et biotechnologie', 'Génie civil', 'Génie mécanique',
    'Génie nucléaire', 'Génie électrique et électronique', 'Humanités digitales',
    'Informatique', 'Informatique - Cybersecurity', 'Ingénierie des sciences du vivant',
    'Ingénierie financière', 'Ingénierie mathématique', 'Ingénierie physique',
    'Management durable et technologie', 'Management, technologie et entrepreneuriat',
    'Mathématiques - master', 'Micro- and Nanotechnologies for Integrated Systems',
    'Microtechnique', 'Neuro-X', 'Physique - master', 'Robotique',
    'Science et génie des matériaux', 'Science et ingénierie computationnelles',
    'Science et ingénierie quantiques', 'Science et technologie de l\'énergie',
    'Sciences et ingénierie de l\'environnement', 'Statistique', 'Systèmes urbains'
]

# Combined list of (display_name, section_name, level), sorted alphabetically
ALL_SECTIONS = sorted(
    [(f"{s} (Bachelor)", s, "Bachelor") for s in BACHELOR_SECTIONS] +
    [(f"{s} (Master)", s, "Master") for s in MASTER_SECTIONS],
    key=lambda x: x[0]
)


def parse_course_metadata(content):
    """Extract course code, credits, professor, and language from content text."""
    metadata = {
        "code": "N/A",
        "credits": "N/A",
        "professor": "Non spécifié",
        "language": "Non spécifié"
    }

    code_match = re.search(r'\b([A-Z]+-\d+)\b', content)
    if code_match:
        metadata["code"] = code_match.group(1)

    credits_match = re.search(r'(\d+)\s+crédits?', content, re.IGNORECASE)
    if credits_match:
        metadata["credits"] = credits_match.group(1)

    prof_match = re.search(
        r'Enseignant[:\s]+(.+?)(?=\s+(?:Langue|Résumé|Summary|Content|Contenu|Lire|Keywords|Mots-clés)[:.\s])',
        content, re.IGNORECASE
    )
    if prof_match:
        professor = prof_match.group(1).strip()
        if len(professor) <= 60:
            metadata["professor"] = professor

    lang_match = re.search(
        r'Langue[:\s]+(.+?)(?=\s+(?:Résumé|Summary|Content|Contenu|Enseignant|Lire|Keywords|Mots-clés)[:.\s])',
        content, re.IGNORECASE
    )
    if lang_match:
        language = lang_match.group(1).strip()
        if len(language) <= 30:
            metadata["language"] = language

    return metadata


def calculate_score_percentage(result):
    """Return the pre-computed display_score from a result dict (falls back to 0.5)."""
    return result.get('display_score', 0.5)
