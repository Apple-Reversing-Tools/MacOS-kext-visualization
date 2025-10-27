#!/usr/bin/env python3
"""
macOS Kernel Extensions Analysis Tool
Analyzes plist files from /System/Library/Extensions and generates JSON data and GraphML visualization files.
"""

import plistlib
import os
import json
from pathlib import Path
from collections import defaultdict
import xml.etree.ElementTree as ET

def parse_plist_file(plist_path):
    """
    Parse a plist file and extract key information about the kext.
    
    Args:
        plist_path (str): Path to the Info.plist file
        
    Returns:
        dict: Parsed kext information or None if parsing fails
    """
    try:
        with open(plist_path, 'rb') as f:
            data = plistlib.load(f)
        
        result = {
            'path': str(plist_path),
            'bundle_id': data.get('CFBundleIdentifier', ''),
            'name': data.get('CFBundleName', ''),
            'version': data.get('CFBundleVersion', ''),
            'executable': data.get('CFBundleExecutable', ''),
            'kext_name': data.get('CFBundleIdentifier', '').split('.')[-1],
            'source_type': 'kext'
        }
        
        # Extract dependencies from OSBundleRequirements
        os_bundle_requirements = data.get('OSBundleRequirements', {})
        dependencies = []
        if isinstance(os_bundle_requirements, dict):
            dependencies = list(os_bundle_requirements.keys())
        elif isinstance(os_bundle_requirements, list):
            dependencies = os_bundle_requirements
            
        result['dependencies'] = dependencies
        
        # Extract libraries from OSBundleLibraries
        os_bundle_libraries = data.get('OSBundleLibraries', {})
        libraries = []
        if isinstance(os_bundle_libraries, dict):
            libraries = list(os_bundle_libraries.keys())
        elif isinstance(os_bundle_libraries, list):
            libraries = os_bundle_libraries
            
        result['libraries'] = libraries
        
        # Extract IOKit classes from IOKitPersonalities
        iokit_personalities = data.get('IOKitPersonalities', {})
        iokit_services = []
        if isinstance(iokit_personalities, dict):
            for key, value in iokit_personalities.items():
                if 'IOClass' in value:
                    iokit_services.append(value.get('IOClass'))
        result['iokit_classes'] = list(set(iokit_services))
        
        # Extract provider classes
        result['provides'] = data.get('IOProviderClass', [])
        if not isinstance(result['provides'], list):
            result['provides'] = [result['provides']] if result['provides'] else []
        
        return result
    except Exception as e:
        print(f"Error parsing {plist_path}: {e}")
        return None

def scan_kexts_only():
    """
    Scan only the Extensions directory for kext plist files.
    
    Returns:
        dict: Dictionary of kext data keyed by bundle ID
    """
    extensions_dir = '/System/Library/Extensions'
    kexts = {}
    
    print(f"Scanning {extensions_dir}...")
    
    # Find all Info.plist files
    plist_files = []
    for root, dirs, files in os.walk(extensions_dir):
        if 'Info.plist' in files:
            plist_path = os.path.join(root, 'Info.plist')
            plist_files.append(plist_path)
    
    print(f"Found {len(plist_files)} Info.plist files")
    
    # Parse each plist file
    for plist_path in plist_files:
        data = parse_plist_file(plist_path)
        if data:
            bundle_id = data.get('bundle_id')
            if bundle_id:
                kexts[bundle_id] = data
    
    print(f"Successfully parsed {len(kexts)} kexts")
    return kexts

def create_graphml(kexts):
    """
    Create GraphML format representation of kext dependencies.
    
    Args:
        kexts (dict): Dictionary of kext data
        
    Returns:
        ET.Element: Root element of the GraphML tree
    """
    root = ET.Element('graphml', 
                      xmlns='http://graphml.graphdrawing.org/xmlns',
                      xmlns_xsi='http://www.w3.org/2001/XMLSchema-instance',
                      xmlns_y='http://www.yworks.com/xml/graphml',
                      xsi_schemaLocation='http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd')
    
    # Define keys for node and edge attributes
    key_nodes = ET.SubElement(root, 'key', id='d0', **{'for': 'node', 'attr.name': 'label', 'attr.type': 'string'})
    key_edges = ET.SubElement(root, 'key', id='d1', **{'for': 'edge', 'attr.name': 'label', 'attr.type': 'string'})
    
    # Create graph element
    graph = ET.SubElement(root, 'graph', id='kext_dependencies', edgedefault='directed')
    
    # Add nodes for each kext
    for bundle_id, kext_data in kexts.items():
        node = ET.SubElement(graph, 'node', id=bundle_id.replace('.', '_'))
        data_label = ET.SubElement(node, 'data', key='d0')
        name = kext_data.get('kext_name', kext_data.get('name', 'Unknown'))
        version = kext_data.get('version', '')
        label = f"{name}\n{version}\n[kext]"
        data_label.text = label
    
    # Add edges for dependencies
    edges_added = set()
    for bundle_id, kext_data in kexts.items():
        # Add edges for dependencies
        for dep in kext_data.get('dependencies', []):
            if dep in kexts and (bundle_id, dep) not in edges_added:
                edge = ET.SubElement(graph, 'edge', 
                                    source=bundle_id.replace('.', '_'),
                                    target=dep.replace('.', '_'))
                data_label = ET.SubElement(edge, 'data', key='d1')
                data_label.text = 'depends'
                edges_added.add((bundle_id, dep))
        
        # Add edges for library dependencies
        for lib in kext_data.get('libraries', []):
            if lib in kexts and (bundle_id, lib) not in edges_added:
                edge = ET.SubElement(graph, 'edge',
                                    source=bundle_id.replace('.', '_'),
                                    target=lib.replace('.', '_'))
                data_label = ET.SubElement(edge, 'data', key='d1')
                data_label.text = 'uses library'
                edges_added.add((bundle_id, lib))
    
    return root

def save_files(kexts, graphml_root, output_dir):
    """
    Save kext data and GraphML to files in the specified directory.
    
    Args:
        kexts (dict): Dictionary of kext data
        graphml_root (ET.Element): Root element of GraphML tree
        output_dir (str): Directory to save files to
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Save JSON data
    json_path = os.path.join(output_dir, 'kexts_data.json')
    with open(json_path, 'w') as f:
        json.dump(kexts, f, indent=2)
    
    # Save GraphML
    graphml_path = os.path.join(output_dir, 'kexts_graph.graphml')
    tree = ET.ElementTree(graphml_root)
    ET.indent(tree, space='  ')
    with open(graphml_path, 'wb') as f:
        tree.write(f, encoding='utf-8', xml_declaration=True)
    
    print(f"Files saved:")
    print(f"  - {json_path}")
    print(f"  - {graphml_path}")

def generate_statistics(kexts):
    """
    Generate and print statistics about the kext data.
    
    Args:
        kexts (dict): Dictionary of kext data
    """
    print(f"\nTotal kexts: {len(kexts)}")
    
    # Calculate dependency statistics
    total_deps = sum(len(k.get('dependencies', [])) for k in kexts.values())
    total_libs = sum(len(k.get('libraries', [])) for k in kexts.values())
    print(f"Total dependencies: {total_deps}")
    print(f"Total libraries: {total_libs}")
    
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
    
    for bundle_id, kext in kexts.items():
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
    
    print(f"\nCategory distribution:")
    for category, count in categories.items():
        print(f"  {category}: {count}")

def main():
    """
    Main function to analyze kexts and generate output files.
    """
    print("macOS Kernel Extensions Analysis Tool")
    print("=" * 50)
    
    # Scan for kexts
    kexts = scan_kexts_only()
    
    if not kexts:
        print("No kexts found. Exiting.")
        return
    
    # Create GraphML representation
    graphml_root = create_graphml(kexts)
    
    # Save files to current directory
    save_files(kexts, graphml_root, '.')
    
    # Generate statistics
    generate_statistics(kexts)
    
    print("\nAnalysis complete!")

if __name__ == '__main__':
    main()
