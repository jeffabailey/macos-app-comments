#!/usr/bin/env python3
"""Debug script to test the parsing issue with a single batch."""

from app_metadata_builder import (
    get_applications, create_prompt_file, run_goose_cli, parse_goose_response
)


def main():
    apps = get_applications()[:3]
    print(f'Testing with {len(apps)} apps')

    prompt_file = create_prompt_file(apps)
    response = run_goose_cli(prompt_file, debug_mode=True)  # Enable debug mode

    print(f'Response is None: {response is None}')
    if response:
        print(f'Response length: {len(response)}')
        descriptions = parse_goose_response(response)
        print(f'Parsed {len(descriptions)} descriptions')
        if descriptions:
            print('Sample:', list(descriptions.keys())[:2])
        else:
            print('No descriptions parsed')
    else:
        print('No response from Goose CLI')


if __name__ == "__main__":
    main()
