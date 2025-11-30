# Contributing to TrackerSpotter

Thank you for your interest in contributing to TrackerSpotter! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

Before creating a bug report:
1. Check the [existing issues](https://github.com/jbesclapez/TrackerSpotter/issues)
2. Make sure you're using the latest version

When creating a bug report, include:
- **Clear title** describing the issue
- **Steps to reproduce** the bug
- **Expected behavior** vs **actual behavior**
- **Environment details**: OS version, Python version, torrent client used
- **Screenshots** if applicable
- **Log output** if relevant

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear title** describing the enhancement
- **Provide detailed description** of the suggested enhancement
- **Explain why** this enhancement would be useful
- **List alternatives** you've considered
- **Include mockups** or examples if applicable

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the code style guidelines
3. **Test your changes** thoroughly
4. **Update documentation** if needed
5. **Write clear commit messages**
6. **Submit a pull request**

#### Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update the CHANGELOG.md with your changes
3. Ensure all tests pass
4. Request review from maintainers

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- Virtual environment (recommended)

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/TrackerSpotter.git
cd TrackerSpotter

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

# Install development dependencies
pip install -r requirements-dev.txt

# Run TrackerSpotter
python trackerspotter.py
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html

# View coverage report
# Open htmlcov/index.html in browser
```

### Code Style

We follow PEP 8 style guidelines with some modifications:

```bash
# Format code with Black
black src/

# Check with flake8
flake8 src/ --max-line-length=100

# Type checking with mypy
mypy src/
```

## Project Structure

```
TrackerSpotter/
├── src/trackerspotter/      # Main source code
│   ├── models.py            # Data models
│   ├── database.py          # Database operations
│   ├── tracker_server.py    # Flask/SocketIO server
│   ├── utils.py             # Utility functions
│   ├── test_kit.py          # Test torrent generator
│   └── static/              # Web UI files
├── tests/                   # Test files
├── docs/                    # Documentation
├── build_scripts/           # Build scripts
└── trackerspotter.py        # Main entry point
```

## Coding Guidelines

### Python Code

```python
# Use type hints
def parse_info_hash(encoded_hash: str) -> tuple[bytes, str]:
    """
    Parse URL-encoded info hash
    
    Args:
        encoded_hash: URL-encoded 20-byte info hash
        
    Returns:
        Tuple of (raw bytes, hex string representation)
    """
    # Implementation

# Use f-strings for formatting
message = f"Received announce from {client_ip}:{port}"

# Handle errors gracefully
try:
    data = parse_announce(request.args)
except ValueError as e:
    logger.error(f"Invalid announce: {e}")
    return error_response("Invalid parameters")
```

### JavaScript Code

```javascript
// Use const/let, not var
const events = [];
let currentFilter = 'all';

// Use arrow functions
const formatBytes = (bytes) => {
    // Implementation
};

// Use async/await
async function loadEvents() {
    try {
        const response = await fetch('/api/events');
        const data = await response.json();
        // Process data
    } catch (error) {
        console.error('Error loading events:', error);
    }
}
```

### CSS Code

```css
/* Use CSS custom properties */
:root {
    --primary-color: #2563eb;
    --spacing-md: 1rem;
}

/* BEM-like naming */
.event-table__row--highlighted {
    background: var(--highlight-color);
}
```

## Commit Message Guidelines

Format: `<type>(<scope>): <description>`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(tracker): add support for scrape requests
fix(ui): correct progress bar calculation
docs(readme): update installation instructions
refactor(database): optimize query performance
```

## Testing Guidelines

### Unit Tests

```python
def test_parse_info_hash():
    """Test info hash parsing"""
    encoded = "%3A%7F%9B%2C..."
    raw, hex_str = parse_info_hash(encoded)
    
    assert len(raw) == 20
    assert len(hex_str) == 40
    assert hex_str == "3a7f9b2c..."
```

### Integration Tests

```python
def test_announce_endpoint(client):
    """Test announce endpoint"""
    response = client.get('/announce?info_hash=...&peer_id=...')
    
    assert response.status_code == 200
    assert b'interval' in response.data
```

## Documentation

- Update README.md for user-facing changes
- Update USAGE_GUIDE.md for feature additions
- Add docstrings to all functions and classes
- Comment complex logic
- Keep .cursorrules updated with project guidelines

## Areas We Need Help With

### High Priority
- UDP tracker support (BEP 15)
- Additional torrent client compatibility testing
- Performance optimization for large event logs
- Cross-platform support (macOS, Linux)

### Medium Priority
- UI/UX improvements
- Dark mode theme
- Chart/graph visualizations
- Session comparison feature

### Low Priority
- Internationalization (i18n)
- Plugin system
- Advanced filtering options
- DHT monitoring (separate from tracker)

## Questions?

- Open a [GitHub Discussion](https://github.com/jbesclapez/TrackerSpotter/discussions)
- Create an [Issue](https://github.com/jbesclapez/TrackerSpotter/issues)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to TrackerSpotter! 🎯

