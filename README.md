# FCB1010 Editor

A Python library and command-line tool for editing and managing Behringer FCB1010 MIDI foot controller presets.

## Features

- Edit, save, and load FCB1010 presets
- **SysEx interface for direct hardware communication**
- Command-line interface for preset management
- Send presets to hardware (requires connected FCB1010)
- Google Sheets integration (optional)
- Modular, testable codebase

## Project Structure

```
.
├── scripts/         # CLI tools and integration scripts
├── src/fcb1010/     # Core library code
├── tests/           # Unit tests
├── docs/            # Documentation and best practices
├── requirements.txt # Python dependencies
├── pyproject.toml   # Tooling config (black, flake8, etc.)
├── Makefile         # Common developer tasks
└── README.md        # This file
```

## Setup

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. (Optional) Set up a virtual environment:
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

## Usage

### Basic Usage

- Run the CLI editor:
  ```sh
  python3 scripts/editor.py
  ```

### SysEx Interface

The library provides an easy-to-use SysEx interface for direct communication with the FCB1010:

```python
from src.fcb1010 import FCB1010

# Connect to FCB1010
fcb = FCB1010()

# Send raw sysex data
fcb.send_sysex_data([0x01, 0x02, 0x03])

# Read preset via sysex
preset_data = fcb.read_preset_sysex(0)

# Write preset via sysex
fcb.write_preset_sysex(0, [0x00, 0x01, 0x02])

# Clean up
fcb.close()
```

For more examples, see `scripts/sysex_example.py`:
```sh
python3 scripts/sysex_example.py
```

### Development

- Run tests:
  ```sh
  make test
  ```
- Lint and format code:
  ```sh
  make lint
  make format
  ```

## Contributing

See `CONTRIBUTING.md` for guidelines.

## Documentation

See the `docs/` folder for best practices, architecture, and troubleshooting.

---

## Next Steps & Expansion

1. **Documentation Improvements**
   - Expand and update `docs/` with more usage examples and troubleshooting tips.
   - Add API documentation for all public classes and functions.

2. **Testing**
   - Increase test coverage, especially for CLI and integration scripts.
   - Add integration tests for hardware communication (mocking MIDI if needed).

3. **Code Quality**
   - Address remaining lint warnings (mainly line length, E501).
   - Refactor long functions for readability and maintainability.

4. **Features**
   - Enhance Google Sheets integration and document its setup.
   - Add preset import/export for other formats (e.g., CSV, XML).
   - Implement a GUI (e.g., with Tkinter or PyQt) for users who prefer graphical editing.

5. **Packaging & Distribution**
   - Add a `setup.py` or update for PyPI distribution.
   - Provide Dockerfile or devcontainer.json for reproducible environments.

6. **Developer Experience**
   - Add pre-commit hooks for linting/formatting.
   - Add GitHub Actions for CI (lint, test, build).

7. **User Experience**
   - Add more helpful CLI prompts and error messages.
   - Support batch operations and scripting via CLI arguments.

8. **Community**
   - Write a Code of Conduct and expand contribution guidelines.
   - Encourage users to submit issues and feature requests.

---

Your workspace is now clean, organized, and ready for professional development and expansion! If you want to address all remaining lint warnings or need help with any of the next steps, just let me know.