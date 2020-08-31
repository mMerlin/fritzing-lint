<!-- cSpell:enable -->
# Fritzing `lint` code

<link href="css/github_override.css" rel="stylesheet"/>

This a project to provide a tool to check for issues in fritzing part files. It (eventually) should be able to examine libraries, bins, individual parts, fzpz files, and even parts embedded in sketch files. To start, it is only looking at parts contained in the standard Fritzing Parts library structure. That is either a regular parts library, or the user parts library.

This is intended to be extremely picky. Like the programming language linting tools, not everything it reports is going to be a real problem. It reports things that should be looked at, and *deliberate* choices made about whether the suspicious condition is valid for the specific part and context. What it reports will (in the future) be able to be controlled by configuration settings and command line flags.

This is a work in progress, so development notes will be found throughout. It is not (yet) intended for plug and play usage for casual Fritzing parts creators. Initially it is expected to be used by the main Fritzing parts library maintainers, to triage cleanup.

* [README](README.md)
* [count_parts](#link_count_parts)
* [extract_fz](#link_extract_fz)
* [parse_fzp](#link_parse_fzp)
* parse_fzpz ¦ zip and read svg.«view». prefix as folders

```sh
pipenv install defusedxml
```

<!--
* [Link](#link_link)
## <a name="link_link">⚓</a> Link
-->

## <a name="link_count_parts">⚓</a> count_parts

Takes command line parameters to specify the path to a Fritzing parts library folder, and (optionally) the user data parts folder. Walks the folder trees, matching the nested content to the expected folder structure and file content. Optionally, does the same for the associated svg folder.

Contains the complete structure to walk through the parts folders, and inspect every Fritzing part. The definition files, and all of the linked svg image view files.

Remove the count reporting, and add a call to the «fzp¦svg» xml processing method

* root folder
  * «part source folder» «core¦user¦contrib¦obsolete»
    * «part definition files» «.fzp»
  * svg
    * «part source folder» «core¦user¦contrib¦obsolete»
      * «view folder» «breadboard¦icon¦pcb¦schematic»
        * «part view image files» «.svg»

```txt
Fritzing part counter

positional arguments:
  Part Library          path to top folder for Fritzing Parts library

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -u user-parts, --user user-parts
                        path to folder containing user parts
  -v, --verbose         increase verbosity
  -e, --exceptions      report exceptions while counting
  -s, --svg             report svg image file counts
```

## <a name="link_extract_fz">⚓</a> extract_fz

?incomplete? code to extract .fz (and other content) from a .fzz file
-- to be able to manipulate the content using xml tools

## <a name="link_parse_fzp">⚓</a> parse_fzp

Planned python code to load, examine, manipulate the contents of an xml part definition file

Reference: phil#lybica:development/FritzingProjects/FritzingParts/repos/part-parse ¦ dtd

* [Notes](#link_parse_notes)

```sh
pipenv install defusedxml
pipenv install defusedexpat
```

Initially:

* get svg view images and layerids
* validate xml data structure
* validate existence of fzp elements and attributes

Will need matching code for processing svg documents. Initial searches are find python libraries to **write** svg, not to read/parse it. Something more than base xml parsing could be useful. svglib is targeted to format conversion.

references

[ElementTree](http://docs.python.org/library/xml.etree.elementtree.html), lxml, cElementTree
xpath
xmltodict «OrderedDict does not handle duplicate keys, which a lot of (bad) xml contains: contrary information says the duplicates become a list»

from memory, a replacement/patch/overlay to ElementTree to address security concerns around malformed xml documents
-- defusedxml defusedexpat

```py
import xml.etree.ElementTree as ET
root = EG.parse('filepath.xml').getroot()
```

### <a name="link_parse_notes">⚓</a> Parsing notes

add a sanity check to the `<label>` tag content. Should be short, no spaces, very limited punctuation.

Add check for leading or trailing whitespace for other elements (description)

Several references seen to `<DefaultUnits>` element. Does Fritzing actually used it, and how?

Many references to "unknown" view layer name. Is it special somehow?

several 'board' layer id values for pcb. Is that another special meaning? For parts that only have a pcb view.

Ignore some errors for obsolete parts (obsolete folder, and obsolete family). Many exception cases are not going to be fixed in obsolete. The issue might be why it is in obsolete in the first place. If fixing the exception would require the obsolete process, don't bother reporting it. Or drop it to 'informational' severity.
-- bad_layer4image
-- bad_bb_layer
-- bb_no_bb_path

## functional comment block

Header prevents the comments here from being hidden if the previous block is folded in the editor

<!-- cSpell:disable -->
<!-- cSpell:enable -->
<!--
# cSpell:disable
# cSpell:enable
cSpell:words
cSpell:ignore
cSpell:enableCompoundWords
-->
