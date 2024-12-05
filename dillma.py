#!/usr/bin/env python3

import sys
import argparse
from openai import OpenAI

client = OpenAI()

def is_control_character(char):
    """Determines if a character is a control character."""
    char_code = ord(char)
    return (
        (0 <= char_code <= 31 and char_code not in {9, 10, 13}) or  # Exclude \t, \n, \r
        char_code == 127 or  # DEL (Delete)
        (128 <= char_code <= 159)  # Extended control characters
    )

def to_caret_notation(char):
    """Converts a control character to its caret notation."""
    char_code = ord(char)
    if char_code <= 31:
        return f"^{chr(char_code + 64)}"
    elif char_code == 127:
        return "^?"
    else:
        return f"\\x{char_code:02x}"

def get_terminal_friendly_string(text):
    """Converts a string to a terminal-friendly representation."""
    result = []
    for char in text:
        if is_control_character(char):
            result.append(to_caret_notation(char))
        else:
            result.append(char)
    return ''.join(result)

def query_ai(system_prompt, user_data):
    try:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",  
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_data}
            ],
            temperature=0.8,
            max_tokens=800
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"An error occurred: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Query AI and process results.")
    parser.add_argument("-q", "--query", help="Custom user query for the LLM (system prompt).")
    parser.add_argument("positional_query", nargs="?", help="Positional query for the LLM (fallback if -q/--query is not specified).")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode to print hex representation if control characters are present.")
    parser.add_argument("-v", "--show-non-printable", action="store_true", required=False, help="Display non-printing characters so they are visible.")
   
    args = parser.parse_args()
    system_prompt = args.query or args.positional_query
    if not system_prompt:
        print("Error: A query is required either as a positional argument or with -q/--query.")
        sys.exit(1)

    user_data = ""
    if not sys.stdin.isatty():
        user_data = sys.stdin.read()

    result = query_ai(system_prompt, user_data)

    if args.debug:
        hex_representation = " ".join(f"{ord(c):02x}" for c in result)
        if any(is_control_character(c) for c in result):
            print(f"* Debug: Control characters detected in response:\n{hex_representation}\n")

    if args.show_non_printable:
        result = get_terminal_friendly_string(result)
    
    print(result)

if __name__ == "__main__":
    main()