#!/usr/bin/env python3
"""
Search for model references in OpenGradient SDK.
"""
import os
import re

sdk_path = "C:\\Users\\waabrent\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\opengradient"

patterns = [
    "bitquant",
    "pricepredictor",
    "riskanalyzer",
    "model_cid",
    "cid",
    "quant",
    "predictor",
    "risk",
    "alpha",
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
                            # Extract a snippet
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if re.search(pattern, line, re.IGNORECASE):
                                    rel_path = os.path.relpath(filepath, sdk_path)
                                    print(f"{rel_path}:{i+1}: {line.strip()[:100]}")
                                    break
                            break  # Only print file once per pattern
            except:
                pass