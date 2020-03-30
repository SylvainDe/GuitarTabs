import html as htmlmodule

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
    return htmlmodule.escape(s, quote=True)


class HtmlGroup(object):

    def __init__(self, *iterable):
        self.elts = tuple(iterable)

    def __str__(self):
        return "".join(str(e) for e in self.elts)


class HtmlTag(object):
    def __init__(self, tag, content=None, on_open="", on_close="", attrs=None, **kwargs):
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

    def __str__(self):
        attrs = "".join(" " + k + ("" if v is None else "=\"%s\"" % v)
                        for k, v in self.attrs.items())
        if self.content is None:
            closing = " />"
        else:
            content = "".join(str(elt) for elt in self.content)
            closing = ">%s%s</%s>" % (self.on_open, content, self.tag)
        return "<%s%s%s%s" % (self.tag, attrs, closing, self.on_close)

    def __add__(self, other):
        return HtmlGroup(self, other)


def h(level, content=None, attrs=None, **kwargs):
    return HtmlTag(tag="h" + str(level), content=content, attrs=attrs, **kwargs, on_close="\n")


def a(content=None, attrs=None, **kwargs):
    return HtmlTag(tag="a", content=content, attrs=attrs, **kwargs)


def pre(content=None, attrs=None, **kwargs):
    return HtmlTag(tag="pre", content=content, attrs=attrs, **kwargs, on_close="\n")


def link(content=None, attrs=None, **kwargs):
    return HtmlTag(tag="link", content=content, attrs=attrs, **kwargs, on_close="\n")


def title(content=None, attrs=None, **kwargs):
    return HtmlTag(tag="title", content=content, attrs=attrs, **kwargs, on_close="\n")


def meta(content=None, attrs=None, **kwargs):
    return HtmlTag(tag="meta", content=content, attrs=attrs, **kwargs, on_close="\n")


def html(content=None, attrs=None, **kwargs):
    return HtmlTag(tag="html", content=content, attrs=attrs, **kwargs, on_close="\n", on_open="\n")


def head(content=None, attrs=None, **kwargs):
    return HtmlTag(tag="head", content=content, attrs=attrs, **kwargs, on_close="\n", on_open="\n")


def body(content=None, attrs=None, **kwargs):
    return HtmlTag(tag="body", content=content, attrs=attrs, **kwargs, on_close="\n", on_open="\n")


def comment(string):
    return "<!-- %s -->\n" % string

doctype = "<!DOCTYPE html>\n"
pagebreak = HtmlTag(tag="mbp:pagebreak", on_close="\n")
new_line = HtmlTag(tag="br", on_close="\n")
