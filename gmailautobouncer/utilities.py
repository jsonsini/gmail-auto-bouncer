#!/usr/bin/env python3
"""
Contains utility functions for generic use elsewhere in package.

Group of utility functions including error formatting and concurrent execution
classes.

The nondemonic classes are simple wrappers to create the ability to instantiate
nested concurrent pools of processes.

Notes
-----
Gmail Auto Bouncer is distributed under the GNU Affero General Public License
v3 (https://www.gnu.org/licenses/agpl.html) as open source software with
attribution required.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License v3
(https://www.gnu.org/licenses/agpl.html) for more details.

Copyright (C) 2025 John Sonsini.  All rights reserved.  Source code available
under the AGPLv3.

"""
import multiprocessing.pool


def format_error(error):
    """
    Converts error into one line string representation.

    Extracts the exception type and message from the error to build a simple
    string summarizing the information to be used when logging.

    Parameters
    ----------
    error : tuple
        Exception type, exception message, and traceback information.

    Returns
    -------
    str
        Formatted version of error with type and message.

    """
    return "%s %s" % (error[0].__name__, error[1])


class NonDaemonicProcess(multiprocessing.Process):
    """
    Process class limited to non daemonic state.

    Extension of multiprocessing.Process with the daemon property modified to
    return false in all cases.

    """

    @property
    def daemon(self):
        """boolean: Explicitly restrict processes to be nondaemonic."""
        return False

    @daemon.setter
    def daemon(self, value):
        pass


class NonDaemonicContext(type(multiprocessing.get_context())):
    """
    Minimal context wrapping nondaemonic processes.

    Multiprocessing context that uses the NonDaemonicProcess class to create a
    pool containing only nondaemonic processes.

    """

    Process = NonDaemonicProcess
    """obj: Processes for pool limited to nondaemonic state."""


class NonDaemonicPool(multiprocessing.pool.Pool):
    """
    Minimal pool wrapping nondaemonic processes.

    Extension of multiprocessing.pool.Pool that uses the NonDaemonContext
    class to create a nestable pool containing only nondaemonic processes.

    """

    def __init__(self, *args, **kwargs):
        """
        Prepares all needed instance variables for execution.

        Adds the nondemonic context to allow for nesting of pools.

        """
        kwargs["context"] = NonDaemonicContext()
        super(NonDaemonicPool, self).__init__(*args, **kwargs)


if __name__ == '__main__':
    pass
