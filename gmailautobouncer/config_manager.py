#!/usr/bin/env python3
"""
Provides common utilities for manipulating configuration properties.

This module contains methods for interacting with a JSON based configuration
file and error handling for any raised exceptions.  Once an initial
configuration is loaded, additional configurations can be merged
with the existing set of loaded properties, individual properties can be
added, updated, retrieved, renamed, or removed, and a collection of all
property names can be returned along with the ability to clear all name
value pairs from a loaded configuration.

Notes
-----
Gmail Auto Bouncer is distributed under the GNU Affero General Public License
v3 (https://www.gnu.org/licenses/agpl.html) as open source software with
attribution required.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License v3
(https://www.gnu.org/licenses/agpl.html) for more details.

Copyright (C) 2022 John Sonsini.  All rights reserved.  Source code available
under the AGPLv3.

"""
import json
import sys

import gmailautobouncer.utilities


class ConfigurationManager(object):
    """
    Provides common utilities for manipulating configuration properties.

    This class contains methods for interacting with a JSON based configuration
    file and error handling for any raised exceptions.  Once an initial
    configuration is loaded, additional configurations can be merged
    with the existing set of loaded properties, individual properties can be
    added, updated, retrieved, renamed, or removed, and a collection of all
    property names can be returned along with the ability to clear all name
    value pairs from a loaded configuration.

    """
    __config = None
    """dict: Mapping of property names and values"""

    def __init__(self):
        """
        Minimal constructor due to static nature of class.

        With every method in class denoted as static there is nothing to
        initialize in a constructor.

        """
        pass

    @staticmethod
    def load_configuration(path):
        """
        Imports configuration parameters from file.

        Creates a dictionary of properties from a JSON document if valid, else
        provides the parsing error to standard out.

        Parameters
        ----------
        path: str
            File path of the configuration to load.

        Returns
        -------
        bool
            Successfulness of loading the configuration file.

        """
        try:
            with open(path, "r") as configuration_file:
                ConfigurationManager.__config = json.load(
                    configuration_file)
            return True
        except:
            print("%s not a valid JSON file, error:  %s" % (
                path, gmailautobouncer.utilities.format_error(sys.exc_info())))
            return False

    @staticmethod
    def add_configuration(path):
        """
        Imports additional parameters and add to existing properties.

        Merges properties from an additional JSON document into an existing
        property dictionary, else provides the parsing error or the lack of an
        existing dictionary to standard out.

        Parameters
        ----------
        path: str
            File path of the configuration to load.

        Returns
        -------
        bool
            Successfulness of loading the configuration file.

        """
        if ConfigurationManager.__config:
            try:
                with open(path, "r") as configuration_file:
                    ConfigurationManager.__config.update(
                        json.load(configuration_file))
                return True
            except:
                print("%s not a valid JSON file, error:  %s" % (
                    path,
                    gmailautobouncer.utilities.format_error(sys.exc_info())))
        else:
            print("no configuration loaded")
            return False

    @staticmethod
    def get_property(name):
        """
        Retrieves property value if available.

        Gets the value associated with the property name if present in the
        current loaded dictionary, else returns None and provides message
        describing error to standard out.

        Parameters
        ----------
        name: str
            Property name.

        Returns
        -------
        obj
            Associated value if name found else None.

        """
        if ConfigurationManager.__config:
            if name in ConfigurationManager.__config:
                return ConfigurationManager.__config[name]
            else:
                print("%s not loaded in configuration" % name)
                return None
        else:
            print("no configuration loaded")
            return None

    @staticmethod
    def add_property(name, value):
        """
        Includes property name value pair in existing dictionary.

        Creates a new property in the loaded configuration, else provides an
        error message detailing that the property already exists or that no
        configuration is loaded to standard out.

        Parameters
        ----------
        name: str
            Property name.
        value: obj
            Property value.

        Returns
        -------
        bool
            Successfulness of adding the property.

        """
        if ConfigurationManager.__config:
            if name not in ConfigurationManager.__config:
                ConfigurationManager.__config[name] = value
                return True
            else:
                print("%s property already in configuration" % name)
                return False
        else:
            print("no configuration loaded")
            return False

    @staticmethod
    def update_property(name, value):
        """
        Assigns new value to existing property.

        Updates a property in the dictionary with a new value, else provides an
        error message detailing that the property does not exist or no
        configuration is loaded to standard out.

        Parameters
        ----------
        name: str
            Property name.
        value: obj
            Property value.

        Returns
        -------
        bool
            Successfulness of updating the property.

        """
        if ConfigurationManager.__config:
            if name in ConfigurationManager.__config:
                ConfigurationManager.__config[name] = value
                return True
            else:
                print("%s property not in configuration" % name)
                return False
        else:
            print("no configuration loaded")
            return False

    @staticmethod
    def remove_property(name):
        """
        Deletes property from current loaded configuration.

        Removes a property from the dictionary. else provides an error message
        detailing the property does not exist or that no configuration has been
        loaded to standard out.

        Parameters
        ----------
        name: str
            Property name.

        Returns
        -------
        bool
            Successfulness of removing the property.

        """
        if ConfigurationManager.__config:
            if name in ConfigurationManager.__config:
                ConfigurationManager.__config.pop(name)
                return True
            else:
                print("%s not loaded in configuration" % name)
                return False
        else:
            print("no configuration loaded")
            return False

    @staticmethod
    def rename_property(old_name, new_name):
        """
        Updates property name in current loaded configuration.

        Associates a property value with a new name, else provides an error
        message detailing that the property does not exist or no configuration
        is loaded to standard out.

        Parameters
        ----------
        old_name: str
            Existing property name.
        new_name: str
            New property name.

        Returns
        -------
        bool
            Successfulness of renaming the property.

        """
        if ConfigurationManager.__config:
            if old_name in ConfigurationManager.__config:
                ConfigurationManager.__config[new_name] = \
                    ConfigurationManager.__config.pop(old_name)
                return True
            else:
                print("%s not loaded in configuration" % old_name)
                return False
        else:
            print("no configuration loaded")
            return False

    @staticmethod
    def get_all_property_names():
        """
        Returns all dictionary keys from currently loaded configuration.

        Retrieves all property names, else provides a message stating no
        configuration is loaded to standard out.

        Returns
        -------
        obj
            All loaded property names or None is no configuration is loaded.

        """
        if ConfigurationManager.__config:
            return ConfigurationManager.__config.keys()
        else:
            print("no configuration loaded")

    @staticmethod
    def clear_properties():
        """
        Removes all properties from current loaded configuration.

        Deletes all property name value pairs from the dictionary, else
        provides a message stating no configuration is loaded to standard out.

        Returns
        -------
        bool
            Successfulness of removing all properties.

        """
        if ConfigurationManager.__config:
            ConfigurationManager.__config = None
            return True
        else:
            print("no configuration loaded")
            return False
