# Development Guide

## Git Hooks

FastWG uses git hooks to ensure code quality before pushing changes. The hooks automatically run:

1. **Code style checks** (flake8)
2. **Code formatting checks** (black)
3. **Import sorting checks** (isort)
4. **Tests** (unittest)

### Setup

To install the git hooks:

```bash
./install-hooks.sh
```

### Manual Usage

You can run the checks manually:

```bash
# Run all checks
./.git/hooks/pre-push

# Run individual checks
flake8 fastwg/ tests/ --max-line-length=127 --max-complexity=10
black --check --diff fastwg/ tests/
isort --check-only --diff fastwg/ tests/
python run_tests.py
```

### Bypassing Hooks

If you need to bypass the pre-push hooks (not recommended):

```bash
git push --no-verify
```

### Configuration

The hooks use the following configuration:

- **flake8**: `.flake8` - Code style rules
- **black**: `pyproject.toml` - Code formatting rules
- **isort**: `pyproject.toml` - Import sorting rules

### Troubleshooting

If the hooks fail:

1. **Style errors**: Run `black fastwg/ tests/` and `isort fastwg/ tests/`
2. **Test failures**: Fix the failing tests
3. **Import errors**: Check that all imports are correct

## Development Tools

### Required Tools

```bash
pip install flake8 black isort mypy coverage
```

### Code Quality

- **flake8**: Code style and complexity checks
- **black**: Automatic code formatting
- **isort**: Import sorting
- **mypy**: Type checking (optional)

### Testing

```bash
# Run all tests
python run_tests.py

# Run with coverage
coverage run --source=fastwg run_tests.py
coverage report
coverage html  # Creates htmlcov/index.html
```

## Project Structure

```
fastwg/
├── fastwg/           # Main package
│   ├── core/        # Core functionality
│   ├── models/      # Data models
│   ├── utils/       # Utilities
│   └── locale/      # Translations
├── tests/           # Test suite
├── docs/            # Documentation
├── .git/hooks/      # Git hooks
├── .flake8          # flake8 configuration
├── pyproject.toml   # Project configuration
└── run_tests.py     # Test runner
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the git hooks: `./.git/hooks/pre-push`
5. Commit and push your changes
6. Create a pull request

The git hooks will ensure your code meets the project's quality standards.
