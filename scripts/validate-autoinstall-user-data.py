#!/usr/bin/env python3

# Copyright 2022 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Validate autoinstall-user-data against the autoinstall schema.

By default, we are expecting the autoinstall user-data to be wrapped in a cloud
config format. Example:

    #cloud-config
    autoinstall:
      <user data comes here>

To validate the user-data directly, you can pass the --no-expect-cloudconfig
switch.
"""

import argparse
import io
import json
from argparse import Namespace
from typing import Any

import jsonschema
import yaml

DOC_LINK: str = (
    "https://canonical-subiquity.readthedocs-hosted.com/en/latest/reference/autoinstall-reference.html"  # noqa: E501
)


SUCCESS_MSG: str = "Success: The provided autoinstall config validated successfully"
FAILURE_MSG: str = "Failure: The provided autoinstall config failed validation"


def verify_link(data: str) -> bool:
    """Verify the autoinstall doc link is in the generated user-data."""

    return DOC_LINK in data


def parse_cloud_config(data: str) -> dict[str, Any]:
    """Parse cloud-config and extra autoinstall data."""

    # "#cloud-config" header is required for cloud-config data
    first_line: str = data.splitlines()[0]
    if not first_line == "#cloud-config":
        raise AssertionError(
            (
                "Expected data to be wrapped in cloud-config "
                "but first line is not '#cloud-config'. Try "
                "passing --no-expect-cloudconfig."
            )
        )

    cc_data: dict[str, Any] = yaml.safe_load(data)

    # "autoinstall" top-level keyword is required in cloud-config delivery case
    if "autoinstall" not in cc_data:
        raise AssertionError(
            (
                "Expected data to be wrapped in cloud-config "
                "but could not find top level 'autoinstall' "
                "key."
            )
        )
    else:
        return cc_data["autoinstall"]


def parse_autoinstall(user_data: str, expect_cloudconfig: bool) -> dict[str, Any]:
    """Parse stringified user_data and extract autoinstall data."""

    if expect_cloudconfig:
        return parse_cloud_config(user_data)
    else:
        return yaml.safe_load(user_data)


def legacy_verify(ai_data: dict[str, Any], json_schema: io.TextIOWrapper) -> None:
    """Legacy verification method for use in CI"""

    jsonschema.validate(ai_data, json.load(json_schema))


def parse_args() -> Namespace:
    """Parse argparse arguments."""

    parser = argparse.ArgumentParser(
        prog="validate-autoinstall-user-data",
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "input",
        nargs="?",
        help="Path to the user data instead of stdin",
        type=argparse.FileType("r"),
        default="-",
    )
    parser.add_argument(
        "--no-expect-cloudconfig",
        dest="expect_cloudconfig",
        action="store_false",
        help="Assume the data is not wrapped in cloud-config.",
        default=True,
    )

    # Hidden validation path we use in CI until the new validation method
    # is ready. i.e. continue to validate based on the json schema directly.
    parser.add_argument(
        "--json-schema",
        help=argparse.SUPPRESS,
        type=argparse.FileType("r"),
        default="autoinstall-schema.json",
    )

    parser.add_argument(
        "--legacy",
        action="store_true",
        help=argparse.SUPPRESS,
        default=False,
    )

    return parser.parse_args()


def main() -> None:
    """Entry point."""

    args: Namespace = parse_args()

    str_user_data: str = args.input.read()

    # Verify autoinstall doc link is in the file

    assert verify_link(str_user_data), "Documentation link missing from user data"

    # Verify autoinstall schema

    try:

        ai_user_data: dict[str, Any] = parse_autoinstall(
            str_user_data, args.expect_cloudconfig
        )
    except Exception as exc:
        print(f"FAILURE: {exc}")
        return 1

    if args.legacy:
        legacy_verify(ai_user_data, args.json_schema)

    print(SUCCESS_MSG)


if __name__ == "__main__":
    main()
