"""
Script to add grid CSS to all coverpages
"""
import re

# Read the file
with open('api/coverpage_templates.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern: Find .info-row-full CSS that doesn't have .info-row-grid after it
# Replace it to include the grid styles

pattern = r'''(        \.info-row \{\{
            display: flex;
            align-items: center;
        \}\}
        
        \.info-row-full \{\{
            grid-column: 1 / -1;
            display: flex;
            align-items: center;
        \}\}
        
        \.info-label \{\{)'''

replacement = r'''        .info-row {{
            display: flex;
            align-items: center;
        }}
        
        .info-row-full {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .info-row-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .info-row-item {{
            display: flex;
            align-items: center;
        }}
        
        .info-label {{'''

content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

# Write back
with open('api/coverpage_templates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated CSS for all coverpages!")
