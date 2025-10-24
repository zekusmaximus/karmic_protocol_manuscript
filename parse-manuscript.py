#!/usr/bin/env python3
"""
Parse full_manuscript.md and generate individual scene files with YAML headers.
Run from repo root: python3 parse_manuscript.py
"""

import re
import os
from pathlib import Path

def parse_manuscript(manuscript_path):
    """
    Parse the manuscript and extract scenes.
    Returns a list of dicts with scene metadata and content.
    """
    with open(manuscript_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    scenes = []
    
    # Pattern to match chapter headers and scenes
    # Matches: === CHAPTER X === followed by [SCENE: CHX_SXX | POV: Y | Location: Z]
    chapter_pattern = r'^=== CHAPTER (\d+) ===\s*$'
    scene_pattern = r'^\[SCENE: CH(\d+)_S(\d+) \| POV: (.+?) \| Location: (.+?)\]$'
    
    lines = content.split('\n')
    current_chapter = None
    current_scene_num = None
    current_pov = None
    current_location = None
    scene_content = []
    scene_start_line = 0
    
    for i, line in enumerate(lines):
        chapter_match = re.match(chapter_pattern, line)
        scene_match = re.match(scene_pattern, line)
        
        # If we hit a new chapter marker
        if chapter_match:
            # Save previous scene if exists
            if current_pov and scene_content:
                scenes.append({
                    'chapter': current_chapter,
                    'scene': current_scene_num,
                    'pov': current_pov,
                    'location': current_location,
                    'content': '\n'.join(scene_content).strip(),
                    'start_line': scene_start_line
                })
                scene_content = []
            
            current_chapter = int(chapter_match.group(1))
            current_scene_num = None
            current_pov = None
            current_location = None
        
        # If we hit a scene marker
        elif scene_match:
            # Save previous scene if exists
            if current_pov and scene_content:
                scenes.append({
                    'chapter': current_chapter,
                    'scene': current_scene_num,
                    'pov': current_pov,
                    'location': current_location,
                    'content': '\n'.join(scene_content).strip(),
                    'start_line': scene_start_line
                })
                scene_content = []
            
            current_chapter = int(scene_match.group(1))
            current_scene_num = int(scene_match.group(2))
            current_pov = scene_match.group(3).strip()
            current_location = scene_match.group(4).strip()
            scene_start_line = i
        
        # Accumulate scene content
        elif current_pov:
            scene_content.append(line)
    
    # Don't forget the last scene
    if current_pov and scene_content:
        scenes.append({
            'chapter': current_chapter,
            'scene': current_scene_num,
            'pov': current_pov,
            'location': current_location,
            'content': '\n'.join(scene_content).strip(),
            'start_line': scene_start_line
        })
    
    return scenes


def generate_yaml_header(scene):
    """
    Generate a YAML header for a scene.
    Auto-populate basic fields; leave others for manual refinement.
    """
    wordcount = len(scene['content'].split())
    
    # Simple tension level heuristic based on content keywords
    tension_keywords = ['raid', 'arrest', 'attack', 'fight', 'chase', 'danger', 'threat', 'crisis', 'emergency']
    tension_level = 3  # default
    content_lower = scene['content'].lower()
    for keyword in tension_keywords:
        if keyword in content_lower:
            tension_level = min(10, tension_level + 2)
    
    # Basic thematic tags from POV and location
    thematic_tags = []
    if 'fiona' in scene['pov'].lower() or 'gile' in scene['pov'].lower():
        thematic_tags.append('law_enforcement')
    if 'tim' in scene['pov'].lower():
        thematic_tags.append('protocol_development')
    if 'georgia' in scene['pov'].lower() or 'sato' in scene['pov'].lower():
        thematic_tags.append('corporate_warfare')
    if 'sherry' in scene['pov'].lower() or 'enlightenment' in content_lower:
        thematic_tags.append('awakening')
    if 'raid' in content_lower:
        thematic_tags.append('government_action')
    if 'bud' in scene['pov'].lower():
        thematic_tags.append('moral_conflict')
    
    # Extract basic plot function from content
    plot_function = "auto_generated"
    if 'raid' in content_lower:
        plot_function = "Raid sequence / government action"
    elif 'meeting' in content_lower or 'discuss' in content_lower:
        plot_function = "Strategic discussion / planning"
    elif 'enlightenment' in content_lower or 'protocol' in content_lower and 'complete' in content_lower:
        plot_function = "Protocol success / character achievement"
    elif 'news' in content_lower or 'broadcast' in content_lower:
        plot_function = "Public revelation / media coverage"
    
    yaml_header = f"""---
chapter: {scene['chapter']}
scene: {scene['scene']}
pov: "{scene['pov']}"
location: "{scene['location']}"
wordcount: {wordcount}
status: "draft"
tags: [auto_generated]
plot_function: "{plot_function}"
thematic_tags: {thematic_tags if thematic_tags else ['[pending]']}
act: "unknown"
revision_notes: "auto_generated - review for accuracy"
links: []
---
"""
    return yaml_header


def create_scene_files(scenes, output_dir='scenes'):
    """
    Create individual scene .md files with YAML headers.
    """
    Path(output_dir).mkdir(exist_ok=True)

    chapter_scene_counts = {}

    for scene in scenes:
        filename = f"ch{scene['chapter']:02d}_s{scene['scene']:02d}.md"
        filepath = Path(output_dir) / filename

        yaml_header = generate_yaml_header(scene)
        full_content = yaml_header + '\n' + scene['content'] + '\n'

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)

        wordcount = len(scene['content'].split())
        print(f"[OK] Created {filename} ({wordcount} words)")
        
        # Track chapter/scene counts
        ch = scene['chapter']
        if ch not in chapter_scene_counts:
            chapter_scene_counts[ch] = 0
        chapter_scene_counts[ch] += 1
    
    return chapter_scene_counts


def create_chapter_map(chapter_scene_counts, output_path='chapter_map.md'):
    """
    Create a summary map of chapters and scene counts.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Chapter & Scene Map\n\n")
        f.write("| Chapter | Scene Count | Total Words |\n")
        f.write("|---------|-------------|-------------|\n")
        
        total_scenes = 0
        for ch in sorted(chapter_scene_counts.keys()):
            count = chapter_scene_counts[ch]
            total_scenes += count
            f.write(f"| {ch} | {count} | [pending] |\n")
        
        f.write(f"\n**Total Chapters:** {len(chapter_scene_counts)}\n")
        f.write(f"**Total Scenes:** {total_scenes}\n")
    
    print(f"\n[OK] Created chapter_map.md ({len(chapter_scene_counts)} chapters, {total_scenes} scenes)")


if __name__ == '__main__':
    manuscript_file = 'full_manuscript.md'
    
    if not Path(manuscript_file).exists():
        print(f"Error: {manuscript_file} not found in current directory")
        exit(1)
    
    print("Parsing manuscript...")
    scenes = parse_manuscript(manuscript_file)
    print(f"Found {len(scenes)} scenes\n")
    
    print("Generating scene files...")
    chapter_counts = create_scene_files(scenes)
    
    print("\nGenerating chapter map...")
    create_chapter_map(chapter_counts)
    
    print("\n[DONE] Scene files created in /scenes directory.")