"""
Script to update candidate info layout to 2x2 grid format
"""
import re

# Read the file
with open('api/coverpage_templates.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to find the one-row layout
# Looking for: <div class="info-row-full" style="display: flex; gap: 20px;">
#   with multiple info-row items inside
old_pattern = r'''(<div class="candidate-info-grid">
                \{f'<div class="info-row-full"><span class="info-label">Name:</span><div class="info-field"></div></div>' if show_name else ''\}
                <div class="info-row-full" style="display: flex; gap: 20px;">
                    \{f'<div class="info-row" style="flex: 1;"><span class="info-label">AdmNo:</span><div class="info-field"></div></div>' if show_number else ''\}
                    \{f'<div class="info-row" style="flex: 1;"><span class="info-label">Class:</span><div class="info-field"></div></div>' if show_class else ''\}
                    \{f'<div class="info-row" style="flex: 1;"><span class="info-label">Date:</span><div class="info-field"></div></div>' if show_date else ''\}
                    <div class="info-row" style="flex: 1;"><span class="info-label">Sign:</span><div class="info-field"></div></div>
                </div>
            </div>)'''

new_pattern = '''<div class="candidate-info-grid">
                {f'<div class="info-row-full"><span class="info-label">NAME:</span><div class="info-field"></div></div>' if show_name else ''}
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">ADM NO:</span><div class="info-field"></div></div>' if show_number else ''}
                    <div class="info-row-item"><span class="info-label">CLASS:</span><div class="info-field"></div></div>
                </div>
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">DATE:</span><div class="info-field"></div></div>' if show_date else ''}
                    <div class="info-row-item"><span class="info-label">SIGNATURE:</span><div class="info-field"></div></div>
                </div>
            </div>'''

content = re.sub(old_pattern, new_pattern, content, flags=re.MULTILINE)

# Write back
with open('api/coverpage_templates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated candidate info layout successfully!")
