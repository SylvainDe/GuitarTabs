import html as htmlmodule

def string_to_html_id(s):
    return htmlmodule.escape(s, quote=True)

def generic_tag(tag, content=None, on_open="", on_close="", attrs=None, **kwargs):
    attrs_used = dict() if attrs is None else attrs.copy()
    if kwargs:
         attrs_used.update(kwargs)
    attrs_str = "".join(" %s=\"%s\"" % (k, v) for k, v in attrs_used.items() if v is not None)
    closing = " />" if content is None else ">%s%s</%s>" % (on_open, content, tag)
    return "<%s%s%s%s" % (tag, attrs_str, closing, on_close)

def h(level, content=None, attrs=None, **kwargs):
    return generic_tag(tag="h" + str(level), content=content, attrs=attrs, **kwargs, on_close="\n")

def a(content=None, attrs=None, **kwargs):
    return generic_tag(tag="a", content=content, attrs=attrs, **kwargs)

def pre(content=None, attrs=None, **kwargs):
    return generic_tag(tag="pre", content=content, attrs=attrs, **kwargs, on_close="\n")

def link(content=None, attrs=None, **kwargs):
    return generic_tag(tag="link", content=content, attrs=attrs, **kwargs, on_close="\n")

def title(content=None, attrs=None, **kwargs):
    return generic_tag(tag="title", content=content, attrs=attrs, **kwargs, on_close="\n")

def meta(content=None, attrs=None, **kwargs):
    return generic_tag(tag="meta", content=content, attrs=attrs, **kwargs, on_close="\n")

def html(content=None, attrs=None, **kwargs):
    return generic_tag(tag="html", content=content, attrs=attrs, **kwargs, on_close="\n", on_open="\n")

def head(content=None, attrs=None, **kwargs):
    return generic_tag(tag="head", content=content, attrs=attrs, **kwargs, on_close="\n", on_open="\n")

def body(content=None, attrs=None, **kwargs):
    return generic_tag(tag="body", content=content, attrs=attrs, **kwargs, on_close="\n", on_open="\n")

doctype = "<!DOCTYPE html>\n"
pagebreak = generic_tag(tag="mbp:pagebreak", on_close="\n")
new_line = generic_tag(tag="br", on_close="\n")

