"""
Script to update instruction list format from 'a.' to '(a)' format
"""
import re

# Read the file
with open('api/coverpage_templates.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern 1: Update ol tags to remove type="a" and add counter styles
# Replace: <ol type="a" style="..." with <ol style="...; list-style: none; counter-reset: list-counter; margin-left: 20px;"
content = re.sub(
    r'<ol type="a"( style="[^"]*")',
    lambda m: f'<ol{m.group(1)[:-1]}; list-style: none; counter-reset: list-counter; margin-left: 20px;"',
    content
)

# Pattern 2: Update ol tags with only type="a" (no style)
content = re.sub(
    r'<ol type="a">',
    '<ol style="list-style: none; counter-reset: list-counter; margin-left: 20px;">',
    content
)

# Pattern 3: Update li tags to add counter increment and display
# Find patterns like: html += f'<li{class_attr}>{instruction}</li>\n'
# Replace with counter display
content = re.sub(
    r"html \+= f'(\s*)<li(\{class_attr\})?>(\{instruction\})</li>\\n'",
    r"html += f'\1<li\2 style=\"counter-increment: list-counter;\"><span>(' + chr(96+idx) + ') </span>\3</li>\\n'",
    content
)

# Write back
with open('api/coverpage_templates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated instruction list format successfully!")
