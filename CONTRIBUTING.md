# Contributing Guidelines

## Branching Strategy

The branching strategy for this project is to develop new features and bugfixes on branches based on `master`. The new branche is then pushed, and a pull request is opened to discuss the changes. After a code review passes, the pull request can be merged.


## Developer Environment

To either lint or test your local version of the project, you must install the development dependencies using [pipenv](https://pipenv.readthedocs.io/en/latest/).

```
pipenv install --dev
```

### Linting

All code is linted automatically on every push using [flake8](http://flake8.pycqa.org/en/latest/). To lint your local copy, you can use the command:

```
pipenv run flake8
```

If you would like to configure your local git repository to lint files before they are committed, install the flake8 git hook.

```
pipenv run flake8 --install-hook git
git config flake8.lazy true
git config flake8.strict true
```

### Testing

Tests are written using [pytest](https://docs.pytest.org/en/latest/). They are run on the CI server after every push. If you would like to run the tests on your local copy of the project, use the command:

```
pipenv run pytest
```
