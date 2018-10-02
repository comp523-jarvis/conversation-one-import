# Conversation.one Import

[![Travis (.com)](https://img.shields.io/travis/com/comp523-jarvis/conversation-one-import.svg)](https://travis-ci.com/comp523-jarvis/conversation-one-import)

This is a script to dynamically insert code into an archive from conversation.one and repack the archive. The repacked archive can then be imported back into the conversation.one project.

## Features

### Custom Intent Code

Custom code for handling an intent can be included using the following syntax:

```js
// import yourCustomCodeFile.js
// end yourCustomCodeFile.js
```

The script will insert the contents of `yourCustomCodeFile.js` between the tags. Because of the ending and closing tags, this feature is idempotent.

### Automatic Import and Export

If the credentials for interacting with Conversation.one are provided, the script can process the project in place without need for the user to export and import archives.

## Usage

### Requirements

A Unix environment with Python 3 installed and accessible from `PATH`.

If you are using the auto-import feature, you must also have some third party dependencies installed. These packages can be installed using [pipenv](https://pipenv.readthedocs.io/en/latest/) with the command:

```
pipenv install
```

Additionally, the `geckodriver` binary must be accessible from your `PATH`. The releases of `geckodriver` are [available on GitHub](https://github.com/mozilla/geckodriver/releases).

### Automatic Import and Export

The script has the ability to log in to Conversation.one, export the project, process it, and then import the processed archive back into Conversation.one.

#### Workflow

##### Project Information

Before you can run the script, you need some information from Conversation.one about your project. From the [Conversation.one project dashboard](https://dashboard.conversation.one/projects), select the project you would like to work on. Ensure you select the appropriate tab, either "Production" or "Staging". Now take note of the "App ID" and "API Key" fields.

![App Information](/docs/images/AppInformation.png)

##### Process and Import

Now you can run the script and your Conversation.one project will be modified in place.

```
pipenv run process.py \
    --auto-import \
    --app-id $APP_ID \
    --app-key $APP_KEY \
    --google-email $GOOGLE_EMAIL \
    --google-password $GOOGLE_PASSWORD \
    --import-path path/to/directory/with/intent/code
```

### Manual Import and Export

The script can also process a local version of the exported project. The user will have to take care of exporting the project from Conversation.one and then importing the output of the script again.

#### Workflow

##### Export

First export your conversation.one project using the "Export All Rules" option.

![Export All Rules](/docs/images/Export.png)

##### Process

Then run the script, passing in the archive you just created.

```
./process.py --infile path/to/exported/archive.zip --outfile output
```

##### Import

Now you can import the archive back in to your project by uploading the `output.zip` file created by the script.

![Import All Rules](/docs/images/Import.png)

### CLI Parameters

```
usage: process.py [-h] [--import-root IMPORT_ROOT] [-v] [--auto-import]
                  [--infile INFILE] [--outfile OUTFILE] [--app-id APP_ID]
                  [--app-key APP_KEY] [--google-email GOOGLE_EMAIL]
                  [--google-password GOOGLE_PASSWORD]

Insert dynamic imports into an export archive from conversation.one

optional arguments:
  -h, --help            show this help message and exit
  --import-root IMPORT_ROOT
                        The root directory to search for imports from.
                        Defaults to the current working directory.
  -v, --verbose         A flag to increase the verbosity of the script's
                        output. Including the flag multiple times will
                        increase the verbosity.
  --auto-import         Automatically obtain the export archive from
                        Conversation.one to process.
  --infile INFILE       Path to a local archive to process. Mutually exclusive
                        with the '--auto-import' flag.
  --outfile OUTFILE     Path where the processed archive will be created.
                        Required if '--auto-import' is not set.
  --app-id APP_ID       The ID of the project to process on Conversation.one.
                        Must be set if '--auto-import' is set.
  --app-key APP_KEY     The API key for the project to import from
                        Conversation.one. Must be set if '--auto-import' is
                        set.
  --google-email GOOGLE_EMAIL
                        The Google email account used to log in to
                        Conversation.one. Must be set if '--auto-import' is
                        set.
  --google-password GOOGLE_PASSWORD
                        The password for the Google account used to log in to
                        Conversation.one. Must be set if '--auto-import' is
                        set.
```

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for developer instructions.
