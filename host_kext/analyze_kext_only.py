#!/usr/bin/env python3
"""
macOS Extensions만 분석하는 스크립트
"""

import plistlib
import os
import json
from pathlib import Path
from collections import defaultdict
import xml.etree.ElementTree as ET

def parse_plist_file(plist_path):
    """Plist 파일을 파싱하고 주요 정보를 추출"""
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
        
        # Dependencies 추출
        os_bundle_requirements = data.get('OSBundleRequirements', {})
        dependencies = []
        if isinstance(os_bundle_requirements, dict):
            dependencies = list(os_bundle_requirements.keys())
        elif isinstance(os_bundle_requirements, list):
            dependencies = os_bundle_requirements
            
        result['dependencies'] = dependencies
        
        # OSBundleLibraries
        os_bundle_libraries = data.get('OSBundleLibraries', {})
        libraries = []
        if isinstance(os_bundle_libraries, dict):
            libraries = list(os_bundle_libraries.keys())
        elif isinstance(os_bundle_libraries, list):
            libraries = os_bundle_libraries
            
        result['libraries'] = libraries
        
        # IOKit Personality 또는 다른 클래스들
        iokit_personalities = data.get('IOKitPersonalities', {})
        iokit_services = []
        if isinstance(iokit_personalities, dict):
            for key, value in iokit_personalities.items():
                if 'IOClass' in value:
                    iokit_services.append(value.get('IOClass'))
        result['iokit_classes'] = list(set(iokit_services))
        
        # Provider 수 (IOService 등)
        result['provides'] = data.get('IOProviderClass', [])
        if not isinstance(result['provides'], list):
            result['provides'] = [result['provides']] if result['provides'] else []
        
        return result
    except Exception as e:
        print(f"Error parsing {plist_path}: {e}")
        return None

def scan_kexts_only():
    """Extensions 디렉토리만 스캔"""
    extensions_dir = '/System/Library/Extensions'
    kexts = {}
    
    print(f"Scanning {extensions_dir}...")
    
    # Info.plist 파일 찾기
    plist_files = []
    for root, dirs, files in os.walk(extensions_dir):
        if 'Info.plist' in files:
            plist_path = os.path.join(root, 'Info.plist')
            plist_files.append(plist_path)
    
    print(f"Found {len(plist_files)} Info.plist files")
    
    # 각 plist 파싱
    for plist_path in plist_files:
        data = parse_plist_file(plist_path)
        if data:
            bundle_id = data.get('bundle_id')
            if bundle_id:
                kexts[bundle_id] = data
    
    print(f"Successfully parsed {len(kexts)} kexts")
    return kexts

def create_graphml(kexts):
    """GraphML 형식으로 변환"""
    root = ET.Element('graphml', 
                      xmlns='http://graphml.graphdrawing.org/xmlns',
                      xmlns_xsi='http://www.w3.org/2001/XMLSchema-instance',
                      xmlns_y='http://www.yworks.com/xml/graphml',
                      xsi_schemaLocation='http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd')
    
    # 키 정의
    key_nodes = ET.SubElement(root, 'key', id='d0', **{'for': 'node', 'attr.name': 'label', 'attr.type': 'string'})
    key_edges = ET.SubElement(root, 'key', id='d1', **{'for': 'edge', 'attr.name': 'label', 'attr.type': 'string'})
    
    # 그래프 요소
    graph = ET.SubElement(root, 'graph', id='kext_dependencies', edgedefault='directed')
    
    # 노드 추가 (kext들)
    for bundle_id, kext_data in kexts.items():
        node = ET.SubElement(graph, 'node', id=bundle_id.replace('.', '_'))
        data_label = ET.SubElement(node, 'data', key='d0')
        name = kext_data.get('kext_name', kext_data.get('name', 'Unknown'))
        version = kext_data.get('version', '')
        label = f"{name}\n{version}\n[kext]"
        data_label.text = label
    
    # 엣지 추가 (의존관계)
    edges_added = set()
    for bundle_id, kext_data in kexts.items():
        # dependencies에서
        for dep in kext_data.get('dependencies', []):
            if dep in kexts and (bundle_id, dep) not in edges_added:
                edge = ET.SubElement(graph, 'edge', 
                                    source=bundle_id.replace('.', '_'),
                                    target=dep.replace('.', '_'))
                data_label = ET.SubElement(edge, 'data', key='d1')
                data_label.text = 'depends'
                edges_added.add((bundle_id, dep))
        
        # libraries에서
        for lib in kext_data.get('libraries', []):
            if lib in kexts and (bundle_id, lib) not in edges_added:
                edge = ET.SubElement(graph, 'edge',
                                    source=bundle_id.replace('.', '_'),
                                    target=lib.replace('.', '_'))
                data_label = ET.SubElement(edge, 'data', key='d1')
                data_label.text = 'uses library'
                edges_added.add((bundle_id, lib))
    
    return root

def save_files(kexts, graphml_root):
    """결과를 파일로 저장"""
    # JSON 데이터 저장
    with open('kext_only/kexts_data.json', 'w') as f:
        json.dump(kexts, f, indent=2)
    
    # GraphML 저장
    tree = ET.ElementTree(graphml_root)
    ET.indent(tree, space='  ')
    with open('kext_only/kexts_graph.graphml', 'wb') as f:
        tree.write(f, encoding='utf-8', xml_declaration=True)
    
    print("Files saved:")
    print("  - kext_only/kexts_data.json")
    print("  - kext_only/kexts_graph.graphml")

def main():
    kexts = scan_kexts_only()
    graphml_root = create_graphml(kexts)
    save_files(kexts, graphml_root)
    
    # 통계 출력
    print(f"\nTotal kexts: {len(kexts)}")
    
    # 의존관계 통계
    total_deps = sum(len(k.get('dependencies', [])) for k in kexts.values())
    total_libs = sum(len(k.get('libraries', [])) for k in kexts.values())
    print(f"Total dependencies: {total_deps}")
    print(f"Total libraries: {total_libs}")

if __name__ == '__main__':
    main()
