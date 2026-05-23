import re

# Database constants
DB_PATH = "./epfl_cours_db"
COLLECTION_NAME = "cours_epfl"
TOP_K_RETRIEVAL = 20  # How many candidates each retrieval pass (BM25 + semantic) returns

# Allowlist for sections (separate Bachelor and Master lists)
BACHELOR_SECTIONS = [
    'Architecture', 'Chemistry', 'Chemistry and Chemical Engineering', 'Chemical Engineering',
    'Civil Engineering', 'Mechanical Engineering', 'Electrical and Electronic Engineering',
    'Computer Science', 'Life Sciences Engineering', 'Mathematics',
    'Microengineering', 'Physics', 'Materials Science and Engineering',
    'Environmental Sciences and Engineering', 'Communication Systems'
]

MASTER_SECTIONS = [
    'Architecture', 'Molecular and Biological Chemistry', 'Data Science',
    'Chemical Engineering and Biotechnology', 'Civil Engineering', 'Mechanical Engineering',
    'Nuclear Engineering', 'Electrical and Electronic Engineering', 'Digital Humanities',
    'Computer Science', 'Computer Science - Cybersecurity', 'Life Sciences Engineering',
    'Financial Engineering', 'Mathematical Engineering', 'Physics Engineering',
    'Sustainable Management and Technology', 'Management, Technology and Entrepreneurship',
    'Mathematics - master', 'Micro- and Nanotechnologies for Integrated Systems',
    'Microengineering', 'Neuro-X', 'Physics - master', 'Robotics',
    'Materials Science and Engineering', 'Computational Science and Engineering',
    'Quantum Science and Engineering', 'Energy Science and Technology',
    'Environmental Sciences and Engineering', 'Statistics', 'Urban Systems'
]
SECTION_LANGUAGE_MAPPING = {
    # Bachelor
    'Architecture': 'Architecture',
    'Chemistry': 'Chimie',
    'Chemistry and Chemical Engineering': 'Chimie et génie chimique',
    'Chemical Engineering': 'Génie chimique',
    'Civil Engineering': 'Génie civil',
    'Mechanical Engineering': 'Génie mécanique',
    'Electrical and Electronic Engineering': 'Génie électrique et électronique',
    'Computer Science': 'Informatique',
    'Life Sciences Engineering': 'Ingénierie des sciences du vivant',
    'Mathematics': 'Mathématiques',
    'Microengineering': 'Microtechnique',
    'Physics': 'Physique',
    'Materials Science and Engineering': 'Science et génie des matériaux',
    'Environmental Sciences and Engineering': 'Sciences et ingénierie de l\'environnement',
    'Communication Systems': 'Systèmes de communication',
    # Master
    'Molecular and Biological Chemistry': 'Chimie moléculaire et biologique',
    'Data Science': 'Data Science',
    'Chemical Engineering and Biotechnology': 'Génie chimique et biotechnologie',
    'Nuclear Engineering': 'Génie nucléaire',
    'Digital Humanities': 'Humanités digitales',
    'Computer Science - Cybersecurity': 'Informatique - Cybersecurity',
    'Financial Engineering': 'Ingénierie financière',
    'Mathematical Engineering': 'Ingénierie mathématique',
    'Physics Engineering': 'Ingénierie physique',
    'Sustainable Management and Technology': 'Management durable et technologie',
    'Management, Technology and Entrepreneurship': 'Management, technologie et entrepreneuriat',
    'Mathematics - master': 'Mathématiques - master',
    'Micro- and Nanotechnologies for Integrated Systems': 'Micro- and Nanotechnologies for Integrated Systems',
    'Neuro-X': 'Neuro-X',
    'Physics - master': 'Physique - master',
    'Robotics': 'Robotique',
    'Computational Science and Engineering': 'Science et ingénierie computationnelles',
    'Quantum Science and Engineering': 'Science et ingénierie quantiques',
    'Energy Science and Technology': 'Science et technologie de l\'énergie',
    'Statistics': 'Statistique',
    'Urban Systems': 'Systèmes urbains',
}

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
        "professor": "Not specified",
        "language": "Not specified"
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
