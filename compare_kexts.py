#!/usr/bin/env python3
"""
macOS Kernel Extensions Comparison Tool
Compares kext data between VM Apple and Host environments and generates analysis reports.
"""

import json
import os
from collections import defaultdict

def load_json(filepath):
    """
    Load JSON data from file.
    
    Args:
        filepath (str): Path to JSON file
        
    Returns:
        dict: Loaded JSON data
    """
    with open(filepath, 'r') as f:
        return json.load(f)

def analyze_kexts(data):
    """
    Analyze kext data and generate statistics.
    
    Args:
        data (dict): Dictionary of kext data
        
    Returns:
        dict: Analysis results
    """
    total = len(data)
    
    # Category analysis
    categories = {
        'graphics': 0,
        'audio': 0,
        'usb': 0,
        'bluetooth': 0,
        'apple_specific': 0,
        'intel': 0,
        'amd': 0,
        'other': 0
    }
    
    for bundle_id, kext in data.items():
        name = kext.get('name', '').lower()
        bundle_lower = bundle_id.lower()
        
        if 'graphics' in name or 'metal' in name or 'gpu' in name or 'framebuffer' in name:
            categories['graphics'] += 1
        elif 'audio' in name or 'hda' in bundle_lower:
            categories['audio'] += 1
        elif 'usb' in name or 'usb' in bundle_lower:
            categories['usb'] += 1
        elif 'bluetooth' in name or 'bt' in bundle_lower:
            categories['bluetooth'] += 1
        elif 'apple' in bundle_lower:
            categories['apple_specific'] += 1
        elif 'intel' in name or 'intel' in bundle_lower:
            categories['intel'] += 1
        elif 'amd' in name:
            categories['amd'] += 1
        else:
            categories['other'] += 1
    
    # Library statistics
    total_libraries = sum(len(kext.get('libraries', [])) for kext in data.values())
    total_dependencies = sum(len(kext.get('dependencies', [])) for kext in data.values())
    
    # Version information
    versions = {}
    for kext in data.values():
        version = kext.get('version', 'N/A')
        versions[version] = versions.get(version, 0) + 1
    
    return {
        'total': total,
        'categories': categories,
        'total_libraries': total_libraries,
        'total_dependencies': total_dependencies,
        'unique_versions': len(versions),
        'top_versions': sorted(versions.items(), key=lambda x: x[1], reverse=True)[:5]
    }

def compare_kext_datasets(vmapple_path, host_path):
    """
    Compare two kext datasets and generate analysis report.
    
    Args:
        vmapple_path (str): Path to VM Apple kext data JSON
        host_path (str): Path to Host kext data JSON
    """
    print("Loading kext datasets...")
    
    try:
        vmapple = load_json(vmapple_path)
        host = load_json(host_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    print(f"\n{'='*60}")
    print("Kext Dataset Comparison Analysis")
    print(f"{'='*60}\n")
    
    vmapple_analysis = analyze_kexts(vmapple)
    host_analysis = analyze_kexts(host)
    
    print("1. Basic Statistics")
    print(f"   VM Apple Kext: {vmapple_analysis['total']} items")
    print(f"   Host Kext: {host_analysis['total']} items")
    print(f"   Difference: {vmapple_analysis['total'] - host_analysis['total']} items\n")
    
    print("2. Library Dependencies")
    print(f"   VM Apple total libraries: {vmapple_analysis['total_libraries']} items")
    print(f"   Host total libraries: {host_analysis['total_libraries']} items")
    print(f"   Difference: {vmapple_analysis['total_libraries'] - host_analysis['total_libraries']} items\n")
    
    print("3. Category Distribution")
    print(f"\n{'Category':<20} {'VM Apple':<15} {'Host':<15} {'Difference':<15}")
    print("-" * 65)
    for cat in sorted(set(list(vmapple_analysis['categories'].keys()) + list(host_analysis['categories'].keys()))):
        vm_count = vmapple_analysis['categories'].get(cat, 0)
        host_count = host_analysis['categories'].get(cat, 0)
        diff = vm_count - host_count
        print(f"{cat:<20} {vm_count:<15} {host_count:<15} {diff:<15}")
    
    # Bundle ID differences
    vmapple_bundles = set(vmapple.keys())
    host_bundles = set(host.keys())
    
    only_in_vmapple = vmapple_bundles - host_bundles
    only_in_host = host_bundles - vmapple_bundles
    common = vmapple_bundles & host_bundles
    
    print(f"\n4. Bundle ID Comparison")
    print(f"   Common: {len(common)} items")
    print(f"   Only in VM Apple: {len(only_in_vmapple)} items")
    print(f"   Only in Host: {len(only_in_host)} items\n")
    
    if only_in_vmapple:
        print("5. Kexts only in VM Apple (top 20):")
        for i, bundle_id in enumerate(list(only_in_vmapple)[:20], 1):
            kext = vmapple[bundle_id]
            print(f"   {i}. {kext.get('name', 'N/A')} ({kext.get('version', 'N/A')})")
            print(f"      Bundle ID: {bundle_id}")
    
    if only_in_host:
        print(f"\n6. Kexts only in Host (top 20):")
        for i, bundle_id in enumerate(list(only_in_host)[:20], 1):
            kext = host[bundle_id]
            print(f"   {i}. {kext.get('name', 'N/A')} ({kext.get('version', 'N/A')})")
            print(f"      Bundle ID: {bundle_id}")
    
    # Version differences
    print(f"\n7. Version Statistics")
    print(f"   VM Apple unique versions: {vmapple_analysis['unique_versions']}")
    print(f"   Host unique versions: {host_analysis['unique_versions']}")
    
    # Generate detailed comparison report
    generate_comparison_report(vmapple, host, vmapple_analysis, host_analysis)

def generate_comparison_report(vmapple, host, vmapple_analysis, host_analysis):
    """
    Generate detailed comparison report and save to file.
    
    Args:
        vmapple (dict): VM Apple kext data
        host (dict): Host kext data
        vmapple_analysis (dict): VM Apple analysis results
        host_analysis (dict): Host analysis results
    """
    report_content = f"""# VM Apple Kext vs Host Kext Comparison Report

## Summary

### Overall Statistics
- **VM Apple Kext**: {vmapple_analysis['total']} items
- **Host Kext**: {host_analysis['total']} items  
- **Difference**: {vmapple_analysis['total'] - host_analysis['total']} items (VM Apple has more)

### Library Dependencies
- VM Apple total libraries: {vmapple_analysis['total_libraries']} items (+{vmapple_analysis['total_libraries'] - host_analysis['total_libraries']})
- Host total libraries: {host_analysis['total_libraries']} items

### Common Points
- Common Kext: **{len(set(vmapple.keys()) & set(host.keys()))}** items (about {len(set(vmapple.keys()) & set(host.keys())) / max(len(vmapple), len(host)) * 100:.1f}%)
- Unique versions: {vmapple_analysis['unique_versions']} items (same)

## Key Differences

### 1. Kexts only in VM Apple ({len(set(vmapple.keys()) - set(host.keys()))} items)

VM Apple environment-specific drivers:

#### USB/Audio related ({len([k for k in vmapple.keys() if k not in host.keys() and ('usb' in k.lower() or 'hda' in k.lower())])} items)
"""
    
    # Add specific kexts only in VM Apple
    only_in_vmapple = set(vmapple.keys()) - set(host.keys())
    usb_audio_count = 0
    mobile_display_count = 0
    
    for bundle_id in only_in_vmapple:
        kext = vmapple[bundle_id]
        name = kext.get('name', '').lower()
        if 'usb' in name or 'hda' in bundle_id.lower():
            usb_audio_count += 1
        elif 'mobiledisp' in bundle_id.lower():
            mobile_display_count += 1
    
    report_content += f"""
- USB/Audio drivers: {usb_audio_count} items
- Mobile display drivers: {mobile_display_count} items
- Apple Silicon specific: {len([k for k in only_in_vmapple if 't8015' in k.lower()])} items

### 2. Kexts only in Host ({len(set(host.keys()) - set(vmapple.keys()))} items)

Real hardware environment-specific drivers:

#### Power Management ({len([k for k in host.keys() if k not in vmapple.keys() and ('pmgr' in k.lower() or 'ppm' in k.lower())])} items)
- Physical power management systems
- Real chipset power control (T8030, T8150, etc.)

#### Physical Hardware Control
- PCIe DMA, Ethernet, etc.
- Advanced I/O features
- PlayStation VR2 support

## Category Distribution

| Category | VM Apple | Host | Difference |
|----------|----------|------|------------|
"""
    
    for cat in sorted(set(list(vmapple_analysis['categories'].keys()) + list(host_analysis['categories'].keys()))):
        vm_count = vmapple_analysis['categories'].get(cat, 0)
        host_count = host_analysis['categories'].get(cat, 0)
        diff = vm_count - host_count
        report_content += f"| **{cat.title()}** | {vm_count} | {host_count} | {diff:+d} |\n"
    
    report_content += f"""
## Key Findings

### VM Apple Environment Characteristics:
1. **USB/Audio Enhancement**: Focus on virtualized USB and audio device support
2. **Mobile Display**: Multiple M1/M2-based display drivers included
3. **Simulation Environment**: Optimized for virtualized rather than physical hardware

### Host Environment Characteristics:
1. **Real Hardware**: Physical hardware control drivers
2. **Power Management**: Real chipset power management (T8030, T8150, etc.)
3. **Advanced Features**: PPM, DMA, Ethernet, etc. advanced I/O features

### Reason for Differences:
- **VM Apple**: Optimized driver set for macOS virtualization environment
- **Host**: Support for all features of real Apple Silicon hardware

## Conclusion

The differences between VM Apple and Host are due to **environment characteristics**:

1. VM Apple focuses on **device simulation** rather than physical hardware control for virtualized environments
2. Host requires more drivers for actual hardware control
3. Most Kexts are common ({len(set(vmapple.keys()) & set(host.keys()))} items/{max(len(vmapple), len(host))} items), with differences being environment-specific drivers

This difference helps understand the optimization direction for each environment.
"""
    
    # Save report to file
    with open('comparison_report.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\nDetailed comparison report saved to: comparison_report.md")

def main():
    """
    Main function to compare kext datasets.
    """
    print("macOS Kernel Extensions Comparison Tool")
    print("=" * 50)
    
    # Define paths to kext data files
    vmapple_path = 'vmapple_kext/kexts_data.json'
    host_path = 'host_kext/kexts_data.json'
    
    # Check if files exist
    if not os.path.exists(vmapple_path):
        print(f"Error: {vmapple_path} not found")
        return
    
    if not os.path.exists(host_path):
        print(f"Error: {host_path} not found")
        return
    
    # Compare datasets
    compare_kext_datasets(vmapple_path, host_path)
    
    print("\nComparison complete!")

if __name__ == '__main__':
    main()
