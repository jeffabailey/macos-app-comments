#!/usr/bin/env python3
"""
Generate descriptions for all apps in /Applications using Goose CLI.
"""
import os
import json
import subprocess
import sys
import plistlib
from jinja2 import Template

BATCH_SIZE = 10


def get_applications():
    """Get all .app bundles from /Applications with their details."""
    apps = []
    for f in os.listdir("/Applications"):
        app_path = os.path.join("/Applications", f)
        if f.endswith('.app') and os.path.isdir(app_path):
            app_name = f.replace('.app', '')
            app_details = get_app_details(app_path, app_name)
            apps.append(app_details)
    return sorted(apps, key=lambda x: x['name'])


def get_app_details(app_path, app_name):
    """Extract details from app bundle including Info.plist."""
    details = {
        'name': app_name,
        'path': app_path,
        'description': '',
        'version': '',
        'bundle_identifier': ''
    }

    # Try to read Info.plist for app metadata
    info_plist_path = os.path.join(app_path, 'Contents', 'Info.plist')
    if os.path.exists(info_plist_path):
        try:
            with open(info_plist_path, 'rb') as f:
                plist_data = plistlib.load(f)

            # Extract common metadata fields
            if 'CFBundleDescription' in plist_data:
                details['description'] = plist_data['CFBundleDescription']
            elif 'CFBundleGetInfoString' in plist_data:
                details['description'] = plist_data['CFBundleGetInfoString']

            if 'CFBundleShortVersionString' in plist_data:
                details['version'] = plist_data['CFBundleShortVersionString']

            if 'CFBundleIdentifier' in plist_data:
                details['bundle_identifier'] = plist_data['CFBundleIdentifier']

        except Exception:
            # Silently continue if we can't read the plist
            pass

    return details


def create_prompt_file(apps):
    """Create a comprehensive prompt file for Goose CLI using Jinja2 templates."""
    # Read the template file
    template_path = "prompt_template.j2"
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()

    # Create Jinja2 template
    template = Template(template_content)

    # Render the template with the apps data
    prompt_content = template.render(apps=apps)

    with open("applications_detail_prompt.txt", 'w', encoding='utf-8') as f:
        f.write(prompt_content)

    return "applications_detail_prompt.txt"


def run_goose_cli(prompt_file, debug_mode=False):
    """Run Goose CLI with the prompt file."""
    try:
        # Read the prompt file contents
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_content = f.read()

        result = subprocess.run(
            ['goose', 'run', '-t', prompt_content],
            capture_output=True, text=True, timeout=120
        )

        if debug_mode:
            print("\n--- RAW GOOSE OUTPUT ---\n")
            print(result.stdout)
            print("\n--- END RAW GOOSE OUTPUT ---\n")

        if result.returncode == 0:
            return result.stdout
        else:
            print(f"Goose CLI error: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error running Goose CLI: {e}")
        return None


def strip_ansi(text):
    """Remove ANSI escape sequences from text."""
    import re
    ansi_escape = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')
    return ansi_escape.sub('', text)


def parse_goose_response(response):
    """Parse the JSON response from Goose CLI, handling code blocks, repeated keys, and nested JSON."""
    import re

    response = strip_ansi(response)

    # 1. Try all code blocks (with or without json label), allow for whitespace/newlines after opening and before closing backticks
    code_blocks = re.findall(
        r"```(?:json)?[ \t]*\n([\s\S]*?)\n[ \t]*```",
        response, re.IGNORECASE
    )
    for block in reversed(code_blocks):
        block = block.strip()
        try:
            result = json.loads(block)
            return result
        except Exception:
            pass
        # Fallback: extract key-value pairs (flat only)
        obj = {}
        key_value_pattern = re.compile(r'"([^\"]+)":\s*"([^\"]*)",?')
        for line in block.splitlines():
            line = line.strip()
            m = key_value_pattern.match(line)
            if m:
                key, value = m.group(1), m.group(2)
                obj[key] = value
        if obj:
            return obj

    # 2. Look for JSON objects that start with { and end with } in the response
    json_pattern = r'(\{[\s\S]*\})'
    matches = re.findall(json_pattern, response, re.DOTALL)
    for match in reversed(matches):
        match = match.strip()
        try:
            parsed = json.loads(match)
            if isinstance(parsed, dict) and len(parsed) > 0:
                if all(isinstance(v, str) for v in parsed.values()):
                    return parsed
        except Exception:
            continue

    # 3. Fallback: extract from first { to last } and try to parse
    first = response.find('{')
    last = response.rfind('}')
    if first != -1 and last != -1 and last > first:
        candidate = response[first:last + 1].strip()
        try:
            result = json.loads(candidate)
            return result
        except Exception:
            # Fallback: extract key-value pairs (flat only)
            obj = {}
            key_value_pattern = re.compile(r'"([^\"]+)":\s*"([^\"]*)",?')
            for line in candidate.splitlines():
                line = line.strip()
                m = key_value_pattern.match(line)
                if m:
                    key, value = m.group(1), m.group(2)
                    obj[key] = value
            if obj:
                return obj

    return {}


def main():
    # Parse command line arguments
    debug_mode = False
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h']:
            print("Usage: python app_metadata_builder.py [--debug|-d]")
            print("Requirements: brew install goose")
            print("\nOptions:")
            print("  --debug, -d    Enable debug output")
            return
        elif sys.argv[1] in ['--debug', '-d']:
            debug_mode = True

    apps = get_applications()
    if not apps:
        print("No applications found in /Applications.")
        return

    print(
        "Found {} apps. Creating prompt file(s) and generating descriptions in "
        "batches of {}...".format(len(apps), BATCH_SIZE)
    )
    all_descriptions = {}
    num_batches = (len(apps) + BATCH_SIZE - 1) // BATCH_SIZE
    for i in range(0, len(apps), BATCH_SIZE):
        batch = apps[i:i + BATCH_SIZE]
        print(
            "Processing batch {} of {} ({} apps)...".format(
                i // BATCH_SIZE + 1, num_batches, len(batch)
            )
        )
        prompt_file = create_prompt_file(batch)
        response = run_goose_cli(prompt_file, debug_mode)
        if response is None:
            print("  ❌ No response from Goose CLI")
            continue
        if debug_mode:
            print(f"  Response length: {len(response)}")
        descriptions = parse_goose_response(response)
        print(f"  Parsed {len(descriptions)} descriptions from batch")
        if descriptions:
            if debug_mode:
                print(
                    f"  Sample: {list(descriptions.keys())[:3]}"
                )
        else:
            print("  ❌ No descriptions parsed from response")
        all_descriptions.update(descriptions)
        if debug_mode:
            print(f"  Total descriptions so far: {len(all_descriptions)}")

    with open("applications.json", 'w', encoding='utf-8') as f:
        json.dump(
            all_descriptions, f, indent=2, ensure_ascii=False
        )
    print(
        "\nSaved {} descriptions to applications.json".format(
            len(all_descriptions)
        )
    )


if __name__ == "__main__":
    main()

    # 1. Try all code blocks (with or without json label), allow for whitespace/newlines after opening and before closing backticks
