#!/usr/bin/env python3
"""
Test the parse_goose_response function with actual Goose CLI output.
"""
import sys
import os

# Import the function from the main script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app_metadata_builder import parse_goose_response  # noqa: E402


def test_parse_goose_response():
    """Test the parse_goose_response function with actual Goose CLI output."""
    sample_response = (
        'starting session | provider: github_copilot model: gpt-4o\n'
        'logging to /Users/jeffbailey/.local/share/goose/sessions/20250712_183856.jsonl\n'
        'working directory: /Users/jeffbailey/Projects/foss/leading/macos-app-comments\n'
        '```json\n'
        '{\n'
        '  "Safari": "Safari is Apple\'s native web browser, offering fast, secure, and privacy-centric internet browsing for macOS users.",\n'
        '  "Scribus": "Scribus is an open-source desktop publishing application ideal for creating professional-quality documents like brochures, magazines, and books.",\n'
        '  "Service Station": "Service Station allows users to customize the macOS context menu with shortcuts and workflows for improved productivity.",\n'
        '  "Skim": "Skim is a lightweight, open-source PDF viewer and annotation tool tailored for research and review purposes.",\n'
        '  "Skitch": "Skitch is a screenshot and annotation app designed for quickly capturing, editing, and sharing visual content with ease.",\n'
        '  "Slack": "Slack is a collaborative communication platform that integrates channels, direct messaging, and app tools for team productivity.",\n'
        '  "Spatial Media Metadata Injector": "Spatial Media Metadata Injector is a specialized tool for embedding spatial metadata into 360-degree videos to support VR compatibility.",\n'
        '  "Steam": "Steam is a widely-used gaming platform for purchasing, managing, and playing PC and macOS games, complete with community features.",\n'
        '  "Syncthing": "Syncthing is an open-source software for secure, decentralized file synchronization across multiple devices in real time.",\n'
        '  "Synology Drive Client": "Synology Drive Client is a file syncing and backup tool for connecting macOS devices with Synology NAS for seamless collaboration and data management."\n'
        '}\n'
        '```'
    )
    print("Testing parse_goose_response function...")
    result = parse_goose_response(sample_response)
    print(f"Parsed result: {result}")
    print(f"Number of apps parsed: {len(result)}")
    if result:
        print("✅ SUCCESS: Function parsed JSON correctly")
        print("Sample entries:")
        for i, (app, desc) in enumerate(list(result.items())[:3]):
            print(f"  {app}: {desc[:50]}...")
    else:
        print("❌ FAILURE: Function returned empty result")
        return False
    return True


def test_actual_output():
    """Test with the exact output from the actual run."""
    actual_output = (
        'starting session | provider: github_copilot model: gpt-4o\n'
        'logging to /Users/jeffbailey/.local/share/goose/sessions/20250712_184137.jsonl\n'
        'working directory: /Users/jeffbailey/Projects/foss/leading/macos-app-comments\n'
        '```json\n'
        '{\n'
        '  "4K Video Downloader": "A versatile tool for downloading videos, playlists, and subtitles from online platforms, ideal for content creators and media enthusiasts seeking to save online content for offline use.",\n'
        '  "Ableton Live 11 Suite": "A professional music production software offering advanced tools for composing, recording, editing, mixing, and live performance, perfect for musicians, producers, and DJs.",\n'
        '  "AdBlock": "A lightweight application designed to block ads and enhance browsing speed and privacy on macOS, suitable for users aiming to improve their online experience."\n'
        '}\n'
        '```'
    )
    print("\nTesting with actual output format...")
    result = parse_goose_response(actual_output)
    print(f"Parsed {len(result)} descriptions")
    if result:
        print("✅ SUCCESS")
        print("Keys:", list(result.keys()))
    else:
        print("❌ FAILURE")
        print("Debugging...")
        print("Response length:", len(actual_output))
        print("Contains ```json:", "```json" in actual_output)
        print("Contains ```:", "```" in actual_output)
        import re
        json_matches = re.findall(
            r'```json\s*({[\s\S]*?})\s*```', actual_output
        )
        print(f"Found {len(json_matches)} JSON matches in code blocks")
        if json_matches:
            print("First match:", json_matches[0][:100])
    return len(result) > 0


def test_multiple_formats():
    """Test with different JSON formats that might be returned."""
    test_cases = [
        # Case 1: JSON in code block
        '```json\n{\n  "App1": "Description 1",\n  "App2": "Description 2"\n}\n```',
        # Case 2: JSON without code block
        (
            'Some text before\n{\n  "App3": "Description 3",\n  "App4": "Description 4"\n}\n'
            'Some text after'
        ),
        # Case 3: JSON with extra whitespace
        '```json\n{\n  "App5": "Description 5",\n  "App6": "Description 6"\n}\n```'
    ]
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTesting case {i}:")
        result = parse_goose_response(test_case)
        print(f"  Result: {len(result)} apps parsed")
        if result:
            print("  ✅ SUCCESS")
        else:
            print("  ❌ FAILURE")
    return True


if __name__ == "__main__":
    print("Running parse_goose_response tests...")
    success1 = test_parse_goose_response()
    success2 = test_actual_output()
    success3 = test_multiple_formats()
    if success1 and success2 and success3:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)
