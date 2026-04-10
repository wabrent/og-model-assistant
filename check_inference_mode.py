#!/usr/bin/env python3
"""
Check InferenceMode enum values.
"""
import opengradient as og

print("InferenceMode enum:")
InferenceMode = og.InferenceMode
for member in InferenceMode:
    print(f"  {member.name}: {member.value}")

# Also check if there are default values
print("\nDefault inference mode:", InferenceMode.VANILLA)

# Check Alpha class default
from core.config import settings
alpha = og.Alpha(private_key=settings.private_key)
print(f"\nAlpha instance created")

# Try to infer with correct parameters but unknown CID
# Maybe there's a test CID
print("\nTrying to find example model CID...")
# Look for any CID in SDK
import opengradient.types as types
for attr in dir(types):
    if 'CID' in attr or 'MODEL' in attr:
        val = getattr(types, attr)
        print(f"  {attr}: {val}")

# Check client.alpha for constants
import opengradient.client.alpha as alpha_module
for attr in dir(alpha_module):
    if 'CID' in attr or 'EXAMPLE' in attr:
        val = getattr(alpha_module, attr)
        print(f"  alpha.{attr}: {val}")