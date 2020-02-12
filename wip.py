import json
import urlfunctions
import operator
import subprocess
import itertools
import html

# https://kdp.amazon.com/en_US/help/topic/G200673180 "Supported HTML Tags in Book Content "
# http://www.amazon.com/kindleformat/kindlegen
KINDLEGEN_PATH = 'Kindlegen/kindlegen'

urlCache = urlfunctions.UrlCache("cache")

URLS = [
    "https://tabs.ultimate-guitar.com/tab/jeff-buckley/hallelujah-chords-198052",
    "https://tabs.ultimate-guitar.com/tab/oasis/wonderwall-chords-27596",
    "https://tabs.ultimate-guitar.com/tab/eagles/hotel-california-chords-46190",
    "https://tabs.ultimate-guitar.com/tab/led-zeppelin/stairway-to-heaven-tabs-9488",
    "https://tabs.ultimate-guitar.com/tab/the-beatles/yesterday-chords-17450",
    "https://tabs.ultimate-guitar.com/tab/adele/someone-like-you-chords-1006751",
    "https://tabs.ultimate-guitar.com/tab/oasis/dont-look-back-in-anger-chords-6097",
    "https://tabs.ultimate-guitar.com/tab/the-beatles/let-it-be-chords-60690",
    "https://tabs.ultimate-guitar.com/tab/john-lennon/imagine-chords-9306",
    "https://tabs.ultimate-guitar.com/tab/elton-john/your-song-chords-29113",
    "https://tabs.ultimate-guitar.com/tab/the-beatles/hey-jude-chords-1061739",
    "https://tabs.ultimate-guitar.com/tab/david-bowie/space-oddity-chords-105869",
    "https://tabs.ultimate-guitar.com/tab/israel-kamakawiwoole/over-the-rainbow-chords-2135261",
    "https://tabs.ultimate-guitar.com/tab/the-beatles/yesterday-chords-887610",
    "https://tabs.ultimate-guitar.com/tab/the-beatles/something-chords-335727",
    "https://tabs.ultimate-guitar.com/tab/the-beatles/something-chords-1680129",
    "https://tabs.ultimate-guitar.com/tab/neil-young/heart-of-gold-chords-56555",
    "https://tabs.ultimate-guitar.com/tab/joan-baez/diamonds-and-rust-chords-1044414",
    "https://tabs.ultimate-guitar.com/tab/jean-jacques-goldman/comme-toi-chords-69704",
    "https://tabs.ultimate-guitar.com/tab/francis-cabrel/la-corrida-chords-995197",
    "https://tabs.ultimate-guitar.com/tab/queen/love-of-my-life-chords-340088",
    "https://tabs.ultimate-guitar.com/tab/the-beatles/let-it-be-chords-17427",
    "https://tabs.ultimate-guitar.com/tab/nirvana/the-man-who-sold-the-world-chords-651988",
    "https://tabs.ultimate-guitar.com/tab/metallica/nothing-else-matters-tabs-8519",
    "https://tabs.ultimate-guitar.com/tab/moriarty/jimmy-chords-790948",
    "https://tabs.ultimate-guitar.com/tab/the-beatles/here-there-and-everywhere-chords-17273",
    "https://tabs.ultimate-guitar.com/tab/muse/feeling-good-chords-815018",
    "https://tabs.ultimate-guitar.com/tab/the-beatles/here-comes-the-sun-chords-1738813",
    "https://tabs.ultimate-guitar.com/tab/the-beatles/here-comes-the-sun-tabs-201130",
    "https://tabs.ultimate-guitar.com/tab/the-beatles/while-my-guitar-gently-weeps-chords-17446",
    "https://tabs.ultimate-guitar.com/tab/jeff-buckley/grace-chords-1191773",
    "https://tabs.ultimate-guitar.com/tab/jeff-buckley/grace-tabs-131242",
    "https://tabs.ultimate-guitar.com/tab/pink-floyd/wish-you-were-here-chords-44555",
    "https://tabs.ultimate-guitar.com/tab/pink-floyd/wish-you-were-here-tabs-984061",
    "https://tabs.ultimate-guitar.com/tab/coldplay/the-scientist-chords-180849",
    "https://tabs.ultimate-guitar.com/tab/r-e-m-/everybody-hurts-chords-37519",
    "https://tabs.ultimate-guitar.com/tab/r-e-m-/everybody-hurts-tabs-90215",
    "https://tabs.ultimate-guitar.com/tab/r-e-m-/losing-my-religion-chords-114345",
    "https://tabs.ultimate-guitar.com/tab/r-e-m-/losing-my-religion-tabs-81372",
    "https://tabs.ultimate-guitar.com/tab/r-e-m-/imitation-of-life-chords-22477",
    "https://tabs.ultimate-guitar.com/tab/radiohead/karma-police-chords-103398",
    "https://tabs.ultimate-guitar.com/tab/elton-john/rocket-man-chords-10744",
    "https://tabs.ultimate-guitar.com/tab/america/a-horse-with-no-name-chords-59609",
    "https://tabs.ultimate-guitar.com/tab/the-beatles/blackbird-tabs-56997",
    "https://tabs.ultimate-guitar.com/tab/the-beatles/across-the-universe-chords-202167",
    "https://tabs.ultimate-guitar.com/tab/the-beatles/i-want-to-hold-your-hand-chords-457088",
    "https://tabs.ultimate-guitar.com/tab/nirvana/the-man-who-sold-the-world-chords-841325",
    "https://tabs.ultimate-guitar.com/tab/travis/sing-chords-1334",
    "https://tabs.ultimate-guitar.com/tab/travis/sing-tabs-2749659",
    "https://tabs.ultimate-guitar.com/tab/simon-garfunkel/the-sound-of-silence-chords-159157",
    "https://tabs.ultimate-guitar.com/tab/simon-garfunkel/the-sound-of-silence-tabs-58064",
    "https://tabs.ultimate-guitar.com/tab/simon-garfunkel/the-sound-of-silence-tabs-2655012",
    "https://tabs.ultimate-guitar.com/tab/depeche-mode/enjoy-the-silence-chords-891725",
    "https://tabs.ultimate-guitar.com/tab/the-handsome-family/far-from-any-road-chords-1457192",
    "https://tabs.ultimate-guitar.com/tab/the-handsome-family/far-from-any-road-tabs-2094741",
    "https://tabs.ultimate-guitar.com/tab/the-handsome-family/far-from-any-road-true-detective-theme-chords-1493932",
]


def write_json_to_file(json_data, filename='debug.json'):
    with open(filename, 'w+') as f:
        json.dump(json_data, f, indent=4, sort_keys=True)


def string_to_html_id(s):
    return html.escape(s, quote=True)


class Chords(object):

    name_to_obj = dict()
    by_name = operator.attrgetter('name')

    def __init__(self, name, details):
        self.name = name
        self.details = details
        self.html_anchor = string_to_html_id(self.name)
        self.register()

    def register(self):
        if self.name in self.name_to_obj:
            assert self.details == self.name_to_obj[self.name].details
        else:
            self.name_to_obj[self.name] = self

    @classmethod
    def from_raw_data(cls, data):
        if data is None:
            data = dict()
        return sorted((cls(name, details) for name, details in data.items()), key=cls.by_name)

    @classmethod
    def get_all(cls):
        return sorted(cls.name_to_obj.values(), key=cls.by_name)

    def get_link(self):
        return "<a href=\"#chord%s\">%s</a>" % (self.html_anchor, self.name)

    def get_html_content(self):
        h = "<a name=\"chord%s\" />\n<h2>%s</h2>" % (self.html_anchor, self.name)
        return h + "".join("%d: %s<br/>\n" % (i, v['id']) for i, v in enumerate(self.details))

    def get_short_html_content(self, alignment=10):
        padding = "&nbsp;" * (alignment - len(self.name))
        return "%s<a href=\"#chord%s\">%s</a>: %s<br />\n" % (padding, self.html_anchor, self.name, self.details[0]['id'])


class Strumming(object):

    def __init__(self, part, measures, bpm, is_triplet, denuminator):
        self.part = part
        self.measures = measures
        self.bpm = bpm
        self.is_triplet = is_triplet
        self.denuminator = denuminator

    @classmethod
    def from_raw_data(cls, data):
       return [cls(part=s['part'],
                    measures=s['measures'],
                    bpm=s['bpm'],
                    is_triplet=s['is_triplet'],
                    denuminator=s['denuminator']) for s in data]

    def get_html_content(self):
        strum_values = {
            1:   (' ', '↓'),
            101: (' ', '↑'),
            202: (' ', ' '),
            3:   ('>', '↓'), # arrow with a small >
            103: ('>', '↑'), # arrow with a small >
            2:   ('x', '↓'), # arrow with a small x
            102: ('x', '↑'), # arrow with a small x
            201: (' ', 'x'),
            203: (' ', '⏸'), # the pause symbol
        }
        values = [m['measure'] for m in self.measures]
        pattern0 = "".join(strum_values[v][0].ljust(2, " ") for v in values).rstrip()
        if pattern0:
            pattern0 += "\n"
        pattern1 = "".join(strum_values[v][1].ljust(2, " ") for v in values).rstrip()
        # TODO: how to count ? how to display lines ? how to handle triplets ?
        #coef = 2  # how to compute this ?
        #beg, end = ("╘═", "╛ ") if coef == 2 else ("└─", "┘ ")
        #pattern2 = "".join((str(1 + i//(2*coef)) if i % (2*coef) == 0 else '&' if i % coef == 0 else ' ').ljust(2, " ") for i, _ in enumerate(values)).replace(" ", space)
        #pattern3 = "".join((beg if i % 2 == 0 else end) for i, _ in enumerate(values)).replace(" ", space)
        part = self.part if self.part else "All"
        return "<pre>%s: %d bpm, triplet:%d, denuminator:%d, %d measures\n%s%s</pre>" % (part, self.bpm, self.is_triplet, self.denuminator, len(self.measures), pattern0, pattern1)


class GuitarTab(object):

    by_name = operator.attrgetter('song_name')
    by_artist = operator.attrgetter('artist_name')
    by_difficulty = operator.attrgetter('difficulty')
    by_type = operator.attrgetter('type_name')

    def __init__(self, song_name, artist_name, url, artist_url, type_name, version, author, rating, votes, is_acoustic, capo, tonality, difficulty, tuning, tab_content, chords, strummings, html_anchor):
        self.song_name = song_name
        self.artist_name = artist_name
        self.url = url
        self.artist_url = artist_url
        self.type_name = type_name
        self.version = version
        self.author = author
        self.rating = rating
        self.votes = votes
        self.is_acoustic = is_acoustic
        self.capo = capo
        self.tonality = tonality
        self.difficulty = difficulty
        self.tuning = tuning
        self.tab_content = tab_content
        self.chords = chords
        self.strummings = strummings
        self.html_anchor = html_anchor

    @classmethod
    def from_url(cls, url):
        print(url)
        soup = urlCache.get_soup(url)

        json_content = json.loads(soup.find("div", class_="js-store")["data-content"])
        page_data = json_content['store']['page']['data']
        tab = page_data['tab']
        tab_view = page_data['tab_view']
        tab_view_meta = tab_view['meta']
        if tab_view_meta == []:
            tab_view_meta = {}
        assert url == tab['tab_url']


        return cls(
            song_name = tab['song_name'],
            artist_name = tab['artist_name'],
            url = url,
            artist_url = tab['artist_url'],
            type_name = tab['type_name'],
            version = tab['version'],
            author = tab['username'],
            rating = tab['rating'],
            votes = tab['votes'],
            is_acoustic = tab['recording']['is_acoustic'],
            capo = tab_view_meta.get('capo', None),
            tonality = tab_view_meta.get('tonality', None),
            difficulty = tab_view_meta.get('difficulty', 'Unknown'),
            tuning = tab_view_meta.get('tuning', dict()).get('name', None),
            tab_content = tab_view['wiki_tab']['content'],
            chords = Chords.from_raw_data(tab_view['applicature']),
            strummings = Strumming.from_raw_data(tab_view['strummings']),
            html_anchor = str(tab['id']) + "-" + string_to_html_id(tab['song_name']),
        )

    @classmethod
    def from_list_url(cls, list_url='https://www.ultimate-guitar.com/top/tabs'):
        soup = urlCache.get_soup(list_url)
        json_content = json.loads(soup.find("div", class_="js-store")["data-content"])
        page_data = json_content['store']['page']['data']
        return [cls.from_url(t['tab_url']) for t in page_data['tabs']]

    def get_link(self, display_artist=True, display_type=True):
        acoustic = "Acoustic " if self.is_acoustic else ""
        artist_name = " - %s" % self.artist_name if display_artist else ""
        type_name = " (%s%s)" % (acoustic, self.type_name) if display_type else ""
        return "<a href=\"#tab%s\">%s%s%s</a><br />\n" % (self.html_anchor, self.song_name, artist_name, type_name)

    def get_header(self):
        return """<a name="tab%s" />
<h2 class="chapter">%s - <a href="%s">%s</a> (%s%s)</h2>
<a href="%s">%s version %d from %s (rated %f / %d votes)</a><br />
""" % (self.html_anchor, self.song_name, self.artist_url, self.artist_name, "Acoustic " if self.is_acoustic else "", self.type_name, self.url, self.type_name, self.version, self.author, self.rating, self.votes)

    def get_optional_field_content(self):
        opt_fields = [
            ('capo', 'Capo'),
            ('tonality', 'Tonality'),
            ('difficulty', 'Difficulty'),
            ('tuning', 'Tuning'),
        ]
        s = ""
        for opt_field, opt_name in opt_fields:
            val = getattr(self, opt_field)
            if val is not None:
                s += "%s: %s<br />\n" % (opt_name, val)
        return s

    def get_chord_content(self):
        alignment = max((len(c.name) for c in self.chords), default=0)
        return "".join(c.get_short_html_content(alignment) for c in self.chords)

    def get_tab_content(self):
        content = ("<pre>\n%s\n</pre>" % self.tab_content
            .replace('\r\n', '\n')
            .replace('[tab]', '')
            .replace('[/tab]', ''))
        for c in self.chords:
            content = content.replace("[ch]%s[/ch]" % c.name, c.get_link())
        return content

    def get_strumming_content(self):
        return "".join(s.get_html_content() for s in self.strummings)


def my_groupby(iterable, key=None):
    return itertools.groupby(sorted(iterable, key=key), key=key)


header = """
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html;charset=utf-8">
<title>Tabs and Chords</title>
<link rel="stylesheet" href="default.css" type="text/css" />
</head>
<body>
<h1>Tabs and Chords</h1>"""
# TODO: Add 'generated by'

footer = """
</body>
</html>
"""

pagebreak = "<mbp:pagebreak />\n"
start = "<a name=\"start\" />\n"

def make_book(urls, htmlfile="wip_book.html", make_mobi=True):
    tabs = [GuitarTab.from_url(url) for url in urls]
    tabs.sort(key=GuitarTab.by_name)

    with open(htmlfile, 'w+') as book:
        # header
        book.write(header)
        book.write(pagebreak)
        # table of content
        book.write("""<a id="TOC" />
<h2>Table of contents</h2>
<h3><a href="#tabs">Meta table of content</a></h3>
<h4><a href="#toc_tabs">Tabs</a></h4>
<h5><a href="#toc_tabs_by_title">By title</a></h5>
<h5><a href="#toc_tabs_by_artist">By artist</a></h5>
<h5><a href="#toc_tabs_by_diff">By difficulty</a></h5>
<h5><a href="#toc_tabs_by_type">By type</a></h5>
<h4><a href="#toc_chords">Chords</a></h4>
<h3><a name="toc_tabs" />
<a href="#tabs">Tabs</a></h3>
""")
        book.write("""<h4><a name="toc_tabs_by_title" />By title</h4>\n""")
        for t in sorted(tabs, key=GuitarTab.by_name):
            book.write(t.get_link())
        book.write("""<h4><a name="toc_tabs_by_artist" />By artist</h4>\n""")
        for artist, tabs_grouped in my_groupby(tabs, key=GuitarTab.by_artist):
            book.write("""<h5>%s</h5>\n""" % artist)
            for t in sorted(tabs_grouped, key=GuitarTab.by_name):
                book.write(t.get_link(display_artist=False))
        book.write("""<h4><a name="toc_tabs_by_diff" />By difficulty</h4>\n""")
        for diff, tabs_grouped in my_groupby(tabs, key=GuitarTab.by_difficulty):
            book.write("""<h5>%s</h5>\n""" % diff)
            for t in sorted(tabs_grouped, key=GuitarTab.by_name):
                book.write(t.get_link())
        book.write("""<h4><a name="toc_tabs_by_type" />By type</h4>\n""")
        for type_name, tabs_grouped in my_groupby(tabs, key=GuitarTab.by_type):
            book.write("""<h5>%s</h5>\n""" % type_name)
            for t in sorted(tabs_grouped, key=GuitarTab.by_name):
                book.write(t.get_link(display_type=False))
        book.write("""<h3><a name="toc_chords" /><a href="#chords">Chords</a></h3>\n""")
        for c in Chords.get_all():
            book.write(c.get_link() + "<br />\n")
        book.write(pagebreak)
        book.write(start)
        # tab content
        book.write("""<a name="tabs" />""")
        for t in tabs:
            book.write(t.get_header())
            book.write(t.get_optional_field_content())
            book.write(t.get_strumming_content())
            book.write(t.get_chord_content())
            book.write(pagebreak)
            book.write(t.get_tab_content())
            book.write(pagebreak)
        # chord content
        book.write("""<a name="chords" />""")
        for c in Chords.get_all():
            book.write(c.get_html_content())
            book.write(pagebreak)

        # footer
        book.write(footer)

    print("Wrote in %s" % htmlfile)
    if make_mobi:
        subprocess.call([KINDLEGEN_PATH, '-verbose', '-dont_append_source', htmlfile])

make_book(URLS)
