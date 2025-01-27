# ULIMS JSON schemas

A collection of whole or partial JSON schemas.

## Available schemas
* checkdir - An example of JSON schemas that build from
sets of JSON schemas, which validate data files. Provides
repo self-testing with minimal depencencies.
 
## Checking schemas and datafiles are okay

The check.py module provides a CLI to make it easier
to confirm JSON schemas and sample datafile are valid. Use
--help to see commands and options. It uses a local copy
of the registry.py module from an unpublished package.

## CLI Usage
* Create and activate virtenv. The following will prompt to install
  required packages: * ./install.sh or manually *pip install jsonschema typer*

* Confirm example schemas and datafile sample are
  still "good" using: ./check.py checkdir

### Break schema(s) or data files
The CLI does minimal capture so requires users to interpret
the output when it fails. Use the checkdir folder and
command to see how change alters the error message.

 *Make one change in checkdir folder and run: ./check.py checkdir

For example, editing checkdir/schemas/base.json and
changing scan $ref (line 21) to a schema that does not
exist will result in "Unresolvable: urn:ulims:scanschnoexist:1.0"
error. Fix typo OR create as new schema file in schemas
where the $id within MUST match $ref unresolved. In this case,
the correct $ref is the $id in checkdir/schemas/scan.json

## Checking a custom folder
All schemas should be kept in a custom folder with two subfolders
like checkdir. Ideally, a large schema will be broken down
into smaller schemas so fragments can be reused. A datafile
sample should exist which is known to pass at commit time
of any file in schemas folder.

Custom folders can be checked with: ./check.py confirm <options>

The checkdir command above is calling this confirm command
with these options. Use confirm --help to see short
and long options mean.

./check.py confirm -d checkdir/datafiles/sample1.json -s checkdir/schemas -c 5 -r "urn:ulims:base:1.0"

### Multiple roots in schema folder
The checkdir example has multiple schema roots which reuse
smaller schemas. In this case, the sample file validates
to both schemas because nothing was unique for instrument. Notice
-r is now an instrument root.
./check.py confirm -d checkdir/datafiles/sample1.json -s checkdir/schemas -c 5 -r "urn:ulims:base:i07:1.0"

### Adding CLI shortcut to custom folder.
Adding a CLI shortcut like checkdir is suggested if you use the
confirm often and the schema is expected to be used for more
than 6 months. Also, add to the list of available schemas
at start of this document.


## Single file schemas
The checkdir example breaks a large schema into smaller schemas,
but requires use of a registry to cache all schema $id. The
smaller schemas can be added as "definitions" in a single
schema file. The effect will be to hard code so reuse
more difficult, but some applications might require this.
