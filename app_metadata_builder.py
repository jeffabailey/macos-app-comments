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
        'bundle_identifier': '',
        'created': '',
        'modified': '',
        'copyright': '',
        'CFBundleDescription': ''
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
                details['CFBundleDescription'] = plist_data['CFBundleDescription']
            elif 'CFBundleGetInfoString' in plist_data:
                details['description'] = plist_data['CFBundleGetInfoString']

            if 'CFBundleShortVersionString' in plist_data:
                details['version'] = plist_data['CFBundleShortVersionString']

            if 'CFBundleIdentifier' in plist_data:
                details['bundle_identifier'] = plist_data['CFBundleIdentifier']

            # Extract additional metadata fields
            if 'CFBundleGetInfoString' in plist_data:
                details['copyright'] = plist_data['CFBundleGetInfoString']

        except Exception:
            # Silently continue if we can't read the plist
            pass

    # Get file creation and modification times
    try:
        stat_info = os.stat(app_path)
        details['created'] = str(stat_info.st_ctime)
        details['modified'] = str(stat_info.st_mtime)
    except Exception:
        # Silently continue if we can't get file stats
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


def _try_parse_json(text):
    """Try to parse JSON from text."""
    try:
        return json.loads(text)
    except Exception:
        return None


def _extract_key_value_pairs(text):
    """Extract key-value pairs from text using regex."""
    import re
    obj = {}
    key_value_pattern = re.compile(r'"([^\"]+)":\s*"([^\"]*)",?')
    for line in text.splitlines():
        line = line.strip()
        m = key_value_pattern.match(line)
        if m:
            key, value = m.group(1), m.group(2)
            obj[key] = value
    return obj


def _try_parse_code_blocks(response):
    """Try to parse JSON from code blocks."""
    import re
    code_blocks = re.findall(
        r"```(?:json)?[ \t]*\n([\s\S]*?)\n[ \t]*```",
        response, re.IGNORECASE
    )
    for block in reversed(code_blocks):
        block = block.strip()
        result = _try_parse_json(block)
        if result:
            return result
        obj = _extract_key_value_pairs(block)
        if obj:
            return obj
    return None


def _is_valid_string_dict(parsed):
    """Check if parsed result is a valid dictionary with string values."""
    return (
        parsed and isinstance(parsed, dict) and len(parsed) > 0
        and all(isinstance(v, str) for v in parsed.values())
    )


def _try_parse_json_objects(response):
    """Try to parse JSON objects from response."""
    import re
    json_pattern = r'(\{[\s\S]*\})'
    matches = re.findall(json_pattern, response, re.DOTALL)
    for match in reversed(matches):
        match = match.strip()
        parsed = _try_parse_json(match)
        if _is_valid_string_dict(parsed):
            return parsed
    return None


def _has_valid_json_bounds(response):
    """Check if response has valid JSON bounds."""
    first = response.find('{')
    last = response.rfind('}')
    return first != -1 and last != -1 and last > first


def _try_parse_fallback(response):
    """Try to parse JSON from first { to last }."""
    if not _has_valid_json_bounds(response):
        return None

    first = response.find('{')
    last = response.rfind('}')
    candidate = response[first:last + 1].strip()
    result = _try_parse_json(candidate)
    if result:
        return result
    obj = _extract_key_value_pairs(candidate)
    if obj:
        return obj
    return None


def parse_goose_response(response):
    """Parse the JSON response from Goose CLI, handling code blocks, repeated keys, and nested JSON."""
    response = strip_ansi(response)

    result = _try_parse_code_blocks(response)
    if result:
        return result

    result = _try_parse_json_objects(response)
    if result:
        return result

    result = _try_parse_fallback(response)
    if result:
        return result

    return {}


def _parse_arguments():
    """Parse command line arguments."""
    debug_mode = False
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h']:
            print("Usage: python app_metadata_builder.py [--debug|-d]")
            print("Requirements: brew install goose")
            print("\nOptions:")
            print("  --debug, -d    Enable debug output")
            return None
        elif sys.argv[1] in ['--debug', '-d']:
            debug_mode = True
    return debug_mode


def _process_batch(batch, batch_num, num_batches, debug_mode):
    """Process a single batch of applications."""
    print(f"Processing batch {batch_num} of {num_batches} ({len(batch)} apps)...")

    prompt_file = create_prompt_file(batch)
    response = run_goose_cli(prompt_file, debug_mode)

    if response is None:
        print("  ❌ No response from Goose CLI")
        return {}

    if debug_mode:
        print(f"  Response length: {len(response)}")

    descriptions = parse_goose_response(response)
    print(f"  Parsed {len(descriptions)} descriptions from batch")

    if descriptions and debug_mode:
        print(f"  Sample: {list(descriptions.keys())[:3]}")
    elif not descriptions:
        print("  ❌ No descriptions parsed from response")

    # Merge app metadata with descriptions
    merged_results = {}
    for app in batch:
        app_name = app['name']
        if app_name in descriptions:
            # Merge metadata with description
            merged_results[app_name] = {
                'description': descriptions[app_name],
                'version': app['version'],
                'created': app['created'],
                'modified': app['modified'],
                'copyright': app['copyright'],
                'CFBundleDescription': app['CFBundleDescription'],
                'bundle_identifier': app['bundle_identifier'],
                'path': app['path']
            }
        else:
            # Include metadata even if no description was generated
            merged_results[app_name] = {
                'description': '',
                'version': app['version'],
                'created': app['created'],
                'modified': app['modified'],
                'copyright': app['copyright'],
                'CFBundleDescription': app['CFBundleDescription'],
                'bundle_identifier': app['bundle_identifier'],
                'path': app['path']
            }

    return merged_results


def _save_results(all_descriptions):
    """Save results to applications.json."""
    with open("applications.json", 'w', encoding='utf-8') as f:
        json.dump(all_descriptions, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(all_descriptions)} applications with metadata to applications.json")


def main():
    debug_mode = _parse_arguments()
    if debug_mode is None:
        return

    apps = get_applications()
    if not apps:
        print("No applications found in /Applications.")
        return

    print(f"Found {len(apps)} apps. Creating prompt file(s) and generating descriptions in batches of {BATCH_SIZE}...")

    all_applications = {}
    num_batches = (len(apps) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(apps), BATCH_SIZE):
        batch = apps[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        batch_results = _process_batch(batch, batch_num, num_batches, debug_mode)
        all_applications.update(batch_results)

        if debug_mode:
            print(f"  Total applications so far: {len(all_applications)}")

    _save_results(all_applications)


if __name__ == "__main__":
    main()
