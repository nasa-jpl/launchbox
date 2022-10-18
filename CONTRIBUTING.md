# For contributing developers

How to run this project in a local development environment and make contributions to it.

- [Getting started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Launching the project](#launching-the-project)
- [Dependency management](#dependency-management)
- [Linting and formatting](#linting-and-formatting)
- [Pull request guidance](#pull-request-guidance)
- [Publishing to PyPI](#publishing-to-pypi)
- [Contribution licensing](#contribution-licensing)


## Getting started

### Prerequisites

We recommend the use of [Docker](https://www.docker.com/get-started/) for local development.

Experienced developers may opt to set up a Python virtual environment for the application
and connect to your own PostgreSQL, S3-like object storage, and Redis services.

### Launching the project

1. Clone this repository and go into its directory
2. Launch the Docker cluster:
   ```bash
   make start
   ```
3. Open the dashboard:
   ```bash
   make dashboard
   ```

When saving Python files, the application will automatically reload itself in the container.

## Dependency management

### Python

Our Python package requirements workflow, based on
[“A Better Pip Workflow™” by Kenneth Reitz](https://kenreitz.org/essays/2016/02/25/a-better-pip-workflow):

- `launchbox/requirements/requirements-to-freeze.txt` specifies pinned versions of our top-level dependencies.
- `launchbox/requirements.txt` contains the output of `pip freeze`
  after running `pip install -r requirements/ requirements-to-freeze.txt`
  (within the app container, which mounts the `launchbox` folder).
- For normal installation, use `pip install -r requirements.txt` (within the app container). 

Steps for updating dependencies:

1. Make updates to top-level dependencies in `launchbox/requirements/requirements-to-freeze.txt`
2. Attach to the app container:
   ```bash
   make terminal
   ```
3. Uninstall all currently-installed dependencies:
   ```bash
   pip freeze | xargs pip uninstall -y
4. Install updated top-level dependencies and subdependencies:
   ```bash
   pip install -r requirements/requirements-to-freeze.txt 
   ```
5. Update the complete list of pinned dependencies:
   ```bash
   pip freeze > requirements.txt
   ```
6. Test the updates!

### Frontend

We follow a standard npm-based workflow for managing our frontend dependencies.


## Linting and formatting

### Python

This project uses Flake8, isort, and Black for Python linting and formatting. 

#### Editor Configuration

- [Black's editor integration docs](https://black.readthedocs.io/en/stable/integrations/)
- [isort's plugin docs](https://github.com/PyCQA/isort/wiki/isort-Plugins)
- Flake8: [VS Code docs](https://code.visualstudio.com/docs/python/linting#_flake8), [PyCharm tutorial](https://realpython.com/pycharm-guide/#using-plugins-and-external-tools-in-pycharm)

### Frontend code

This project uses ESLint, Prettier, and Stylelint for frontend linting and formatting.

#### Editor Configuration

- [Black's editor integration docs](https://black.readthedocs.io/en/stable/integrations/)
- [isort's plugin docs](https://github.com/PyCQA/isort/wiki/isort-Plugins)
- Flake8: [VS Code docs](https://code.visualstudio.com/docs/python/linting#_flake8), [PyCharm tutorial](https://realpython.com/pycharm-guide/#using-plugins-and-external-tools-in-pycharm)

### Pre-commit enforcement

We strongly encourage using the [pre-commit](https://pre-commit.com/) package
to ensure coding standards are enforced prior to committing your code.
Here's how to set it up for this project:

1. [Install pre-commit](<https://pre-commit.com/#install>) if you have not already.
2. If you had previously install it, verify the installation and
   [ensure you're running the latest version](https://github.com/pre-commit/pre-commit/blob/main/CHANGELOG.md):
   ```bash
   pre-commit --version
   ```
3. Install the Git hooks in this project:
   ```bash
   pre-commit install
   ```
4. Now, every time you go to make a commit, `pre-commit` will run automatically.
   If it fails, the commit will not be executed, and you will have to fix the identified problems to continue.


## Pull request guidance

This repository employs the [Release Drafter](https://github.com/marketplace/actions/release-drafter) GitHub Actions workflow to automatically build draft release notes as pull requests are merged. Release Drafter will categorize the main type of changes in each PR within the release notes and also determine what the version number of the next release should be (depending on whether the release is a major, minor, or patch release).

Release Drafter's ability to do this correctly **depends on PRs being tagged with certain labels**. Most PRs should include at least two labels:

1. A label for the **category** of the changes included in the PR (`feature`, `fix`, `docs`, or `maintenance`)
2. A label for the **significance** of the chance
   (`major`, `minor`, or `patch`, per [Semantic Versioning](https://semver.org/) definitions)

Release Drafter will attempt to automatically apply the category label to a new PR
based on its branch name, title, or paths of files that were changed.
Please check that it did this sensibly, and modify the labels as necessary.
Try to avoid having two major category labels on a PR,
because it will then be added to both of those categories in the list.

The quality of the generated release notes also depends on PRs having good human-readable titles.

In cases where a PR is not worth noting in the release notes, you can also
tell Release Drafter not to add an entry for it by labeling it with `skip-changelog`.

Finally, don't fret about this too much!
The Release Drafter configuration and labeling scheme may take some time to fine-tune,
and the drafted release notes can always be manually edited before final publication.


## Publishing to PyPI

_[To be completed after initial release on PyPI.]_


## Contribution licensing

All contributions to this project will be released under the same MIT License as the overall project.
By submitting a pull request, you are agreeing to comply with these terms.
