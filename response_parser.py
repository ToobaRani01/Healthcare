# response_parser.py
"""
Module for parsing structured responses from AI to extract disease, medication, and conclusion.
"""

def parse_structured_response(response_text):
    """
    Parses the GPT response to extract disease, medication, and conclusion.
    The response should follow a structured format with clear sections.
    Uses simple string operations instead of complex regex.
    
    Returns:
        tuple: (disease, probability, severity, medication, other_diagnoses, conclusion)
    """
    case_description = None
    disease = None
    probability = None
    severity = None
    medication = None
    other_diagnoses = None
    disclaimer = None
    
    text_lower = response_text.lower()
    
    # Extract Case Description
    case_markers = ['**case description**', '**case description:**', 'case description:', 'understanding:', '**understanding:**']
    for marker in case_markers:
        if marker in text_lower:
            idx = text_lower.find(marker)
            if idx != -1:
                start_pos = idx + len(marker)
                remaining = response_text[start_pos:]
                next_section = remaining.lower().find('**')
                if next_section != -1:
                    case_description = remaining[:next_section].strip()
                else:
                    case_description = remaining.split('\n\n')[0].strip() if '\n\n' in remaining else remaining.strip()
                break
    
    # Extract Primary Diagnosis - look for "Primary Diagnosis:" section
    disease_markers = ['**primary diagnosis**', '**primary diagnosis:**', 'primary diagnosis:', 'disease diagnosis:', '**disease diagnosis:**']
    for marker in disease_markers:
        if marker in text_lower:
            idx = text_lower.find(marker)
            if idx != -1:
                start_pos = idx + len(marker)
                remaining = response_text[start_pos:]
                next_section = remaining.lower().find('**')
                if next_section != -1:
                    raw_disease = remaining[:next_section].strip()
                else:
                    raw_disease = remaining.split('\n\n')[0].strip() if '\n\n' in remaining else remaining.strip()
                
                # Extract probability from "(XX%)" if present
                import re
                prob_match = re.search(r'\((\d+)\s*%\)', raw_disease)
                if prob_match:
                    probability = prob_match.group(1) + "%"
                    disease = raw_disease.replace(prob_match.group(0), "").strip().strip('*').strip()
                else:
                    disease = raw_disease.strip('*').strip()
                break

    # Extract Severity Level - look for "Severity Level:" section
    severity_markers = ['**severity level**', '**severity level:**', 'severity level:']
    for marker in severity_markers:
        if marker in text_lower:
            idx = text_lower.find(marker)
            if idx != -1:
                start_pos = idx + len(marker)
                remaining = response_text[start_pos:]
                next_section = remaining.lower().find('**')
                if next_section != -1:
                    severity = remaining[:next_section].strip().strip('*').strip()
                else:
                    severity = remaining.split('\n\n')[0].strip().strip('*').strip() if '\n\n' in remaining else remaining.strip().strip('*').strip()
                break
    
    # Extract medication - look for "Medication:" section
    medication_markers = ['**medication**', '**medication:**', 'medication:', 'treatment:']
    for marker in medication_markers:
        if marker in text_lower:
            idx = text_lower.find(marker)
            if idx != -1:
                start_pos = idx + len(marker)
                remaining = response_text[start_pos:]
                # Find next section
                next_section = remaining.find('**')
                if next_section != -1:
                    medication = remaining[:next_section].strip()
                else:
                    if '\n\n' in remaining:
                        medication = remaining.split('\n\n')[0].strip()
                    else:
                        medication = remaining.strip()
                medication = medication.strip('*').strip()
                break

    # Extract Other Probable Diagnoses
    other_markers = ['**other probable diagnoses**', '**other probable diagnoses:**', 'other probable diagnoses:']
    for marker in other_markers:
        if marker in text_lower:
            idx = text_lower.find(marker)
            if idx != -1:
                start_pos = idx + len(marker)
                remaining = response_text[start_pos:]
                next_section = remaining.lower().find('**')
                if next_section != -1:
                    other_diagnoses = remaining[:next_section].strip().strip('*').strip()
                else:
                    other_diagnoses = remaining.split('\n\n')[0].strip().strip('*').strip() if '\n\n' in remaining else remaining.strip().strip('*').strip()
                break
    
    # Extract disclaimer (formerly conclusion)
    disclaimer_markers = ['**disclaimer**', '**disclaimer:**', 'disclaimer:', '**conclusion**', 'conclusion:', 'summary:', 'final note:', 'important note:']
    for marker in disclaimer_markers:
        if marker in text_lower:
            idx = text_lower.find(marker)
            if idx != -1:
                start_pos = idx + len(marker)
                remaining = response_text[start_pos:]
                # Disclaimer is usually at the end, so take rest
                disclaimer = remaining.strip()
                disclaimer = disclaimer.strip('*').strip()
                break
    
    # If disclaimer not found, try to get the last paragraph
    if not disclaimer:
        paragraphs = response_text.split('\n\n')
        if paragraphs:
            last_para = paragraphs[-1].strip()
            # Skip if it's too short or looks like a section header
            if len(last_para) > 20 and not last_para.startswith('**'):
                disclaimer = last_para
    
    return case_description, disease, probability, severity, medication, other_diagnoses, disclaimer

