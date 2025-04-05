# EnvSwitch

A CLI tool that intelligently switches environment configurations in files based on context and intent.

## Overview

EnvSwitch helps developers quickly switch between different environment configurations (dev, staging, production, etc.) in configuration files. It uses fuzzy matching and AI-powered intent recognition to understand what environment you want to switch to and makes the appropriate replacements.

## Features

- 🧠 AI-powered intent recognition
- 🔍 Fuzzy matching for configuration values
- 🔄 Automatic environment detection
- 🧪 Dry run mode to preview changes
- 💾 Safe file writing

## Installation

```bash
# Clone the repository
git clone https://github.com/0xrushi/envswitch.git
cd envswitch

# Install the package
pip install -e .
```

## Usage

```bash
# Basic usage
envswitch <file> <context_json> "<intent>"

# Example
envswitch tests/target_file_1.txt tests/context.json "convert to staging"
envswitch tests/target_file_2.txt tests/context.json "convert to staging"
envswitch tests/target_file_3.txt tests/context.json "convert to staging"

# With write option (default is summary only)
envswitch tests/target_file_1.txt tests/context.json "switch to production" --write
```

### Arguments

- `file`: Path to the configuration file you want to modify
- `context_json`: Path to the context JSON file that defines your environments
- `intent`: Natural language instruction (e.g., "switch to staging", "use dev environment")

### Options

- `--write`, `-w`: Write changes to file (default: False)
- `--summary`: Preview changes in summary format (default: True)

## Context JSON Format

The context JSON file defines the mapping between environments and their configuration values:

```json
{
  "dev": {
    "https://api-dev.example.com": "backend",
    "8080": "port",
    "DEV": "env",
    "devblob.storage.azure.net": "blob"
  },
  "staging": {
    "https://api-staging.example.com": "backend",
    "9090": "port",
    "STAGING": "env",
    "stagingblob.storage.azure.net": "blob"
  }
}
```

Each environment (e.g., "dev", "staging") contains key-value pairs where:
- The key is the actual value in the configuration file
- The value is a label that identifies what this value represents

## Requirements

- Python 3.9+
- OpenAI API key (set as environment variable `OPENAI_API_KEY`)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.