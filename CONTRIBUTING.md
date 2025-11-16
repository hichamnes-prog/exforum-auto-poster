# Contributing to ClipKit

Thank you for your interest in contributing to ClipKit! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/clipkit/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, etc.)
   - Logs or error messages

### Suggesting Features

1. Check existing feature requests
2. Create a new issue describing:
   - The problem you're trying to solve
   - Your proposed solution
   - Alternative solutions you've considered
   - Any additional context

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/clipkit.git
   cd clipkit
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**
   ```bash
   ./scripts/dev-setup.sh
   ```

4. **Make your changes**
   - Follow the coding standards below
   - Add tests if applicable
   - Update documentation

5. **Test your changes**
   ```bash
   # Backend tests
   cd backend
   pytest

   # Frontend tests
   cd frontend
   npm test
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

   Use conventional commits:
   - `feat:` new feature
   - `fix:` bug fix
   - `docs:` documentation changes
   - `style:` formatting, missing semicolons, etc.
   - `refactor:` code refactoring
   - `test:` adding tests
   - `chore:` maintenance tasks

7. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

   Then create a Pull Request on GitHub with:
   - Clear description of changes
   - Link to related issues
   - Screenshots/videos if UI changes

## Development Guidelines

### Backend (Python)

- Follow PEP 8 style guide
- Use type hints where possible
- Add docstrings to functions and classes
- Keep functions small and focused
- Use meaningful variable names

```python
def process_video(video_path: str, config: dict) -> List[Clip]:
    """
    Process video and generate clips.

    Args:
        video_path: Path to the video file
        config: Configuration dictionary

    Returns:
        List of generated clips
    """
    # Implementation
```

### Frontend (React)

- Use functional components and hooks
- Follow ESLint configuration
- Use meaningful component and variable names
- Keep components small and reusable
- Add PropTypes or TypeScript types

```jsx
function VideoCard({ video, onDelete }) {
  // Component implementation
}
```

### Commit Messages

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Example:
```
feat(transcription): add support for multiple languages

- Add language detection
- Support 50+ languages
- Update UI to show detected language

Closes #123
```

## Project Structure

```
clipkit/
├── backend/              # Python/FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Configuration
│   │   ├── models/      # Data models
│   │   ├── services/    # Business logic
│   │   └── worker/      # Celery tasks
│   └── tests/           # Backend tests
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   └── services/    # API client
│   └── public/
└── scripts/             # Utility scripts
```

## Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate
pytest
pytest --cov=app  # With coverage
```

### Frontend Tests

```bash
cd frontend
npm test
npm run test:coverage
```

## Documentation

- Update README.md for user-facing changes
- Add inline code comments for complex logic
- Update API documentation in docstrings
- Add examples for new features

## Code Review Process

1. Automated checks must pass (linting, tests)
2. At least one maintainer approval required
3. Address review comments
4. Squash commits if requested
5. Maintain clean git history

## Questions?

- Open a [Discussion](https://github.com/yourusername/clipkit/discussions)
- Join our community chat
- Email maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
