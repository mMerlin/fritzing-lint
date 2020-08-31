<!-- cSpell:enable -->
# lint reported

<link href="css/github_override.css" rel="stylesheet"/>

«Some of» the part file lint reported, with reasons that the condition is likely undesired.

* [Empty Family Property](#link_empty_family)
* [Not Child Element](#link_not_child)

To Be Continued

<!--
* [Link](#link_link)
## <a name="link_link">⚓</a> Link
-->

## <a name="link_empty_family">⚓</a> Empty Family Property

Every Fritzing part should have a property element, with a name of "family", that contains a name. This is what Fritzing Inspector uses as the base to offer other parts that might be replacements for the current part. A blank family name means that either no part can every be offered as an alternative, or that any other part with a blank family will be available.

lint type: Fritzing functionality

## <a name="link_not_child">⚓</a> Not Child Element

A xml element was found with a tag that is not part of the Fritzing part definition format, at least for the context it was found in. Fritzing is not going to process the element. It may have a misspelled tag name, or it might be in the wrong location in the file.

lint type: xmd data structure error

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
