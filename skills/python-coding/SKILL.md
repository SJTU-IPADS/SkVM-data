---
name: python-coding
description: Python code generation with best practices, HTTP APIs, error handling, and script structure.
---

# Python Coding

## Script Structure

Always structure Python scripts with:

```python
#!/usr/bin/env python3
"""Brief description of what this script does."""

import sys
# standard library imports first
# third-party imports second

def main():
    """Main entry point."""
    # Core logic here
    pass

if __name__ == "__main__":
    main()
```

## HTTP Requests

### Using urllib (standard library, always available)
```python
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import json

def fetch_json(url):
    try:
        req = Request(url, headers={"User-Agent": "Python-Script/1.0"})
        with urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except (URLError, HTTPError) as e:
        print(f"Error fetching {url}: {e}")
        return None
```

### Using requests (if available)
```python
import requests

def fetch_json(url):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"Error: {e}")
        return None
```

## Error Handling

Always wrap external calls (HTTP, file I/O, parsing) in try/except:

```python
try:
    data = fetch_json(api_url)
    if data is None:
        print("Failed to fetch data")
        sys.exit(1)
    # process data
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)
```

## Common Patterns

- **JSON parsing**: `json.loads(text)` for strings, `json.load(file)` for files
- **File writing**: Use `with open(path, 'w') as f:` context manager
- **CLI arguments**: Use `sys.argv` for simple cases, `argparse` for complex
- **String formatting**: Use f-strings: `f"Temperature: {temp}°F"`
- **Data processing**: List comprehensions, dict comprehensions for transformations

## API Integration

When creating scripts that call APIs:
1. Define the API endpoint URL as a constant
2. Handle HTTP errors (4xx, 5xx) gracefully
3. Parse the JSON response
4. Extract and format the relevant data
5. Print a human-readable summary
6. Include a way to run the script standalone
