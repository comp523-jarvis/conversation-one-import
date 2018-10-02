"""
Client for interacting with Conversation.one.

This module contains functionality to obtain an authentication token
through the UI as well as perform project imports and exports using
Conversation.one's API.
"""

import io
import logging
import random

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = 'https://dashboard.conversation.one'
EXPORT_URI = '/API/export_rules.php'
IMPORT_URI = '/API/import_rules.php'
LOGIN_URI = '/hybridauth/window/Google?destination=user/login&destination_error=user/login'     # noqa

AUTH_COOKIE_NAME = 'SSESSdd77a869f34d32a764688b5b7691433b'

# Input identifiers
EMAIL_INPUT_ID = 'identifierId'
PASSWORD_INPUT_NAME = 'password'


logger = logging.getLogger(__name__)


def export_project(token, app_id, app_key):
    """
    Download the export of a conversation.one project.

    Args:
        token:
            A token authorizing the export request.
        app_id:
            The ID of the project to export.
        app_key:
            The API key for the project to export.

    Returns:
        The contents of the zip file as a BytesIO instance.
    """
    export_url = f'{BASE_URL}{EXPORT_URI}'
    logger.debug('Exporting project using endpoint: %s', export_url)
    r = requests.post(
        export_url,
        cookies={AUTH_COOKIE_NAME: token},
        data={
            'domain_id': app_id,
            'key': app_key,
            'new_format': '1',
            # Testing indicates 'random' needs to be a 7 digit number.
            'random': random.randint(1_000_000, 9_999_999),
        },
    )
    r.raise_for_status()

    logger.info('Exported project %s', app_id)

    return io.BytesIO(r.content)


def import_project(token, app_id, app_key, source, user):
    """
    Import a project into Conversation.one.
    """
    import_url = f'{BASE_URL}{IMPORT_URI}'
    logger.debug('Importing project using endpoint: %s', import_url)
    r = requests.post(
        import_url,
        cookies={AUTH_COOKIE_NAME: token},
        data={
            'domain_id': app_id,
            'key': app_key,
            'user': user,
        },
        files={'file': ('output.zip', source, 'application/zip')},
    )
    r.raise_for_status()

    logger.debug('Import response: %s', r.text)

    logger.info("Imported project %s", app_id)


def log_in(email, password):
    """
    Log into Conversation.one through Google to obtain an auth token.

    Returns:
        An auth token.
    """
    logger.info('Logging in to Conversation.one')

    driver = open_browser()

    login_url = f'{BASE_URL}{LOGIN_URI}'
    driver.get(login_url)
    logger.debug('Opened login page: %s', login_url)

    logger.debug('Searching for email input')
    email_input = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, EMAIL_INPUT_ID)),
    )
    logger.debug('Found email input')

    email_input.send_keys(email)
    email_input.send_keys(Keys.ENTER)
    logger.debug('Entered email: %s', email)

    logger.debug('Searching for password input')
    password_input = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.NAME, PASSWORD_INPUT_NAME)),
    )
    logger.debug('Found password input')

    password_input.send_keys(password)
    password_input.send_keys(Keys.ENTER)
    logger.debug('Entered password')

    logger.debug('Waiting for authentication to complete.')
    WebDriverWait(driver, 30).until(EC.title_contains('Conversation'))
    logger.debug('Successfully redirected to Conversation.one')

    token = driver.get_cookie(AUTH_COOKIE_NAME)['value']
    logger.debug('Found authentication token')

    driver.quit()

    logger.info('Succesfully obtained authentication token.')

    return token


def open_browser():
    opts = webdriver.firefox.options.Options()
    opts.set_headless()

    driver = webdriver.Firefox(options=opts)

    logger.debug("Opened Firefox instance.")

    return driver
