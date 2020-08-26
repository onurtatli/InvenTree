[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Build Status](https://travis-ci.org/inventree/InvenTree.svg?branch=master)](https://travis-ci.org/inventree/InvenTree) [![Documentation Status](https://readthedocs.org/projects/inventree/badge/?version=latest)](https://inventree.readthedocs.io/en/latest/?badge=latest) [![Coverage Status](https://coveralls.io/repos/github/inventree/InvenTree/badge.svg)](https://coveralls.io/github/inventree/InvenTree)

<img src="images/logo/inventree.png" alt="InvenTree" width="128"/>

# InvenTree
InvenTree is an open-source Inventory Management System which provides powerful low-level stock control and part tracking. The core of the InvenTree system is a Python/Django database backend which provides an admin interface (web-based) and a JSON API for interaction with external interfaces and applications.

InvenTree is designed to be lightweight and easy to use for SME or hobbyist applications, where many existing stock management solutions are bloated and cumbersome to use. Updating stock is a single-action process and does not require a complex system of work orders or stock transactions. 

However, powerful business logic works in the background to ensure that stock tracking history is maintained, and users have ready access to stock level information.

## Getting Started

Refer to the [getting started guide](https://inventree.github.io/docs/start/install) for installation and setup instructions.

## Documentation

For InvenTree documentation, refer to the [InvenTre documentation website](https://inventree.github.io).

## Integration

InvenTree is designed to be extensible, and provides multiple options for integration with external applications or addition of custom plugins:

* [InvenTree API](https://inventree.github.io/docs/extend/api)
* [Python module](https://inventree.github.io/docs/extend/python)
* [Plugin interface](https://inventree.github.io/docs/extend/plugins)
* [Third party](https://inventree.github.io/docs/extend/integrate)

## Developer Documentation

For code documentation, refer to the [developer documentation](http://inventree.readthedocs.io/en/latest/).

## Contributing

Contributions are welcomed and encouraged. Please help to make this project even better! Refer to the [contribution page](https://inventree.github.io/pages/contribute).

## Donate

If you use InvenTree and find it to be useful, please consider making a donation toward its continued development. 

[Donate via PayPal](https://paypal.me/inventree?locale.x=en_AU)

inside WSL

## Installing

Each of these programs need to be installed (e.g. using apt or similar) before running the make install script:

sudo apt-get install python3 python3-dev python3-pip g++ make libpango-1.0-0 libpangocairo-1.0-0

## Virtual Environment

apt-get install python3-venv
python3 -m venv inventree-env
source inventree-env/bin/activate


## Installation

sudo make install

## Initialize Database

sudo make migrate

## Create Admin Account

sudo make superuser

## Run Development Server

cd InvenTree
python manage.py runserver 127.0.0.1:8000