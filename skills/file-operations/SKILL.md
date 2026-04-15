---
name: file-operations
description: File and directory management, project structure creation, search and replace, configuration editing.
---

# File Operations

## Project Structure Creation

When creating a project structure:
1. Create directories first (top-down)
2. Create files with appropriate content
3. Verify the structure matches requirements

### Python Project Template
```
project-name/
├── src/
│   └── package_name/
│       └── __init__.py
├── tests/
│   └── __init__.py
├── pyproject.toml
└── README.md
```

### Generic Project Template
```
project-name/
├── src/
│   └── main.py
├── README.md
└── .gitignore
```

## File Search and Replace

When updating configuration files across a project:

1. **List target files** — identify all files that need changes
2. **Read each file** — understand the current content
3. **Make targeted changes** — replace specific values, not entire files
4. **Verify changes** — read the file back to confirm

### Common Config Changes
- Database host: `localhost` → `prod-db.example.com`
- Log level: `DEBUG` → `WARNING` or `ERROR`
- API endpoints: development → production URLs
- Database names: `dev_db` → `production_db`

## File Content Patterns

### .gitignore
```
__pycache__/
*.pyc
.env
node_modules/
dist/
*.egg-info/
```

### README.md
```markdown
# Project Name

Brief description.

## Installation
...

## Usage
...
```

### pyproject.toml
```toml
[project]
name = "package-name"
version = "0.1.0"
description = "Brief description"
requires-python = ">=3.10"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.backends._legacy:_Backend"
```

## Information Extraction

When extracting information from files:
1. Read the file completely
2. Identify the specific data points requested
3. Save extracted information to the output file in the requested format
