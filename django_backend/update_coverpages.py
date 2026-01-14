#!/usr/bin/env python
"""
Script to update candidate information sections in coverpage templates
"""

# Lines to update (excluding Biology Paper 2 at line 981)
lines_to_update = [5983, 6443, 6907, 8300, 8751, 9201, 9644]

# Read the file
with open('api/coverpage_templates.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines in file: {len(lines)}")

# Check which class each line belongs to
for line_num in lines_to_update:
    # Search backwards for the class definition
    for i in range(line_num - 1, max(0, line_num - 500), -1):
        if 'class ' in lines[i] and 'Coverpage:' in lines[i]:
            class_name = lines[i].strip()
            print(f"Line {line_num}: {class_name}")
            break
