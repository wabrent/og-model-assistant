#!/usr/bin/env python3
"""
Explore AlphaSense module in OpenGradient SDK.
"""
import opengradient as og
import inspect

print("Exploring AlphaSense module...")
print("=" * 50)

if hasattr(og, 'alphasense'):
    alphasense = og.alphasense
    print(f"AlphaSense module: {alphasense}")
    
    # List all attributes
    print("\nAttributes:")
    for attr in dir(alphasense):
        if not attr.startswith('_'):
            obj = getattr(alphasense, attr)
            print(f"  {attr}: {type(obj).__name__}")
            if isinstance(obj, type):
                print(f"    (class)")
                # Check if it's a model class
                if 'model' in attr.lower() or 'quant' in attr.lower() or 'predict' in attr.lower():
                    print(f"    -> Potential ML model class")
                    # Inspect signature
                    try:
                        sig = inspect.signature(obj.__init__)
                        print(f"      __init__{sig}")
                    except:
                        pass
    
    # Check BaseModel
    if hasattr(alphasense, 'BaseModel'):
        BaseModel = alphasense.BaseModel
        print(f"\nBaseModel class: {BaseModel}")
        print("  Methods:")
        for attr in dir(BaseModel):
            if not attr.startswith('_'):
                print(f"    {attr}")
    
    # Check create_run_model_tool
    if hasattr(alphasense, 'create_run_model_tool'):
        print(f"\ncreate_run_model_tool: {alphasense.create_run_model_tool}")
        try:
            sig = inspect.signature(alphasense.create_run_model_tool)
            print(f"  Signature: {sig}")
        except:
            pass
    
    # Check run_model_tool
    if hasattr(alphasense, 'run_model_tool'):
        print(f"\nrun_model_tool: {alphasense.run_model_tool}")
        try:
            sig = inspect.signature(alphasense.run_model_tool)
            print(f"  Signature: {sig}")
        except:
            pass
    
    # Try to import Alpha class
    if hasattr(og, 'Alpha'):
        Alpha = og.Alpha
        print(f"\nog.Alpha class: {Alpha}")
        print("  Methods:")
        for attr in dir(Alpha):
            if not attr.startswith('_'):
                print(f"    {attr}")
    
    # Check if there's a way to list available models
    print("\n" + "=" * 50)
    print("Trying to discover ML models...")
    
    # Try to instantiate BaseModel with private key
    from core.config import settings
    if hasattr(alphasense, 'BaseModel'):
        try:
            model = alphasense.BaseModel(private_key=settings.private_key)
            print(f"  Created BaseModel instance: {model}")
        except Exception as e:
            print(f"  Error creating BaseModel: {e}")
    
    # Try to use run_model_tool
    if hasattr(alphasense, 'run_model_tool'):
        print("\n  Testing run_model_tool...")
        try:
            # Need to know model name and inputs
            result = alphasense.run_model_tool(
                model_name="bitquant",
                inputs={"symbol": "ETH/USDT", "horizon": "24h"}
            )
            print(f"    Result: {result}")
        except Exception as e:
            print(f"    Error: {e}")
            
else:
    print("AlphaSense module not found in OpenGradient SDK")