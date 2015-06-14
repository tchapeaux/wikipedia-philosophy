This scripts demonstrates that [by recursively clicking on the first link of any Wikipedia page, you eventually arrive at the *Philosophy* page](https://en.wikipedia.org/wiki/Wikipedia:Getting_to_Philosophy).

[Relevant xkcd](http://xkcd.com/903/) (see title text of the comic)

## Dependencies

The [request](http://docs.python-requests.org/en/latest/) Python library must be installed.

## Usage

Call it as any Python script:
`python wikiped_philosophy (start point)`

`(start point)` can be any title of an existing page

## Example output
    > python wikiped_philosophy.py "Knowledge"
    Knowledge
    awareness
    conscious
    Quality (philosophy)
    Found philosophy in 4 links

    > python wikiped_philosophy.py "belgian fries"
    belgian fries
    Comparison of American and British English
    British English
    [...]  # skip skip
    cylinder (geometry)
    surface
    mathematics
    quantity
    property (philosophy)
    modern philosophy
    Found philosophy in 38 links


## More details

The script uses the [MediaWiki API](https://www.mediawiki.org/wiki/API:Main_page) to access article pages.

The details rules for choosing each successive link are:
- Pages are fetched on the English language Wikipedia
- Ignore everything before the first paragraph (infoboxes and such)
- Already visited links are skipped
- Subsections are ignored (the main article is used instead)
- Redirection pages are always followed

## TODO

    Dans ses écrits, un sage Italien
    Dit que le mieux est l'ennemi du bien.
                        -- Voltaire

This script seems quite good "as is" to me! It will probably not get updated much further. However some people are perfectionist and they might like the script to:
- Handle other languages Wikipedias
- Handle non-existent titles better (now it just crashes)
- Remove "etymology" links (not really interesting)
- Add "random first article" option
- Have command-line arguments to enable/disable caching (it is enabled by default)
