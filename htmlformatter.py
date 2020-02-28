import html as htmlmodule

def string_to_html_id(s):
    return htmlmodule.escape(s, quote=True)

def generic_tag(tag, content=None, on_open="", on_close="", **kwargs):
    attrs = "".join(" %s=\"%s\"" % (k, v) for k, v in kwargs.items() if v is not None)
    closing = " />" if content is None else ">%s%s</%s>" % (on_open, content, tag)
    return "<%s%s%s%s" % (tag, attrs, closing, on_close)

def h(level, content=None, **kwargs):
    return generic_tag(tag="h" + str(level), content=content, **kwargs, on_close="\n")

def a(content=None, **kwargs):
    return generic_tag(tag="a", content=content, **kwargs)

def pre(content=None, **kwargs):
    return generic_tag(tag="pre", content=content, **kwargs, on_close="\n")

def link(content=None, **kwargs):
    return generic_tag(tag="link", content=content, **kwargs, on_close="\n")

def title(content=None, **kwargs):
    return generic_tag(tag="title", content=content, **kwargs, on_close="\n")

def meta(content=None, **kwargs):
    return generic_tag(tag="meta", content=content, **kwargs)

def html(content=None, **kwargs):
    return generic_tag(tag="html", content=content, **kwargs, on_close="\n", on_open="\n")

def head(content=None, **kwargs):
    return generic_tag(tag="head", content=content, **kwargs, on_close="\n", on_open="\n")

def body(content=None, **kwargs):
    return generic_tag(tag="body", content=content, **kwargs, on_close="\n", on_open="\n")

doctype = "<!DOCTYPE html>\n"
pagebreak = generic_tag(tag="mbp:pagebreak", on_close="\n")
new_line = generic_tag(tag="br", on_close="\n")

