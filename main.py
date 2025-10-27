#!/usr/bin/env python3
"""
macOS Kernel Extensions Analysis Suite
Main entry point for the complete kext analysis workflow.
"""

import os
import sys
import subprocess
import argparse

def run_script(script_name, description):
    """
    Run a Python script and handle errors.
    
    Args:
        script_name (str): Name of the script to run
        description (str): Description of what the script does
    """
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:")
            print(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}:")
        print(f"Return code: {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"Script {script_name} not found")
        return False

def check_data_files():
    """
    Check if required data files exist.
    
    Returns:
        bool: True if all required files exist
    """
    required_files = [
        'vmapple_kext/kexts_data.json',
        'host_kext/kexts_data.json'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("Missing required data files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        print("\nPlease run the analysis scripts first to generate data files.")
        return False
    
    return True

def main():
    """
    Main function for the kext analysis suite.
    """
    parser = argparse.ArgumentParser(
        description='macOS Kernel Extensions Analysis Suite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --all                    # Run complete analysis workflow
  python main.py --analyze               # Only analyze kexts
  python main.py --compare               # Only compare datasets
  python main.py --visualize             # Only generate visualizations
  python main.py --vmapple               # Analyze VM Apple kexts only
  python main.py --host                  # Analyze Host kexts only
        """
    )
    
    parser.add_argument('--all', action='store_true',
                       help='Run complete analysis workflow')
    parser.add_argument('--analyze', action='store_true',
                       help='Analyze kexts and generate data files')
    parser.add_argument('--compare', action='store_true',
                       help='Compare VM Apple and Host kext datasets')
    parser.add_argument('--visualize', action='store_true',
                       help='Generate HTML visualization files')
    parser.add_argument('--vmapple', action='store_true',
                       help='Analyze VM Apple kexts only')
    parser.add_argument('--host', action='store_true',
                       help='Analyze Host kexts only')
    parser.add_argument('--check', action='store_true',
                       help='Check if required data files exist')
    
    args = parser.parse_args()
    
    print("macOS Kernel Extensions Analysis Suite")
    print("=" * 60)
    
    # If no arguments provided, show help
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    # Check data files if requested
    if args.check:
        if check_data_files():
            print("✓ All required data files exist")
        else:
            print("✗ Some required data files are missing")
        return
    
    # Run complete workflow
    if args.all:
        print("Running complete analysis workflow...")
        
        # Step 1: Analyze kexts
        if not run_script('analyze_kexts.py', 'Kext Analysis'):
            print("Failed to analyze kexts. Exiting.")
            return
        
        # Step 2: Compare datasets
        if check_data_files():
            if not run_script('compare_kexts.py', 'Dataset Comparison'):
                print("Failed to compare datasets. Continuing...")
        else:
            print("Skipping comparison - data files not found")
        
        # Step 3: Generate visualizations
        if check_data_files():
            if not run_script('generate_visualizations.py', 'Visualization Generation'):
                print("Failed to generate visualizations. Continuing...")
        else:
            print("Skipping visualization generation - data files not found")
        
        print("\n" + "="*60)
        print("Complete analysis workflow finished!")
        print("="*60)
        return
    
    # Run individual components
    if args.analyze:
        run_script('analyze_kexts.py', 'Kext Analysis')
    
    if args.compare:
        if check_data_files():
            run_script('compare_kexts.py', 'Dataset Comparison')
        else:
            print("Cannot compare datasets - required data files not found")
    
    if args.visualize:
        if check_data_files():
            run_script('generate_visualizations.py', 'Visualization Generation')
        else:
            print("Cannot generate visualizations - required data files not found")
    
    if args.vmapple:
        print("VM Apple analysis not implemented as separate script")
        print("Use --analyze to generate data files")
    
    if args.host:
        print("Host analysis not implemented as separate script")
        print("Use --analyze to generate data files")

if __name__ == '__main__':
    main()
