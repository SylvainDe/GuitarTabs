import html as htmlmodule
import urllib.parse
import re

# TODO: Consider other options:
# From https://stackoverflow.com/questions/1548474/python-html-generator :
# - http://karrigell.sourceforge.net/en/htmltags.html
# - https://github.com/Knio/dominate
# From https://stackoverflow.com/questions/48064631/how-to-generate-a-static-html-with-python :
# - https://pypi.org/project/html/
# - https://www.yattag.org/
# From https://stackoverflow.com/questions/6748559/generating-html-documents-in-python :
# - https://www.yattag.org/
# From https://stackoverflow.com/questions/3887393/what-python-html-generator-module-should-i-use-in-a-non-web-application :
# - https://github.com/Yelp/PushmasterApp/blob/master/pushmaster/taglib.py


def string_to_html_id(s):
    # return htmlmodule.escape(s, quote=True)
    regex = re.compile('[^a-zA-Z0-9_-]')
    return regex.sub('_', s)

def encode_uri(uri):
    return urllib.parse.quote(uri, safe="/:")

class HtmlGroup(object):
    def __init__(self, *iterable):
        self.elts = tuple(iterable)

    def __str__(self):
        return "".join(str(e) for e in self.elts)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.elts == other.elts


class HtmlTag(object):

    empty_elements = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "keygen",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
        "mbp:pagebreak",
    }

    def __init__(
        self, tag, content=None, on_open="", on_close="", attrs=None, **kwargs
    ):
        self.tag = tag
        self.attrs = dict()
        if attrs:
            self.attrs.update(attrs)
        if kwargs:
            self.attrs.update(kwargs)
        self.content = None if content is None else [content]
        self.on_open = on_open
        self.on_close = on_close

    def add(self, elt):
        if self.content is None:
            self.content = [elt]
        else:
            self.content.append(elt)
        return self

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.tag == other.tag
            and self.attrs == other.attrs
            and self.content == other.content
            and self.on_open == other.on_open
            and self.on_close == other.on_close
        )

    def __str__(self):
        attrs = "".join(
            " " + k + ("" if v is None else '="%s"' % v) for k, v in self.attrs.items()
        )
        content = self.content
        if content is None and self.tag in self.empty_elements:
            closing = " />"
        else:
            content = [] if content is None else content
            content = "".join(str(elt) for elt in content)
            closing = ">%s%s</%s>" % (self.on_open, content, self.tag)
        return "<%s%s%s%s" % (self.tag, attrs, closing, self.on_close)

    def __add__(self, other):
        return HtmlGroup(self, other)


def heading(level, content=None, attrs=None, **kwargs):
    return HtmlTag(
        tag="h" + str(level), content=content, attrs=attrs, **kwargs, on_close="\n"
    )


def a(content=None, attrs=None, **kwargs):
    return HtmlTag(tag="a", content=content, attrs=attrs, **kwargs)


def pre(content=None, attrs=None, **kwargs):
    return HtmlTag(tag="pre", content=content, attrs=attrs, **kwargs, on_close="\n")


def link(content=None, attrs=None, **kwargs):
    return HtmlTag(tag="link", content=content, attrs=attrs, **kwargs, on_close="\n")


def title(content=None, attrs=None, **kwargs):
    return HtmlTag(tag="title", content=content, attrs=attrs, **kwargs, on_close="\n")


def li(content=None, attrs=None, **kwargs):
    return HtmlTag(tag="li", content=content, attrs=attrs, **kwargs, on_close="\n")


def ul(content=None, attrs=None, **kwargs):
    return HtmlTag(
        tag="ul", content=content, attrs=attrs, **kwargs, on_close="\n", on_open="\n"
    )


def meta(content=None, attrs=None, **kwargs):
    return HtmlTag(tag="meta", content=content, attrs=attrs, **kwargs, on_close="\n")


def html(content=None, attrs=None, **kwargs):
    return HtmlTag(
        tag="html", content=content, attrs=attrs, **kwargs, on_close="\n", on_open="\n"
    )


def head(content=None, attrs=None, **kwargs):
    return HtmlTag(
        tag="head", content=content, attrs=attrs, **kwargs, on_close="\n", on_open="\n"
    )


def body(content=None, attrs=None, **kwargs):
    return HtmlTag(
        tag="body", content=content, attrs=attrs, **kwargs, on_close="\n", on_open="\n"
    )


def comment(string):
    return "<!-- %s -->\n" % string


doctype = "<!DOCTYPE html>\n"
new_line = HtmlTag(tag="br", on_close="\n")
if True:
    pagebreak = HtmlTag(tag="div", attrs={"style": "break-after:page"}, on_close="\n")
else:
    pagebreak = HtmlTag(tag="mbp:pagebreak", on_close="\n")
