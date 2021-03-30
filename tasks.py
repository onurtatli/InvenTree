# -*- coding: utf-8 -*-

from invoke import task
from shutil import copyfile

import random
import string
import os
import sys

def apps():
    """
    Returns a list of installed apps
    """

    return [
        'barcode',
        'build',
        'common',
        'company',
        'label',
        'order',
        'part',
        'report',
        'stock',
        'InvenTree',
        'users',
    ]

def localDir():
    """
    Returns the directory of *THIS* file.
    Used to ensure that the various scripts always run
    in the correct directory.
    """
    return os.path.dirname(os.path.abspath(__file__))

def managePyDir():
    """
    Returns the directory of the manage.py file
    """

    return os.path.join(localDir(), 'InvenTree')

def managePyPath():
    """
    Return the path of the manage.py file
    """

    return os.path.join(managePyDir(), 'manage.py')

def manage(c, cmd, pty=False):
    """
    Runs a given command against django's "manage.py" script.

    Args:
        c - Command line context
        cmd - django command to run
    """

    c.run('cd {path} && python3 manage.py {cmd}'.format(
        path=managePyDir(),
        cmd=cmd
    ), pty=pty)

@task(help={'length': 'Length of secret key (default=50)'})
def key(c, length=50, force=False):
    """
    Generates a SECRET_KEY file which InvenTree uses for generating security hashes
    """

    SECRET_KEY_FILE = os.path.join(localDir(), 'InvenTree', 'secret_key.txt')

    # If a SECRET_KEY file does not exist, generate a new one!
    if force or not os.path.exists(SECRET_KEY_FILE):
        print("Generating SECRET_KEY file - " + SECRET_KEY_FILE)
        with open(SECRET_KEY_FILE, 'w') as key_file:
            options = string.digits + string.ascii_letters + string.punctuation

            key = ''.join([random.choice(options) for i in range(length)])

            key_file.write(key)

    else:
        print("SECRET_KEY file already exists - skipping")


@task(post=[key])
def install(c):
    """
    Installs required python packages, and runs initial setup functions.
    """

    # Install required Python packages with PIP
    c.run('pip3 install -U -r requirements.txt')

    # If a config.yaml file does not exist, copy from the template!
    CONFIG_FILE = os.path.join(localDir(), 'InvenTree', 'config.yaml')
    CONFIG_TEMPLATE_FILE = os.path.join(localDir(), 'InvenTree', 'config_template.yaml')

    if not os.path.exists(CONFIG_FILE):
        print("Config file 'config.yaml' does not exist - copying from template.")
        copyfile(CONFIG_TEMPLATE_FILE, CONFIG_FILE)


@task
def shell(c):
    """
    Open a python shell with access to the InvenTree database models.
    """

    manage(c, 'shell', pty=True)


@task
def superuser(c):
    """
    Create a superuser (admin) account for the database.
    """

    manage(c, 'createsuperuser', pty=True)

@task
def check(c):
    """
    Check validity of django codebase
    """

    manage(c, "check")

@task
def migrate(c):
    """
    Performs database migrations.
    This is a critical step if the database schema have been altered!
    """

    print("Running InvenTree database migrations...")
    print("========================================")

    manage(c, "makemigrations")
    manage(c, "migrate")
    manage(c, "migrate --run-syncdb")
    manage(c, "check")

    print("========================================")
    print("InvenTree database migrations completed!")


@task
def static(c):
    """
    Copies required static files to the STATIC_ROOT directory,
    as per Django requirements.
    """

    manage(c, "collectstatic")


@task(pre=[install, migrate, static])
def update(c):
    """
    Update InvenTree installation.

    This command should be invoked after source code has been updated,
    e.g. downloading new code from GitHub.

    The following tasks are performed, in order:

    - install
    - migrate
    - static
    """
    pass

@task
def translate(c):
    """
    Regenerate translation files.

    Run this command after added new translatable strings,
    or after adding translations for existing strings.
    """

    # Translate applicable .py / .html / .js files
    manage(c, "makemessages -e py -e html -e js")
    manage(c, "compilemessages")

    path = os.path.join('InvenTree', 'script', 'translation_stats.py')

    c.run(f'python {path}')

@task
def style(c):
    """
    Run PEP style checks against InvenTree sourcecode
    """

    print("Running PEP style checks...")
    c.run('flake8 InvenTree')

@task
def test(c, database=None):
    """
    Run unit-tests for InvenTree codebase.
    """
    # Run sanity check on the django install
    manage(c, 'check')

    # Run coverage tests
    manage(c, 'test', pty=True)

@task
def coverage(c):
    """
    Run code-coverage of the InvenTree codebase,
    using the 'coverage' code-analysis tools.

    Generates a code coverage report (available in the htmlcov directory)
    """

    # Run sanity check on the django install
    manage(c, 'check')

    # Run coverage tests
    c.run('coverage run {manage} test {apps}'.format(
        manage=managePyPath(),
        apps=' '.join(apps())
    ))

    # Generate coverage report
    c.run('coverage html')

@task
def mysql(c):
    """
    Install packages required for using InvenTree with a MySQL database.
    """
    
    print('Installing packages required for MySQL')

    c.run('sudo apt-get install mysql-server libmysqlclient-dev')
    c.run('pip3 install mysqlclient')

@task
def postgresql(c):
    """
    Install packages required for using InvenTree with a PostgreSQL database
    """

    print("Installing packages required for PostgreSQL")

    c.run('sudo apt-get install postgresql postgresql-contrib libpq-dev')
    c.run('pip3 install psycopg2')

@task(help={'filename': "Output filename (default = 'data.json')"})
def export_records(c, filename='data.json'):
    """
    Export all database records to a file
    """

    # Get an absolute path to the file
    if not os.path.isabs(filename):
        filename = os.path.join(localDir(), filename)
        filename = os.path.abspath(filename) 

    print(f"Exporting database records to file '{filename}'")

    if os.path.exists(filename):
        response = input("Warning: file already exists. Do you want to overwrite? [y/N]: ")
        response = str(response).strip().lower()

        if response not in ['y', 'yes']:
            print("Cancelled export operation")
            sys.exit(1)

    cmd = f'dumpdata --exclude contenttypes --exclude auth.permission --indent 2 --output {filename}'

    manage(c, cmd, pty=True)

@task(help={'filename': 'Input filename'})
def import_records(c, filename='data.json'):
    """
    Import database records from a file
    """

    # Get an absolute path to the supplied filename
    if not os.path.isabs(filename):
        filename = os.path.join(localDir(), filename)

    if not os.path.exists(filename):
        print(f"Error: File '{filename}' does not exist")
        sys.exit(1)

    print(f"Importing database records from '{filename}'")

    cmd = f'loaddata {filename}'

    manage(c, cmd, pty=True)

@task
def import_fixtures(c):
    """
    Import fixture data into the database.

    This command imports all existing test fixture data into the database.

    Warning:
        - Intended for testing / development only!
        - Running this command may overwrite existing database data!!
        - Don't say you were not warned...
    """

    fixtures = [
        # Build model
        'build',
        
        # Common models
        'settings',

        # Company model
        'company',
        'price_breaks',
        'supplier_part',

        # Order model
        'order',

        # Part model
        'bom',
        'category',
        'params',
        'part',
        'test_templates',

        # Stock model
        'location',
        'stock_tests',
        'stock',
    ]

    command = 'loaddata ' + ' '.join(fixtures)

    manage(c, command, pty=True)

@task
def backup(c):
    """
    Create a backup of database models and uploaded media files.

    Backup files will be written to the 'backup_dir' file specified in 'config.yaml'
    """

    manage(c, 'dbbackup')
    manage(c, 'mediabackup')

@task
def restore(c):
    """
    Restores database models and media files.

    Backup files are read from the 'backup_dir' file specified in 'config.yaml'
    """

    manage(c, 'dbrestore')
    manage(c, 'mediarestore')

@task(help={'address': 'Server address:port (default=127.0.0.1:8000)'})
def server(c, address="127.0.0.1:8000"):
    """
    Launch a (deveopment) server using Django's in-built webserver.

    Note: This is *not* sufficient for a production installation.
    """

    manage(c, "runserver {address}".format(address=address), pty=True)
