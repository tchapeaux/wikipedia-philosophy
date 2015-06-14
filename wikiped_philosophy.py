import logging
import os
import re
import sys

import requests


class MediaWikiAPIError(Exception):
    pass


class MediaWikiAPIWarning(MediaWikiAPIError):
    pass


def wikipedia_api(params):
    BASE_URL = "http://en.wikipedia.org/w/api.php"
    ACTION = "query"
    FORMAT = "json"
    url = BASE_URL + "?action=" + ACTION + "&" + params + "&format=" + FORMAT
    headers = {'user-agent': 'getting_to_philosophy/0.1 (https://github.com/tchapeaux/wikipedia-philosophy ; chapeauxthomas@gmail.com)'}
    logging.info("GET -- " + url)
    req = requests.get(url, headers=headers)
    resp = req.json()
    if "warnings" in resp:
        raise MediaWikiAPIWarning(resp["warnings"])
    return resp


def getPageContentByTitle(title):
    # First try for a cached version
    try:
        with open("wiki_pages/wiki_"+title.upper()+".txt") as f:
            logging.info("Page taken from cache")
            content = f.read()
    except IOError:
        logging.info("Page not in cache: fetching from MediaWikiAPI")
        PARAMS = "titles={TITLES}&prop=revisions&rvprop=content"
        PARAMS = PARAMS.format(TITLES=title)
        resp = wikipedia_api(PARAMS)
        pages = resp.get("query").get("pages")
        if "-1" in pages:
            raise MediaWikiAPIError("No result for title " + title + "\n" + pages)
        if len(pages) > 1:
            raise MediaWikiAPIError("More than one result for title " + title + "\n" + pages)
        page_id = pages.keys()[0]
        revisions = pages.get(page_id).get("revisions")
        assert len(revisions) == 1, "Not exactly one revision... See for yourself:\n" + str(revisions)
        content = revisions[0]["*"].encode("utf-8")
        with open("wiki_pages/wiki_"+title.upper()+".txt", "w") as f:
            f.write(content)

    if "#REDIRECT" in content.upper():
        matches = re.search("#REDIRECT ?\[\[(.*?)\]\]", content, flags=re.IGNORECASE)
        assert matches is not None, "REDIRECT link with unexpected format: " + content
        new_title = matches.groups()[0]
        logging.info("Redirecting to " + new_title)
        return getPageContentByTitle(new_title)
    return content


def remove_infoboxes(content):
    open_close_mapping = {
        '{': '}',
        '[': ']',
        '<': '>',
    }
    removed = ""
    while content.strip()[0] in open_close_mapping:
        OPEN_SYM = content[0]
        CLOS_SYM = open_close_mapping[OPEN_SYM]
        stack_level = 1  # count nested {} level
        removed += content[0]
        content = content[1:]
        while stack_level > 0:
            first_open = content.find(OPEN_SYM)
            first_close = content.find(CLOS_SYM)
            assert first_close > -1, "Unmatched '" + OPEN_SYM + "' in content\n" + str(content)
            if first_open == -1 or first_close < first_open:
                removed += content[:first_close + 1]
                content = content[first_close + 1:]
                stack_level -= 1
            elif first_open < first_close:
                removed += content[:first_open + 1]
                content = content[first_open + 1:]
                stack_level += 1
            else:
                raise Exception("Invalid state" + content + first_open + first_close)
        content = content.strip()
    removed = removed.replace('\n', '')
    # print "INFO -- Removed", len(removed), "characters: ", removed[:20], "(...)", removed[len(removed)-20:]
    return content


def is_valid_link(link):
    if link is None:
        return False
    for title in titles_sequence:
        if title.upper() == link.upper():
            return False
    if "wikt:" in link or ":wiktionary:" in link:
        return False
    return True


if __name__ == '__main__':
    logging.basicConfig(filename="wikiped_philosophy.log", level=logging.DEBUG)

    if not os.path.exists("wiki_pages"):
        os.makedirs("wiki_pages")

    title = "human"
    titles_sequence = []

    if len(sys.argv) > 1:
        logging.info("First title given by command-line: " + sys.argv[1])
        title = sys.argv[1]
    else:
        logging.info("Using default first title: " + title)

    while title.upper() != "Philosophy".upper():
        print title

        assert title not in titles_sequence, "Loop detected with title " + str(title)
        titles_sequence.append(title)

        logging.info("Accessing page " + str(title))
        content = getPageContentByTitle(title)

        logging.info("Removing infoboxes...")
        content = remove_infoboxes(content)

        # Search first non-visited link
        first_link = None
        while not is_valid_link(first_link):
            first_link_matches = re.search("\[\[(.*?)\]\]", content)  # the ? asks for minimal match
            assert first_link_matches, "No link in first paragraph: " + content
            first_link = first_link_matches.groups()[0]
            if '|' in first_link:
                first_link = first_link.split('|')[0]
            # quick hack: we want this link to be 'disabled', so we replace the first '[[' by something else
            content = content.replace('[[', 'LINKDISABLED:', 1)

        logging.info("First link found: " + str(first_link))

        title = first_link

    logging.info("Final title sequence: " + str(titles_sequence))

    print "Found philosophy in ", len(titles_sequence), "links"
