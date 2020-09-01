<!-- cSpell:enable -->
# Fritzing Lint

<link href="css/github_override.css" rel="stylesheet"/>

A set of scripts, process, notes to detect and report problems with Fritzing part files, whether they are part of the core library, in users parts, or from individual part definition files.

See the [github.io index page](https://mmerlin.github.io/fritzing-lint)

* [scenarios](#link_scenarios)

<!--
* [Link](#link_link)
## <a name="link_link">⚓</a> Link
-->

## <a name="link_scenarios">⚓</a> scenarios

* File «set» based reporting
  * all definition files in Fritzing parts library
  * all definition files in user parts library
  * all fzpz files in a folder
  * all fzp files in a folder
  * all parts in a bin
  * part files matching wild card expression
    * fzpz, fzp
  * parts using a specified svg view image file
  * parts filtered by metadata
    * family, tag, title, description, author, more
    * exact or substring match
* missing image files
* orphan image files

## About

python scripts to check for problems in fritzing part files, and the associated svg view files.

<!-- cSpell:disable -->
<!-- cSpell:enable -->
<!--
# cSpell:disable
# cSpell:enable
cSpell:words
cSpell:ignore
cSpell:enableCompoundWords
-->
