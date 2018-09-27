# Contributing Guidelines

## Branching Strategy

The branching strategy for this project is to develop new features and bugfixes on branches based on `master`. The new branche is then pushed, and a pull request is opened to discuss the changes. After a code review passes, the pull request can be merged.


## Testing

Tests are written using [pytest](https://docs.pytest.org/en/latest/). To run them, you must first install the test dependencies using [pipenv](https://pipenv.readthedocs.io/en/latest/).

```
pipenv install --dev
pipenv run pytest
```
