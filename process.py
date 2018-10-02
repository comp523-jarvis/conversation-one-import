#!/usr/bin/env python3

import argparse
import logging
import os
import re
import shutil
import tempfile
import zipfile

try:
    import client
    AUTO_IMPORT_AVAILABLE = True
except ImportError:
    AUTO_IMPORT_AVAILABLE = False


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


logger = logging.getLogger(__name__)


class ImproperlyConfiguredException(BaseException):
    """
    Exception indicating improper configuration of the program.

    This could be caused by an invalid combination of arguments or the
    omition of certain parameters.
    """


def extract_archive(source, dest_path):
    """
    Extract a zip archive to a destination path.
    """
    with zipfile.ZipFile(source) as archive:
        archive.extractall(dest_path)
        logger.debug("Extracted archive to '%s'", dest_path)


def get_arg_parser():
    """
    Get the parser for the arguments given to the program.

    Returns:
        The argument parser to use.
    """
    parser = argparse.ArgumentParser(
        description=("Insert dynamic imports into an export archive from "
                     "conversation.one"),
    )

    parser.add_argument(
        '--import-root',
        default=os.getcwd(),
        help=("The root directory to search for imports from. Defaults to the "
              "current working directory."),
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

    # Archive input/output methods
    parser.add_argument(
        '--auto-import',
        action='store_true',
        default=False,
        help=("Automatically obtain the export archive from Conversation.one "
              "to process."),
    )
    parser.add_argument(
        '--infile',
        help=("Path to a local archive to process. Mutually exclusive with "
              "the '--auto-import' flag."),
        type=argparse.FileType('rb'),
    )
    parser.add_argument(
        '--outfile',
        help=("Path where the processed archive will be created. Required if "
              "'--auto-import' is not set."),
    )

    # Conversation.one project information
    parser.add_argument(
        '--app-id',
        help=("The ID of the project to process on Conversation.one. Must be "
              "set if '--auto-import' is set."),
    )
    parser.add_argument(
        '--app-key',
        help=("The API key for the project to import from Conversation.one. "
              "Must be set if '--auto-import' is set."),
    )

    # Authentication information
    parser.add_argument(
        '--google-email',
        help=("The Google email account used to log in to Conversation.one. "
              "Must be set if '--auto-import' is set."),
    )
    parser.add_argument(
        '--google-password',
        help=("The password for the Google account used to log in to "
              "Conversation.one. Must be set if '--auto-import' is set."),
    )

    return parser


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
    args = parse_args()

    if args.auto_import:
        token = client.log_in(args.google_email, args.google_password)
        zip_source = client.export_project(
            app_id=args.app_id,
            app_key=args.app_key,
            token=token,
        )
    else:
        zip_source = args.infile

    with tempfile.TemporaryDirectory() as tempdir:
        # Extract the archive
        logger.debug("Create temporary directory: %s", tempdir)

        extracted = os.path.join(tempdir, 'extracted')
        extract_archive(zip_source, extracted)

        # Process the files to insert our dynamic imports.
        interaction_rules = os.path.join(
            extracted,
            'Basic rules',
            'interaction_rules.js',
        )
        process_file(interaction_rules, args.import_root)

        # If a zip extension is provided, remove it because it will be
        # added later.
        if args.auto_import:
            outfile = os.path.join(tempdir, 'output')
            logger.debug(
                "Auto import is enabled. Generated output filename: %s",
                outfile,
            )
        else:
            outfile = args.outfile

        if outfile.endswith('.zip'):
            outfile = outfile[:-4]
            logger.debug("Stripped '.zip' extension from outfile")

        # Pack the new archive
        shutil.make_archive(outfile, 'zip', extracted)

        if args.auto_import:
            with open(f'{outfile}.zip', 'rb') as f:
                client.import_project(
                    app_id=args.app_id,
                    app_key=args.app_key,
                    source=f,
                    token=token,
                    user=args.google_email,
                )


def parse_args():
    """
    Parse and validate the arguments provided to the program.

    Returns:
        The parsed arguments.
    """
    parser = get_arg_parser()
    args = parser.parse_args()

    # We do this as early as possible so that we can start logging ASAP.
    log_level = VERBOSITY_LEVELS[
        max(0, min(len(VERBOSITY_LEVELS) - 1, args.verbose))
    ]
    logging.basicConfig(level=log_level)

    if args.auto_import:
        logger.debug('Validating arguments for auto import')

        if not AUTO_IMPORT_AVAILABLE:
            raise ImproperlyConfiguredException(
                "Could not import functionality to enable auto import. Please "
                "ensure the requirements are installed and try again."
            )

        if not args.app_id:
            raise ImproperlyConfiguredException(
                "The '--app-id' option must be set if the '--auto-import' "
                "flag is used."
            )

        if not args.app_key:
            raise ImproperlyConfiguredException(
                "The '--app-key' option must be set if the '--auto-import' "
                "flag is used."
            )

        if not args.google_email:
            raise ImproperlyConfiguredException(
                "The '--google-email' option must be set if the "
                "'--auto-import' flag is used."
            )

        if not args.google_password:
            raise ImproperlyConfiguredException(
                "The '--google-password' option must be set if the "
                "'--auto-import' flag is used."
            )
    else:
        logger.debug('Validating arguments for local import')

        if not args.infile:
            raise ImproperlyConfiguredException(
                "The '--infile' argument must be provided if '--auto-import' "
                "is not used."
            )

        if not args.outfile:
            raise ImproperlyConfiguredException(
                "The '--outfile' argument must be provided if '--auto-import' "
                "is not used."
            )

    return args


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
