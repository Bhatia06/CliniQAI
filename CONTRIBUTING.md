# Contributing to CliniQAI

Thank you for considering contributing to CliniQAI! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to uphold our Code of Conduct:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
   ```bash
   git clone https://github.com/yourusername/CliniQAI.git
   cd CliniQAI
   ```
3. **Set up the development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Development Workflow

1. **Create a branch** for your feature or bugfix
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, maintainable code
   - Follow the existing code style
   - Add comments where necessary

3. **Test your changes**
   - Ensure the application runs without errors
   - Test all components that might be affected by your changes
   - Verify that your feature works as expected

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Submit a pull request**
   - Go to your fork on GitHub
   - Click "New pull request"
   - Select your branch and submit the PR with a clear description

## Coding Standards

### Python Code

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use meaningful variable and function names
- Include docstrings for functions and classes
- Keep functions focused on a single responsibility
- Limit line length to 88 characters

### HTML/CSS

- Use 2-space indentation
- Include appropriate comments
- Follow a consistent naming convention
- Ensure UI is responsive and accessible

### JavaScript

- Use ES6+ features where appropriate
- Comment complex logic
- Follow consistent naming conventions
- Avoid unnecessary global variables

## Pull Request Process

1. Ensure your code follows the coding standards
2. Update documentation if needed
3. Include a description of the changes and their purpose
4. Make sure all tests pass
5. Your PR will be reviewed by maintainers who may request changes

## Types of Contributions

### Bug Reports

- Use the issue tracker on GitHub
- Describe the bug in detail (what happened, what you expected to happen)
- Include steps to reproduce the issue
- Mention your environment (OS, browser, Python version)

### Feature Requests

- Use the issue tracker and label as "enhancement"
- Clearly describe the feature and its benefits
- Discuss possible implementation approaches

### Documentation

- Help improve or translate documentation
- Fix typos or clarify explanations
- Add examples or use cases

## Community

- Join discussions in the issue tracker
- Help answer questions from other contributors
- Share the project with others who might be interested

## Attribution

Contributors will be acknowledged in the project documentation. Thank you for your contributions to improving healthcare through technology!

---

By contributing to CliniQAI, you help create better tools for healthcare professionals and patients, potentially improving the identification and management of adverse drug reactions. 