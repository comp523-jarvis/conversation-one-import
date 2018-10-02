#!/usr/bin/env python3

import argparse
import logging
import os
import re
import shutil
import sys
import tempfile
import zipfile


VERBOSITY_LEVELS = [
    logging.INFO,
    logging.DEBUG,
]


IMPORT_DIRECTIVE_PATTERN = re.compile(
    r'^// import (?P<filename>[a-zA-Z0-9_\-\.]*)$'
    r'.*?'
    r'^// end (?P=filename)$',
    # There can be multiple lines between the start and end of the
    # directive, so we require the following flags.
    re.MULTILINE | re.DOTALL,
)


logging.basicConfig()
logger = logging.getLogger(__name__)


def extract_archive(source, dest_path):
    """
    Extract a zip archive to a destination path.
    """
    with zipfile.ZipFile(source) as archive:
        archive.extractall(dest_path)
        logger.debug("Extracted archive to '%s'", dest_path)


def insert_imports(content, import_root):
    """
    Scan the provided content for import directives and insert the
    appropriate new content.

    Args:
        content:
            The content containing the import directives to perform.
        import_root:
            The root directory to search for imports from. The file path
            referenced in each ``// import <file>`` directive will be
            appended to the import root when opening the file to import.

    Returns:
        The provided content with all import directives completed.
    """
    logger.debug("Start import processing")

    def replace_func(match):
        logger.debug("Found import directive:\n%s", match.group(0))
        filename = match.group('filename')

        import_path = os.path.join(import_root, filename)
        with open(import_path, 'r') as f:
            code = f.read()

        logger.info("Inserted contents of %s", import_path)

        return '// import {filename}\n{content}\n// end {filename}'.format(
            content=code,
            filename=filename,
        )

    new_content = re.sub(IMPORT_DIRECTIVE_PATTERN, replace_func, content)

    logger.debug("End import processing")

    return new_content


def main():
    """
    Entry point into the script.

    The general process is we extract the archive, process the files
    we're interested in, then repack the archive.
    """
    args = parse_args(sys.argv[1:])

    # Clamp verbosity level to allowable range
    logger.setLevel(
        VERBOSITY_LEVELS[max(0, min(len(VERBOSITY_LEVELS) - 1, args.verbose))],
    )

    with tempfile.TemporaryDirectory() as tempdir:
        # Extract the archive
        logger.debug("Create temporary directory: %s", tempdir)
        extract_archive(args.infile, tempdir)

        # Process the files to insert our dynamic imports.
        interaction_rules = os.path.join(
            tempdir,
            'Basic rules',
            'interaction_rules.js',
        )
        process_file(interaction_rules, args.import_root)

        # If a zip extension is provided, remove it because it will be
        # added later.
        outfile = args.outfile
        if outfile.endswith('.zip'):
            outfile = outfile[:-4]

        # Pack the new archive
        shutil.make_archive(outfile, 'zip', tempdir)


def parse_args(args):
    """
    Parse the arguments provided to the program.

    Args:
        args:
            The arguments to parse. Typically some portion of
            ``sys.argv``.
    """
    parser = argparse.ArgumentParser(
        description=("Insert dynamic imports into an export archive from "
                     "conversation.one"),
    )

    parser.add_argument(
        'infile',
        help="The exported archive to process.",
        type=argparse.FileType('rb'),
    )
    parser.add_argument(
        'outfile',
        help="The name of the archive to output to.",
        type=str,
    )

    parser.add_argument(
        '--import-root',
        default=os.getcwd(),
        help=("The root directory to search for imports from. Defaults to the "
              "current working directory."),
        type=str,
    )

    parser.add_argument(
        '-v',
        '--verbose',
        action='count',
        default=0,
        help=("A flag to increase the verbosity of the script's output. "
              "Including the flag multiple times will increase the "
              "verbosity."),
    )

    return parser.parse_args(args)


def process_file(path, import_root):
    """
    Process a single file.

    Args:
        path:
            The path of the file to process.
        import_root:
            The root directory to search for imports from. The file path
            referenced in each ``// import <file>`` directive will be
            appended to the import root when opening the file to import.
    """
    logger.debug("Start processing %s", path)

    with open(path, 'r') as f:
        content = f.read()
    logger.debug("Read contents of %s", path)

    new_content = insert_imports(content, import_root)
    with open(path, 'w') as f:
        f.write(new_content)

    logger.debug("End processing %s", path)


if __name__ == '__main__':
    main()
