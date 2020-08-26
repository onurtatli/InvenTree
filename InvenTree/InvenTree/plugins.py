# -*- coding: utf-8 -*-

import inspect
import importlib
import pkgutil


def iter_namespace(pkg):

    return pkgutil.iter_modules(pkg.__path__, pkg.__name__ + ".")


def get_modules(pkg):
    # Return all modules in a given package
    return [importlib.import_module(name) for finder, name, ispkg in iter_namespace(pkg)]


def get_classes(module):
    # Return all classes in a given module
    return inspect.getmembers(module, inspect.isclass)


def get_plugins(pkg, baseclass):
    """
    Return a list of all modules under a given package.

    - Modules must be a subclass of the provided 'baseclass'
    - Modules must have a non-empty PLUGIN_NAME parameter
    """

    plugins = []

    modules = get_modules(pkg)

    # Iterate through each module in the package
    for mod in modules:
        # Iterate through each class in the module
        for item in get_classes(mod):
            plugin = item[1]
            if issubclass(plugin, baseclass) and plugin.PLUGIN_NAME:
                plugins.append(plugin)

    return plugins
