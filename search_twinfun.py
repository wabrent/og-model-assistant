#!/usr/bin/env python3
"""
Search for TwinFun and MemSync references in OpenGradient SDK.
"""
import os
import re

sdk_path = "C:\\Users\\waabrent\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\opengradient"

patterns = [
    "twin",
    "mem",
    "sync",
    "replicate",
    "mirror",
    "clone",
    "model.*sync",
]

for root, dirs, files in os.walk(sdk_path):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            rel_path = os.path.relpath(filepath, sdk_path)
                            print(f"\n=== {rel_path} ===")
                            # Print first few matching lines
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if re.search(pattern, line, re.IGNORECASE):
                                    print(f"{i+1}: {line.strip()}")
                                    # Show context
                                    for j in range(max(0, i-2), min(len(lines), i+3)):
                                        if j != i:
                                            print(f"  {j+1}: {lines[j].strip()}")
                                    print("---")
                            break
            except:
                pass