import datetime
import subprocess
import itertools
import pathlib
import htmlformatter as HtmlFormatter
import sys

from tabs import AbstractGuitarTab as Tab
from chords import Chord


# https://kdp.amazon.com/en_US/help/topic/G200673180 "Supported HTML Tags in Book Content "
# http://www.amazon.com/kindleformat/kindlegen
KINDLEGEN_PATH = 'Kindlegen/kindlegen'

# TODO: Handle path in a smart way: the path in the code should be the relative
# path in the repo but the path in the generated html code should be relative to
# the html file.
CSS_FILE="default.css"
COVER_FILE="empty.jpg"

def my_groupby(iterable, key=None):
    return itertools.groupby(sorted(iterable, key=key), key=key)


def get_html_head(title):
    return HtmlFormatter.head()\
        .add(HtmlFormatter.meta(attrs={'http-equiv': "Content-type", 'content': "text/html;charset=utf-8"}))\
        .add(HtmlFormatter.meta(attrs={'name': "cover", 'content': COVER_FILE}))\
        .add(HtmlFormatter.title(content=title))\
        .add(HtmlFormatter.link(rel="stylesheet", href=CSS_FILE, type="text/css"))


def get_html_body(title, tabs, chords):
    # Ensure consistent ordering
    tabs.sort(key=Tab.by_name_and_url)
    chords.sort(key=Chord.by_name)
    show_titles_in_toc = True
    show_chords_in_toc = False
    heading = HtmlFormatter.heading
    link = HtmlFormatter.a
    body = HtmlFormatter.body()
    # Header
    body.add(heading(1, title))
    body.add("Generated on the %s with '%s'\n" %
                (datetime.datetime.now(),
                " ".join(sys.argv)))
    body.add(HtmlFormatter.pagebreak)
    # Table of content
    body.add(link(id="TOC"))
    body.add("\n")
    body.add(heading(2, "Table of contents"))
    body.add(heading(3, link(href="#tabs", content="Tabs")))
    if show_titles_in_toc:
        for t in tabs:
            body.add(t.get_link())
            body.add(HtmlFormatter.new_line)
    body.add(heading(3, link(href="#chords", content="Chords")))
    if show_chords_in_toc:
        for c in chords:
            body.add(c.get_link(display_type=True))
            body.add(HtmlFormatter.new_line)
    body.add(heading(3, link(href="#index_tabs", content="Tab Index")))
    if not show_titles_in_toc:
        body.add(link(href="#index_tabs_by_title", content="Tabs by title"))
        body.add(HtmlFormatter.new_line)
    body.add(link(href="#index_tabs_by_artist", content="Tabs by artist"))
    body.add(HtmlFormatter.new_line)
    body.add(link(href="#index_tabs_by_diff", content="Tabs by difficulty"))
    body.add(HtmlFormatter.new_line)
    body.add(link(href="#index_tabs_by_type", content="Tabs by type"))
    body.add(HtmlFormatter.new_line)
    body.add(link(href="#index_tabs_by_src", content="Tabs by website"))
    body.add(HtmlFormatter.new_line)
    body.add(HtmlFormatter.pagebreak)
    body.add(heading(3, link(href="#index_chords", content="Chord Index")))
    if not show_chords_in_toc:
        body.add(link(href="#index_chords_by_title", content="Chords by name"))
        body.add(HtmlFormatter.new_line)
    body.add(link(href="#index_chords_by_type", content="Chords by type"))
    body.add(HtmlFormatter.new_line)
    body.add(link(name="start"))
    body.add("\n")
    # Tab content
    body.add(link(name="tabs"))
    body.add(heading(2, "Tabs"))
    for t in tabs:
        body.add(t.get_html_content(heading_level=3))
    # Chord content
    body.add(link(name="chords"))
    body.add(heading(2, "Chords"))
    for c in chords:
        body.add(c.get_html_content(heading_level=3))
    # Tab Index
    body.add(link(name="index_tabs"))
    body.add(heading(2, "Tab index"))
    if not show_titles_in_toc:
        body.add(heading(3, link(name="index_tabs_by_title") + "By title"))
        for t in tabs:
            body.add(t.get_link())
            body.add(HtmlFormatter.new_line)
    body.add(heading(3, link(name="index_tabs_by_artist") + "By artist"))
    for artist, tabs_grouped in my_groupby(tabs, key=Tab.by_artist):
        body.add(HtmlFormatter.a(name=HtmlFormatter.string_to_html_id("artist_%s" % artist)))
        body.add("\n")
        body.add(heading(4, artist))
        for t in tabs_grouped:
            body.add(t.get_link(display_artist=False))
            body.add(HtmlFormatter.new_line)
    body.add(heading(3, link(name="index_tabs_by_diff") + "By difficulty"))
    for diff, tabs_grouped in my_groupby(tabs, key=Tab.by_difficulty):
        body.add(heading(4, diff))
        for t in tabs_grouped:
            body.add(t.get_link())
            body.add(HtmlFormatter.new_line)
    body.add(heading(3, link(name="index_tabs_by_type") + "By type"))
    for type_name, tabs_grouped in my_groupby(tabs, key=Tab.by_type):
        body.add(heading(4, type_name))
        for t in tabs_grouped:
            body.add(t.get_link(display_type=False))
            body.add(HtmlFormatter.new_line)
    body.add(heading(3, link(name="index_tabs_by_src") + "By website"))
    for src, tabs_grouped in my_groupby(tabs, key=Tab.by_src):
        body.add(heading(4, src))
        for t in tabs_grouped:
            body.add(t.get_link(display_src=False))
            body.add(HtmlFormatter.new_line)
    # Chord Index
    body.add(link(name="index_chords"))
    body.add(heading(2, "Chord index"))
    if not show_chords_in_toc:
        body.add(heading(3, link(name="index_chords_by_title") + "By name"))
        for c in chords:
            body.add(c.get_link(display_type=True))
            body.add(HtmlFormatter.new_line)
    body.add(heading(3, link(name="index_chords_by_type") + "By type"))
    for type_name, chords_grouped in my_groupby(chords, key=Chord.by_type):
        body.add(heading(4, type_name))
        for c in chords_grouped:
            body.add(c.get_link(display_type=False))
            body.add(HtmlFormatter.new_line)
    return body


def generate_html(title, tabs, chords):
    return HtmlFormatter.doctype + str(HtmlFormatter.html().add(get_html_head(title)).add(get_html_body(title, tabs, chords)))


def subprocess_call(cmd):
    cmd_str = " ".join(cmd)
    print("%s begin" % cmd_str)
    ret = subprocess.call(cmd)
    print("%s returned %d" % (cmd_str, ret))


def make_book(tabs, chords, base_filename, make_mobi=True, make_pdf=True, title="Tabs and Chords"):
    # File name handling
    if base_filename.endswith(".html"):
        base_filename = base_filename[:-len(".html")]
    html_file = base_filename + ".html"
    pdf_file = base_filename + ".pdf"
    # Create intermediate directories
    pathlib.Path(base_filename).parent.mkdir(parents=True, exist_ok=True)
    # Generate HTML
    with open(html_file, 'w+') as book:
        book.write(generate_html(title, tabs, chords))
        print("Wrote in %s" % html_file)
    # Generate PDF
    if make_pdf:
        # Various options from https://superuser.com/questions/592974/how-to-print-to-save-as-pdf-from-a-command-line-with-chrome-or-chromium
        cmd = ["chromium-browser", "--headless", "--disable-gpu", "--print-to-pdf=" + pdf_file, html_file]
        cmd = ["google-chrome",    "--headless", "--disable-gpu", "--print-to-pdf=" + pdf_file, html_file]
        cmd = ["wkhtmltopdf", html_file, pdf_file]
        subprocess_call(cmd)
    # Generate MOBI
    if make_mobi:
        cmd = [KINDLEGEN_PATH, '-verbose', '-dont_append_source', html_file]
        subprocess_call(cmd)
