#!/usr/bin/env python3
"""Test the vlan module."""

import os
import sys
import unittest
import random

# Try to create a working PYTHONPATH
EXEC_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(
    os.path.join(
        os.path.abspath(
            os.path.join(
                os.path.abspath(
                    os.path.join(
                        os.path.abspath(
                            os.path.join(
                                os.path.abspath(
                                    os.path.join(EXEC_DIR, os.pardir)
                                ),
                                os.pardir,
                            )
                        ),
                        os.pardir,
                    )
                ),
                os.pardir,
            )
        ),
        os.pardir,
    )
)
_EXPECTED = """\
{0}switchmap-ng{0}tests{0}switchmap_{0}server{0}db{0}table""".format(
    os.sep
)
if EXEC_DIR.endswith(_EXPECTED) is True:
    # We need to prepend the path in case the repo has been installed
    # elsewhere on the system using PIP. This could corrupt expected results
    sys.path.insert(0, ROOT_DIR)
else:
    print(
        """This script is not installed in the "{0}" directory. Please fix.\
""".format(
            _EXPECTED
        )
    )
    sys.exit(2)


# Create the necessary configuration to load the module
from tests.testlib_ import setup

CONFIG = setup.config()
CONFIG.save()

from switchmap.server.db.table import vlan as testimport
from switchmap.server.db.models import Vlan
from switchmap.server.db.table import IVlan
from switchmap.server.db import models

from tests.testlib_ import db
from tests.testlib_ import data


class TestDbTableVlan(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    @classmethod
    def setUpClass(cls):
        """Execute these steps before starting tests."""
        # Load the configuration in case it's been deleted after loading the
        # configuration above. Sometimes this happens when running
        # `python3 -m unittest discover` where another the tearDownClass of
        # another test module prematurely deletes the configuration required
        # for this module
        config = setup.config()
        config.save()

        # Create database tables
        models.create_all_tables()

        # Pollinate db with prerequisites
        db.populate()

    @classmethod
    def tearDownClass(cls):
        """Execute these steps when all tests are completed."""
        # Drop tables
        database = db.Database()
        database.drop()

        # Cleanup the
        CONFIG.cleanup()

    def test_idx_exists(self):
        """Testing function idx_exists."""
        # Create record
        row = _row()

        # Test before insertion of an initial row
        nonexistent = testimport.exists(row.idx_device, row.vlan)
        self.assertFalse(nonexistent)

        # Test after insertion of an initial row
        testimport.insert_row(row)
        preliminary_result = testimport.exists(row.idx_device, row.vlan)
        self.assertTrue(preliminary_result)
        self.assertEqual(_convert(preliminary_result), _convert(row))

        # Test idx_index function
        result = testimport.idx_exists(preliminary_result.idx_vlan)
        self.assertTrue(result)
        self.assertEqual(_convert(result), _convert(preliminary_result))

    def test_exists(self):
        """Testing function exists."""
        # Create record
        row = _row()

        # Test before insertion of an initial row
        result = testimport.exists(row.idx_device, row.vlan)
        self.assertFalse(result)

        # Test after insertion of an initial row
        testimport.insert_row(row)
        result = testimport.exists(row.idx_device, row.vlan)
        self.assertTrue(result)
        self.assertEqual(_convert(result), _convert(row))

    def test_vlans(self):
        """Testing function vlans."""
        # Initialize key variables
        maximum = 10

        # Create record
        row = _row()

        # Test before insertion of an initial row
        result = testimport.exists(row.idx_device, row.vlan)
        self.assertFalse(result)

        # Get existing values
        inserts = testimport.vlans(row.idx_device)
        start = len(inserts)
        stop = start + maximum

        # Insert `maximum` values
        for _ in range(stop - start):
            # Create record
            row = _row()

            # Test before insertion of an initial row
            result = testimport.exists(row.idx_device, row.vlan)
            self.assertFalse(result)

            # Test after insertion of an initial row
            testimport.insert_row(row)
            result = testimport.exists(row.idx_device, row.vlan)
            self.assertTrue(result)

            # Update list of values inserted
            inserts.append(result)

        # Test
        results = testimport.vlans(row.idx_device)
        results.sort(key=lambda x: (x.vlan))
        inserts.sort(key=lambda x: (x.vlan))

        # Test the length of the results
        self.assertEqual(len(results), stop)
        self.assertEqual(len(inserts), stop)

        for key, result in enumerate(results):
            self.assertEqual(_convert(result), _convert(inserts[key]))

    def test_insert_row(self):
        """Testing function insert_row."""
        # Create record
        row = _row()

        # Test before insertion of an initial row
        result = testimport.exists(row.idx_device, row.vlan)
        self.assertFalse(result)

        # Test after insertion of an initial row
        testimport.insert_row(row)
        result = testimport.exists(row.idx_device, row.vlan)
        self.assertTrue(result)
        self.assertEqual(_convert(result), _convert(row))

    def test_update_row(self):
        """Testing function update_row."""
        # Create record
        row = _row()

        # Test before insertion of an initial row
        result = testimport.exists(row.idx_device, row.vlan)
        self.assertFalse(result)

        # Test after insertion of an initial row
        testimport.insert_row(row)
        result = testimport.exists(row.idx_device, row.vlan)
        self.assertTrue(result)
        self.assertEqual(_convert(result), _convert(row))

        # Do an update
        idx = result.idx_vlan
        updated_row = Vlan(
            idx_device=row.idx_device,
            vlan=random.randint(0, 1000000),
            name=data.random_string(),
            state=row.state,
            enabled=row.enabled,
        )
        testimport.update_row(idx, updated_row)

        # Test the update
        result = testimport.exists(updated_row.idx_device, updated_row.vlan)
        self.assertTrue(result)
        self.assertEqual(_convert(result), _convert(updated_row))

    def test__row(self):
        """Testing function _row."""
        # This function is tested by all the other tests
        pass


def _convert(row):
    """Convert RVlan to IVlan record.

    Args:
        row: RVlan/IVlan record

    Returns:
        result: IVlan result

    """
    # Do conversion
    result = IVlan(
        idx_device=row.idx_device,
        vlan=row.vlan,
        name=row.name,
        state=row.state,
        enabled=row.enabled,
    )
    return result


def _row():
    """Create an IVlan record.

    Args:
        None

    Returns:
        result: IVlan object

    """
    # Create result
    result = IVlan(
        idx_device=1,
        vlan=random.randint(0, 1000000),
        name=data.random_string(),
        state=random.randint(0, 1000000),
        enabled=1,
    )
    return result


if __name__ == "__main__":
    # Do the unit test
    unittest.main()