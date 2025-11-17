#!/usr/bin/env python3
"""
Master script to generate both PCM and Pricing datasets.
Scale is controlled by TARGET_PRODUCTS variable in the individual scripts.

Usage: python3 GENERATE_ALL.py
"""

import subprocess
import sys
import re
from pathlib import Path

def get_target_products():
    """Read TARGET_PRODUCTS from GENERATE_1000.py"""
    script_path = Path(__file__).parent / 'GENERATE_1000.py'
    with open(script_path, 'r') as f:
        content = f.read()
        match = re.search(r'TARGET_PRODUCTS\s*=\s*(\d+)', content)
        if match:
            return int(match.group(1))
    return 1000  # fallback

def run_script(script_name):
    """Run a Python script and return success status."""
    script_path = Path(__file__).parent / script_name
    print(f"\n{'='*70}")
    print(f"Running {script_name}...")
    print(f"{'='*70}\n")
    
    result = subprocess.run([sys.executable, str(script_path)], capture_output=False)
    return result.returncode == 0

def main():
    target = get_target_products()
    
    print("="*70)
    print(f"GENERATING COMPLETE {target}-PRODUCT DATASETS")
    print("="*70)
    print()
    print("This will generate:")
    print(f"  1. qb-pcm-{target} - Product catalog data ({target} products)")
    print(f"  2. qb-pricing-{target} - Pricing data for those products")
    print()
    print("="*70)
    
    # Step 1: Generate PCM data
    if not run_script('GENERATE_1000.py'):
        print(f"\n❌ ERROR: Failed to generate qb-pcm-{target} dataset")
        return 1
    
    # Step 2: Generate Pricing data
    if not run_script('GENERATE_PRICING_1000.py'):
        print(f"\n❌ ERROR: Failed to generate qb-pricing-{target} dataset")
        return 1
    
    print()
    print("="*70)
    print("✓ ALL DATASETS GENERATED SUCCESSFULLY!")
    print("="*70)
    print()
    print("Import sequence:")
    print()
    print("  # Step 1: Import product catalog")
    print("  sfdx sfdmu:run --sourceusername csvfile \\")
    print(f"    --path qb-pcm-{target} \\")
    print("    --targetusername <your-org>")
    print()
    print("  # Step 2: Import pricing")
    print("  sfdx sfdmu:run --sourceusername csvfile \\")
    print(f"    --path qb-pricing-{target} \\")
    print("    --targetusername <your-org>")
    print()
    print("Both datasets use UPSERT - works on clean orgs OR orgs with existing data!")
    print("="*70)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

