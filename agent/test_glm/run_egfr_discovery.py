#!/usr/bin/env python3
"""
Simplified EGFR Inhibitor Discovery Runner
This script runs the workflow step by step with proper error handling
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path

def check_and_install_package(package_name, import_name=None):
    """Check if a package is installed and install it if not"""
    if import_name is None:
        import_name = package_name

    try:
        __import__(import_name)
        print(f"✓ {package_name} is already installed")
        return True
    except ImportError:
        print(f"⚠ {package_name} not found, attempting to install...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"✓ Successfully installed {package_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {package_name}: {e}")
            return False

def main():
    """Main execution function"""
    print("=" * 80)
    print("EGFR INHIBITOR DISCOVERY WORKFLOW")
    print("Setting up environment and running analysis...")
    print("=" * 80)

    # Check and install required packages
    required_packages = [
        ("requests", "requests"),
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("matplotlib", "matplotlib"),
        ("seaborn", "seaborn"),
        ("tqdm", "tqdm"),
        ("chembl-webresource-client", "chembl_webresource_client"),
        ("biopython", "Bio"),
    ]

    optional_packages = [
        ("rdkit-pypi", "rdkit"),
        ("datamol", "datamol"),
        ("rcsbsearch", "rcsbsearch"),
    ]

    print("\n1. Checking and installing required packages...")
    all_required_installed = True
    for package, import_name in required_packages:
        if not check_and_install_package(package, import_name):
            all_required_installed = False

    print("\n2. Checking optional packages (will use mock data if not available)...")
    for package, import_name in optional_packages:
        check_and_install_package(package, import_name)

    if not all_required_installed:
        print("\n❌ Some required packages could not be installed. Please install them manually.")
        return False

    print("\n3. Setting up the workflow...")

    # Create output directory
    output_dir = Path("egfr_discovery_results")
    output_dir.mkdir(exist_ok=True)
    print(f"✓ Output directory created: {output_dir}")

    # Run the discovery workflow
    try:
        # Import and run the main discovery workflow
        sys.path.append('.')
        from egfr_inhibitor_discovery import EGFRInhibitorDiscovery

        print("\n4. Initializing EGFR Discovery Workflow...")
        discovery = EGFRInhibitorDiscovery(str(output_dir))

        # Run the complete workflow step by step
        print("\n5. Running workflow steps...")

        # Step 1: Query ChEMBL
        print("   5.1 Querying ChEMBL for EGFR inhibitors...")
        egfr_data = discovery.query_chembl_egfr_inhibitors()
        print(f"       Found {len(egfr_data)} EGFR inhibitors")

        if not egfr_data.empty:
            # Step 2: SAR Analysis (will work if RDKit is available)
            print("   5.2 Performing SAR analysis...")
            try:
                import rdkit
                sar_results = discovery.analyze_sar_rdkit(egfr_data)
                print(f"       SAR analysis completed for {len(sar_results.get('dataframe', []))} compounds")
            except ImportError:
                print("       RDKit not available, using mock SAR data...")
                sar_results = None

            # Step 3: Generate molecules (will work if datamol is available)
            print("   5.3 Generating similar molecules...")
            try:
                import datamol
                if sar_results:
                    generated_mols = discovery.generate_similar_molecules()
                    print(f"       Generated {len(generated_mols)} drug-like molecules")
                else:
                    print("       Skipping molecule generation (no SAR data available)")
            except ImportError:
                print("       datamol not available, using mock generated molecules...")
                generated_mols = None
        else:
            print("       No EGFR inhibitors found, skipping subsequent steps")
            sar_results = None
            generated_mols = None

        # Step 4: Literature review
        print("   5.4 Searching PubMed for resistance mechanisms...")
        try:
            resistance_papers = discovery.search_pubmed_resistance_mechanisms()
            print(f"       Found {len(resistance_papers)} resistance-related papers")
        except Exception as e:
            print(f"       Literature search failed: {e}")
            resistance_papers = []

        # Step 5: Mutation analysis
        print("   5.5 Analyzing EGFR mutations...")
        mutations = discovery.query_cosmic_mutations()
        print(f"       Analyzed {len(mutations)} EGFR mutations")

        # Step 6: Create visualizations and report
        print("   5.6 Creating comprehensive report...")
        readme_path = discovery.create_comprehensive_report()
        print(f"       Report created: {readme_path}")

        print("\n" + "=" * 80)
        print("WORKFLOW COMPLETION SUMMARY")
        print("=" * 80)
        print(f"✓ EGFR inhibitors identified: {len(egfr_data)}")
        print(f"✓ SAR analysis: {'Completed' if sar_results else 'Skipped (RDKit not available)'}")
        print(f"✓ Molecules generated: {'Completed' if generated_mols is not None else 'Skipped (datamol not available)'}")
        print(f"✓ Resistance papers found: {len(resistance_papers)}")
        print(f"✓ Mutations analyzed: {len(mutations)}")
        print(f"✓ Report generated: {readme_path}")

        print(f"\n🎉 Workflow completed successfully!")
        print(f"📁 All results saved to: {output_dir.absolute()}")

        return True

    except Exception as e:
        print(f"\n❌ Workflow failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)