#!/usr/bin/env python3
"""
Explore ModelHub in OpenGradient SDK.
"""
import opengradient as og
import inspect

print("Exploring ModelHub...")
print("=" * 50)

# Get ModelHub class
ModelHub = og.ModelHub
print(f"ModelHub: {ModelHub}")

# Inspect __init__ signature
try:
    sig = inspect.signature(ModelHub.__init__)
    print(f"\nModelHub.__init__ signature:")
    print(f"  {sig}")
except Exception as e:
    print(f"  Cannot get signature: {e}")

# Check class attributes
print("\nModelHub attributes and methods:")
for attr in dir(ModelHub):
    if not attr.startswith('_'):
        obj = getattr(ModelHub, attr)
        print(f"  {attr}: {type(obj).__name__}")

# Try to instantiate ModelHub without arguments
print("\nTrying to instantiate ModelHub...")
try:
    model_hub = ModelHub()
    print(f"  Success: {model_hub}")
    
    # Call methods
    print("\n  Calling list_models()...")
    if hasattr(model_hub, 'list_models'):
        models = model_hub.list_models()
        print(f"    Result: {type(models)}")
        if isinstance(models, list):
            print(f"    Number of models: {len(models)}")
            for i, model in enumerate(models[:5]):
                print(f"      {i+1}. {model}")
        else:
            print(f"    Models: {models}")
    
    # Check for other methods
    print("\n  Checking for predict method...")
    if hasattr(model_hub, 'predict'):
        print("    predict() exists")
        # Get signature
        try:
            sig = inspect.signature(model_hub.predict)
            print(f"    predict signature: {sig}")
        except:
            pass
    
    # Check for get_model
    if hasattr(model_hub, 'get_model'):
        print("\n  Checking get_model()...")
        # Try to get a specific model
        try:
            model = model_hub.get_model("bitquant")
            print(f"    Got model: {model}")
        except Exception as e:
            print(f"    Error: {e}")
            
except Exception as e:
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()

# Check ModelRepository
print("\n" + "=" * 50)
print("Exploring ModelRepository...")
ModelRepository = og.ModelRepository
print(f"ModelRepository: {ModelRepository}")

# Try to see if there are ML model classes
print("\nChecking for ML model classes in opengradient.agents...")
if hasattr(og, 'agents'):
    agents = og.agents
    print("  Agents module attributes:")
    for attr in dir(agents):
        if not attr.startswith('_'):
            print(f"    {attr}")
            obj = getattr(agents, attr)
            if isinstance(obj, type):
                print(f"      (class)")

# Check alphasense module
if hasattr(og, 'alphasense'):
    alphasense = og.alphasense
    print("\n  AlphaSense module attributes:")
    for attr in dir(alphasense):
        if not attr.startswith('_') and 'model' in attr.lower() or 'quant' in attr.lower():
            print(f"    {attr}")