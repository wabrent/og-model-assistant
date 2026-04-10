#!/usr/bin/env python3
"""
Explore OpenGradient SDK capabilities.
"""
import opengradient as og
import inspect

print("OpenGradient SDK version:", og.__version__ if hasattr(og, '__version__') else 'unknown')
print("\nAvailable attributes:")
for attr in dir(og):
    if not attr.startswith('_'):
        obj = getattr(og, attr)
        print(f"  {attr}: {type(obj).__name__}")

# Check if there's MLModel class or similar
print("\nChecking for ML models...")
if hasattr(og, 'MLModel'):
    print("og.MLModel exists")
    mlmodel = og.MLModel
    for attr in dir(mlmodel):
        if not attr.startswith('_'):
            print(f"  MLModel.{attr}")

# Check LLM class
if hasattr(og, 'LLM'):
    print("\nog.LLM signature:")
    try:
        sig = inspect.signature(og.LLM.__init__)
        print(f"  __init__{sig}")
    except:
        pass

# Check if there's a hub API client
if hasattr(og, 'Hub'):
    print("\nog.Hub exists")
    hub = og.Hub
    for attr in dir(hub):
        if not attr.startswith('_'):
            print(f"  Hub.{attr}")

# Check ModelHub
if hasattr(og, 'ModelHub'):
    print("\nog.ModelHub exists")
    try:
        # Try to instantiate ModelHub
        from core.config import settings
        model_hub = og.ModelHub(private_key=settings.private_key)
        print(f"  ModelHub instance: {model_hub}")
        methods = [m for m in dir(model_hub) if not m.startswith('_')]
        print(f"  ModelHub methods: {methods}")
        
        # Try to list models
        if hasattr(model_hub, 'list_models'):
            print("\n  Trying to list models...")
            models = model_hub.list_models()
            print(f"    Found {len(models)} models")
            for model in models[:3]:
                print(f"    - {model}")
    except Exception as e:
        print(f"  Error with ModelHub: {e}")

# Check ModelRepository
if hasattr(og, 'ModelRepository'):
    print("\nog.ModelRepository exists")
    model_repo = og.ModelRepository
    for attr in dir(model_repo):
        if not attr.startswith('_'):
            print(f"  ModelRepository.{attr}")

# Try to instantiate LLM with private key
print("\nTrying to instantiate LLM...")
from core.config import settings
try:
    llm = og.LLM(private_key=settings.private_key)
    print(f"  LLM created: {llm}")
    # Check methods
    methods = [m for m in dir(llm) if not m.startswith('_')]
    print(f"  LLM methods: {methods[:10]}...")
except Exception as e:
    print(f"  Error creating LLM: {e}")