<!-- cSpell:enable -->
# Fritzing `lint` code

<link href="/home/phil/Documents/data_files/markdown.css" rel="stylesheet"/>

* [here](./)
* [top](/home/phil/index.md)
</br></br>

* [count_parts](#link_count_parts)
* [extract_fz](#link_extract_fz)
* [parse_fzp](#link_parse_fzp)
* parse_fzpz ¦ zip and read svg.«view». prefix as folders

```sh
pipenv install defusedxml
# pipenv install defusedexpat
# failed: no gcc in pipenv toolbox
```

Virtual Box ¦ Fedora 31 Workstation ¦ update 20200727

```sh
% sudo vi /etc/yum.repos.d/vscode.repo
[code]
name=Visual Studio Code
baseurl=https://packages.microsoft.com/yumrepos/vscode
enabled=1
gpgcheck=1\gpgkey=https://packages.microsoft.com/keys/microsoft.asc
% sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
% sudo dnf upgrade --refresh rpm glibc
% sudo dnf -y install gcc libX11-xcb libicu
% sudo dnf install --refresh code
% sudo dnf install pipenv
% mkdir -p ~/development/fritzing-lint
% start sshd
# lybica
# shadow31 continue
% cd ~/development/fritzing-lint
pipenv --three
pipenv install pylint
pipenv install defusedxml
#pipenv install defusedexpat
# fails on vm too
pipenv shell
pylint parse_xml.py

```

lybica

```sh
rsync -a ~/Templates phil@shadow31:
rsync -a $HOME/development/workspace/python/fritzing-lint/*.py phil@shadow31:development/fritzing-lint
rsync -a $HOME/development/workspace/python/fritzing-lint/*.md phil@shadow31:development/fritzing-lint
```

<!--
* [Link](#link_link)
## <a name="link_link">⚓</a> Link
-->

## <a name="link_count_parts">⚓</a> count_parts

Takes command line parameters to specify the path to Fritzing parts library folder, and (optionally) the user data parts folder. Walks the folder trees, matching the nested content to the expected folder structure and file content. Optionally, does the same for the associated svg folder.

Contains the complete structure to walk through the parts folders, and inspect every Fritzing part. That definition files, and all of the linked svg image view files.

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

?incomplete? code to extract .fz (and other) from a .fzz file
-- to be able to manipulate the content using xml tools

## <a name="link_parse_fzp">⚓</a> parse_fzp

Planned python code to load, examine, manipulate the contents of an xml part definition file

Reference: phil#lybica:development/FritzingProjects/FritzingParts/repos/part-parse ¦ dtd

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
