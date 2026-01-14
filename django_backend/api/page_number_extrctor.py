import re

def extract_paper_number_from_name(paper_name: str) -> int:
    paper_name_upper = paper_name.upper()

    # Check for "PAPER II" first (most specific)
    if re.search(r'PAPER\s+II\b', paper_name_upper):
        return 2
    # Check for standalone "II" (most specific)
    if re.search(r'\bII\b', paper_name_upper):
        return 2
    
    if 'PILI' in paper_name_upper:
        return 2
    
    if 'KWANZA' in paper_name_upper:
        return 1
    
    if 'TATU' in paper_name_upper:
        return 3
    
    # Check for "PAPER I" (but not "PAPER II")
    if re.search(r'PAPER\s+I\b', paper_name_upper):
        return 1
    
    # Check for standalone "I" (but NOT part of "II")
    # Use negative lookahead to ensure "I" is not followed by another "I"
    if re.search(r'\bI\b(?!I)', paper_name_upper):
        return 1
    
    # Check for numeric "2"
    if re.search(r'\b2\b', paper_name_upper):
        return 2
    
    # Check for numeric "1"
    if re.search(r'\b1\b', paper_name_upper):
        return 1
    
    raise ValueError(f"Could not extract paper number from '{paper_name}'")