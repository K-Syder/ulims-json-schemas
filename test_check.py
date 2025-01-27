#!/usr/bin/env python3
import unittest

from typer.testing import CliRunner

from check import app


class TestCheckCLI(unittest.TestCase):

    def setUp(self):
        self.RUNNER = CliRunner()
        self.EXPECTED = "Confirmed files OK in:"
        return super().setUp()

    def test_checkdir(self):
        result = self.RUNNER.invoke(app, ["checkdir"])
        self.assertEqual(result.exit_code, 0)
        found = result.stdout.startswith(self.EXPECTED)
        self.assertTrue(found)

    def test_confirm_base(self):
        result = self.RUNNER.invoke(
            app,
            [
                "confirm",
                "-d",
                "checkdir/datafiles/sample1.json",
                "-s",
                "checkdir/schemas",
                "-c",
                "5",
                "-r",
                "urn:ulims:base:1.0",
            ],
        )
        self.assertEqual(result.exit_code, 0)
        found = result.stdout.startswith(self.EXPECTED)
        self.assertTrue(found)

    def test_confirm_basei07(self):
        result = self.RUNNER.invoke(
            app,
            [
                "confirm",
                "-d",
                "checkdir/datafiles/sample1.json",
                "-s",
                "checkdir/schemas",
                "-c",
                "5",
                "-r",
                "urn:ulims:base:i07:1.0",
            ],
        )
        self.assertEqual(result.exit_code, 0)
        found = result.stdout.startswith(self.EXPECTED)
        self.assertTrue(found)

    def test_invalid_option(self):
        result = self.RUNNER.invoke(app, ["invalid"])
        self.assertEqual(result.exit_code, 2)

    def test_no_datafile(self):
        result = self.RUNNER.invoke(
            app,
            [
                "confirm",
                "-d",
                "checkdir/datafiles/sample2notexisting.json",
                "-s",
                "checkdir/schemas",
                "-c",
                "5",
                "-r",
                "urn:ulims:base:1.0",
            ],
        )
        self.assertEqual(result.exit_code, 1)

    def test_wrong_schemafolder(self):
        result = self.RUNNER.invoke(
            app,
            [
                "confirm",
                "-d",
                "checkdir/datafiles/sample1.json",
                "-s",
                "checkdir/schemas/notexisting",
                "-c",
                "5",
                "-r",
                "urn:ulims:base:1.0",
            ],
        )
        self.assertEqual(result.exit_code, 1)

    def test_confirm_base_wrong_count(self):
        result = self.RUNNER.invoke(
            app,
            [
                "confirm",
                "-d",
                "checkdir/datafiles/sample1.json",
                "-s",
                "checkdir/schemas",
                "-c",
                "6",  # should be 5
                "-r",
                "urn:ulims:base:1.0",
            ],
        )
        self.assertEqual(result.exit_code, 0)
        found = result.stdout.startswith("Number of resources did not match expected value.")
        self.assertTrue(found)

if __name__ == "__main__":
    unittest.main()
