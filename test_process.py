import os
from unittest import mock

import pytest

import process


def test_insert_imports():
    """
    Given a valid import directive, the contents of the referenced file
    should be inserted into the new content.
    """
    filename = 'foo.js'
    data = 'console.log("foo");'
    import_root = '/tmp'
    content = f'// import {filename}\n// end {filename}'
    expected = f'// import {filename}\n{data}\n// end {filename}'
    expected_import = os.path.join(import_root, filename)

    with mock.patch(
        'builtins.open',
        create=True,
        new=mock.mock_open(read_data=data),
    ) as mock_open:
        new_content = process.insert_imports(content, import_root)

    assert new_content == expected
    assert mock_open.call_count == 1
    assert mock_open.call_args[0] == (expected_import, 'r')


@pytest.mark.parametrize(
    'content',
    [
        '// import foo.js',                 # No closing tag
        '// import foo.js\n//end bar.js',   # Mismatched file names
        '// end foo.js',                    # No start tag
    ],
)
def test_insert_imports_mismatched_tags(content):
    """
    If one of the tags is missing or the filenames don't match, the
    content should not be altered.
    """
    assert process.insert_imports(content, '/tmp') == content


def test_insert_imports_overwrite():
    """
    If there is content between the opening and closing portions of the
    import directive, the content should be overwritten.
    """
    filename = 'foo.js'
    data = 'foo'
    import_root = '/tmp'
    content = f'// import {filename}\nbar\n// end {filename}'
    expected = f'// import {filename}\n{data}\n// end {filename}'
    expected_import = os.path.join(import_root, filename)

    with mock.patch(
        'builtins.open',
        create=True,
        new=mock.mock_open(read_data=data),
    ) as mock_open:
        new_content = process.insert_imports(content, import_root)

    assert new_content == expected
    assert mock_open.call_count == 1
    assert mock_open.call_args[0] == (expected_import, 'r')
