"""Enable registry of JSON schemas which resolves all references.

The main entry point for this module is function
validate_data_against_registry which acts the same way as
metadata_templates.validation.json_validation.validate_data_against_template
by default.


"""

import json
import logging
from collections.abc import Mapping
from importlib.resources import files
from pathlib import Path

from jsonschema import Draft202012Validator, exceptions, FormatChecker
from referencing import Registry, Resource
from referencing import exceptions as exceptsref
from referencing.jsonschema import EMPTY_REGISTRY as _EMPTY_REGISTRY

# There is an exception outside of exceptions, need to capture
from referencing.jsonschema import UnknownDialect

VALID_MESSAGE = "Valid"

default_format_checker = FormatChecker(["date", "email"])

logger = logging.getLogger("__name__")


class RegistryError(Exception):
    """Outer exception for jsonschema and referencing packages"""

    pass


def discover(package: str) -> Path:
    """Python package containing json schemas or subschemas.

    Returns a source path suitable for passing to the
    populate function. A "valid" package must have
    a "sclibrary" folder containing
    a set of json schemas or subschemas that
    can be built into a fully resolved "whole" state which
    validates all $id and $ref statements used within that
    package. Once package is installed there are
    no future dependencies (ie. file or http).
    """
    folder: str = "sclibrary"
    return Path(files(package).joinpath(folder))  # type: ignore[arg-type]


def populate(source: Path, extension: str = "*.json") -> Registry:
    """Create a "whole" json schema from source folder for validating data files."""
    source = Path(source)
    if not source.exists():
        raise FileNotFoundError
    found_files = source.rglob(extension)
    try:
        # The following uses the new @ (added in Python 3.5) and
        # using with yield function seems to obscure what its
        # its doing. PEP465 and Python docs says matrix
        # multiplication. The referencing package points
        # at an example which uses this syntax so little
        # value in finding a different syntax.
        return _load(found_files) @ _EMPTY_REGISTRY.crawl()  # type: ignore[arg-type]
    except (
        # The following are in order they appear in referencing
        # package exceptions module. Not all will occur at this
        # time but leaving here for reference. Those not seen
        # are marked with "not traced" and might be deferred
        # until a call to is_valid() after yielding finishes.
        exceptsref.NoSuchResource,  # Not traced
        exceptsref.NoInternalID,  # $id key is missing from top level
        exceptsref.Unretrievable,  # Not traced
        exceptsref.CannotDetermineSpecification,  # $schema key is missing
        exceptsref.Unresolvable,  # Traced, deferred
        UnknownDialect,  # $schema value is invalid
    ) as err:
        logger.error(err, exc_info=True)
        raise RegistryError(err) from err


def _load(found_files: list[Path]) -> Mapping:  # type: ignore
    for found in found_files:
        try:
            content = json.loads(Path(found).read_text(encoding="utf-8"))
        except json.decoder.JSONDecodeError:
            logger.warning(f"Invalid JSON found, ignored: {found}")
        else:
            # The following will raise exceptions if the
            # json file does not meet minimum requirements. The
            # referencing package does not follow recommended
            # pattern [ie. PackageException(Exception)] so
            # this function leaves it to the caller to
            # capture. The caller can see the 8 exceptions
            # via: import referencing.exceptions as refexcept
            # where refexcept.CannotDetermineSpecification means
            # the "schema" is missing and refexcept.UnknownDialect
            # means "schema" value is not valid.
            yield Resource.from_contents(content)


def validate_data_against_registry(
    metadata: dict,
    schemas_folder: Path,
    root_id: str = "",
) -> tuple[bool, str]:
    """Check metadata is valid with optional silent mode.

    The schemas_folder can contain a single monolithic json
    schema OR smaller reusable pieces (ie. parent $ref = child $id)
    that combine to create a single "whole" schema from
    the validators perspective. Using smaller pieces reduces
    depth of {} in a single file and makes reuse easier.

    The root_id value MUST exist as an $id in one of the JSON
    files in the schema_folder. If missing a warning log
    entry will occur giving a hint. A "whole" schema must
    start with a base $id (parent) since every file in
    the schemas_folder will have an $id that any parent
    can use as a $ref
    """
    if not root_id:
        return False, "Requires an ID root to find the whole schema."
    try:
        loaded = populate(schemas_folder)
    except RegistryError as err:
        return False, str(err)
    try:
        base = loaded.contents(root_id)
    except exceptsref.NoSuchResource as _:
        msg = f'Check --> "$id" : "{root_id}" <-- exists in file within schema folder: {schemas_folder}'  # noqa: E501
        logger.warning(msg)
        return False, msg
    # We need to use the registry within validator so we
    # cannot use "jsonschema.validators.validator_for" as
    # used in other modules.
    check = Draft202012Validator(
        schema=base, registry=loaded, format_checker=default_format_checker
    )
    # The referencing package causes two levels of checking, where
    # the first occurs BEFORE json metadata is seen. The
    # second level is done here. A third level of checking
    # is done by the jonschema package following this block.
    try:
        if check.is_valid(metadata):
            return True, VALID_MESSAGE
    except exceptsref.Unresolvable as err:
        # This exception is caused by referencing BUT as of Dec 2024
        # the object err is WrappedReferencingError from jsonschema
        # which is a _RefResolutionError. Says deprecated
        # since 4.18.0 and capture what we are capturing here. The
        # returned str(err) may need casting removed when wrap goes.
        # https://github.com/python-jsonschema/jsonschema/blob/main/jsonschema/exceptions.py#L235
        msg = f"An $id used in a $ref not found within schema folder: {schemas_folder}"
        logger.warning(msg)
        logger.error(err, exc_info=True)
        return False, str(err)

    # If we reach this point it means the "whole" schema has
    # failed so track down the cause.
    try:
        check.validate(metadata)
        # Like referencing, jsonschema package does not have
        # parent exception. The following are in order as seen
        # in module jsonschema.exceptions
    except (
        exceptions.ValidationError,
        exceptions.SchemaError,
        exceptions.UndefinedTypeCheck,
        exceptions.UnknownType,
        exceptions.FormatError,
    ) as err:
        logger.error(err, exc_info=True)
        return False, err.message

    if True:  # pragma: no cover
        msg = "Unexpected fallthrough occurred, investigate ASAP"
        logger.critical(msg)
        return False, msg
