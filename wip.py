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
    "https://tabs.ultimate-guitar.com/tab/the-beatles/yesterday-ukulele-1728302",
    "https://tabs.ultimate-guitar.com/tab/adele/someone-like-you-chords-1006751",
    "https://tabs.ultimate-guitar.com/tab/oasis/dont-look-back-in-anger-chords-6097",
    "https://tabs.ultimate-guitar.com/tab/the-beatles/let-it-be-chords-60690",
    "https://tabs.ultimate-guitar.com/tab/john-lennon/imagine-chords-9306",
    "https://tabs.ultimate-guitar.com/tab/elton-john/your-song-chords-29113",
    "https://tabs.ultimate-guitar.com/tab/the-beatles/hey-jude-chords-1061739",
    "https://tabs.ultimate-guitar.com/tab/david-bowie/space-oddity-chords-105869",
    "https://tabs.ultimate-guitar.com/tab/israel-kamakawiwoole/over-the-rainbow-chords-2135261",
    "https://tabs.ultimate-guitar.com/tab/israel-kamakawiwoole/over-the-rainbow-ukulele-1486181",
    "https://tabs.ultimate-guitar.com/tab/the-beatles/yesterday-chords-887610",
    "https://tabs.ultimate-guitar.com/tab/the-beatles/something-chords-335727",
    "https://tabs.ultimate-guitar.com/tab/the-beatles/something-chords-1680129",
    "https://tabs.ultimate-guitar.com/tab/the-beatles/something-ukulele-1801336",
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
    # For testing purposes
    "https://tabs.ultimate-guitar.com/tab/nirvana/smells-like-teen-spirit-drums-859029",
    "https://tabs.ultimate-guitar.com/tab/metallica/nothing-else-matters-video-1024840",
    "https://tabs.ultimate-guitar.com/tab/guns-n-roses/sweet-child-o-mine-power-301970",
    "https://tabs.ultimate-guitar.com/tab/muse/hysteria-bass-96516",
    "https://tabs.ultimate-guitar.com/tab/led-zeppelin/stairway-to-heaven-guitar-pro-223796",
    "https://tabs.ultimate-guitar.com/tab/eagles/hotel-california-official-1910943",
    "https://tabs.ultimate-guitar.com/tab/misc-cartoons/frozen-let-it-go-chords-1445224",
    "https://tabs.ultimate-guitar.com/tab/tones-and-i/dance-monkey-chords-2787730",
    "https://tabs.ultimate-guitar.com/tab/frank-sinatra/fly-me-to-the-moon-ukulele-1351387",
]


def write_json_to_file(json_data, filename='debug.json'):
    with open(filename, 'w+') as f:
        json.dump(json_data, f, indent=4, sort_keys=True)


class HtmlFormatter(object):

    @staticmethod
    def string_to_html_id(s):
        return html.escape(s, quote=True)

    @staticmethod
    def pre(s):
        return "<pre>%s</pre>\n" % s

    @staticmethod
    def a(href=None, content=None, title=None, name=None):
        title_used = "" if title is None else " title=\"%s\"" % title
        name_used = "" if name is None else " name=\"%s\"" % name
        href_used = "" if href is None else " href=\"%s\"" % href
        closing = " />" if content is None else ">%s</a>" % content
        return "<a%s%s%s%s" % (href_used, name_used, title_used, closing)


class Chords(object):

    name_and_type_to_obj = dict()
    by_name = lambda c: (c.name, c.is_ukulele)
    by_type = lambda c: "Ukulele" if c.is_ukulele else "Guitar"

    def __init__(self, name, is_ukulele, details):
        self.name = name
        self.is_ukulele = is_ukulele
        self.details = details
        self.index = self.register()
        self.html_anchor = HtmlFormatter.string_to_html_id("chord%s%s%s" % (self.name, "-ukulele" if is_ukulele else "", str(self.index) if self.index else ""))

    def register(self):
        key = (self.name, self.is_ukulele)
        data = self.name_and_type_to_obj.setdefault(key, [])
        for i, d in enumerate(data):
            if d.details == self.details:
                return i
        data.append(self)
        return len(data) - 1

    @classmethod
    def from_raw_data(cls, data, is_ukulele):
        if data is None:
            data = dict()
        if data == []:
            data = dict()
        return sorted((cls(name, is_ukulele, details) for name, details in data.items()), key=cls.by_name)

    @classmethod
    def get_all(cls):
        return [v for values in cls.name_and_type_to_obj.values() for v in values]

    def get_link(self, display_type):
        type_name = " (Ukulele)" if display_type and self.is_ukulele else ""
        return HtmlFormatter.a(href="#" + self.html_anchor, title=self.details[0]['id'], content=self.name + type_name)

    @classmethod
    def format_fingering_detail(cls, name, fingering):
        # WORK IN PROGRESS
        # print(name, str(fingering))
        frets = fingering['frets']
        capos = fingering['listCapos']
        fingers = fingering['fingers']
        fret_offset = fingering['fret']
        nb_strings = len(frets)
        nb_frets = 5
        width = 2
        height = 1

        top, mid, bottom, vert_lines = ("┍", "┯", "┑", "━"), ("├", "┼", "┤", "─"), ("└", "┴", "┘", "─"), ("│", "│", "│", " ")
        symbols = []
        symbols.append(top)
        for i in range(nb_frets - 1):
            symbols.extend([vert_lines] * height + [mid])
        symbols.extend([vert_lines] * height + [bottom])
        fretboard = [([beg.ljust(width, fill)] + [mid.ljust(width, fill)] * (nb_strings - 2) + [end]) for beg, mid, end, fill in symbols]

        for j, (fr, fi) in enumerate(reversed(list(zip(frets, fingers)))):
            if fr > 0:
                assert fi in [0, 1, 2, 3, 4]
                fi_str = str(fi)
                if fret_offset:
                    fr -= fret_offset - 1
                i = 1 + ((fr - 1) * (height + 1)) + (height // 2)
                fretboard[i][j] = fi_str + fretboard[i][j][len(fi_str):]
            elif fr == 0:
                assert fi == 0
            elif fr == -1:
                assert fi == 0
            else:
                assert False

        return HtmlFormatter.pre("\n".join("".join(line) for line in fretboard))

    def get_html_content(self):
        type_name = " (Ukulele)" if self.is_ukulele else ""
        debug = self.format_fingering_detail(self.name, self.details[0])
        idx_width = len(str(len(self.details)))
        fret_details = [["x" if f < 0 else str(f) for f in reversed(detail['frets'])] for detail in self.details]
        fret_width = max(len(f) for frets in fret_details for f in frets)
        content = "\n".join("%s:%s" % (str(i + 1).rjust(idx_width), "".join(f.rjust(1 + fret_width) for f in frets)) for i, frets in enumerate(fret_details))
        return HtmlFormatter.a(name=self.html_anchor) + "\n<h2>%s%s</h2>\n%s%s" % (self.name, type_name, HtmlFormatter.pre(content), debug)

    def get_short_html_content(self, alignment=10):
        padding = " " * (alignment - len(self.name))
        return "%s%s: %s" % (padding, self.get_link(display_type=False), self.details[0]['id'])


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
        width = 2
        values = [strum_values[m['measure']] for m in self.measures]
        numbers = list(range(len(values)))
        if self.is_triplet:
            assert self.denuminator in (8, 16), "denuminator=%d is not handled for triplet" % self.denuminator
            if self.denuminator == 8:
                coef, beg, mid, end, fill = 3, "└", "┴", "┘", "─"
            else:
                coef, beg, mid, end, fill = 6, "╘", "╧", "╛", "═"
            beg2, mid2, end2, fill2 = "└", "3", "┘", "─"
            symbols = [[beg.ljust(width, fill), mid.ljust(width, fill), end], [beg2.ljust(width, fill2), mid2.ljust(width, fill2), end2]]
        else:
            assert self.denuminator in (4, 8, 16), "denuminator=%d is not handled" % self.denuminator
            if self.denuminator == 4:
                coef, beg, end, fill = 1, "│", "│", " "
            elif self.denuminator == 8:
                coef, beg, end, fill = 2, "└", "┘", "─"
            else:
                coef, beg, end, fill = 4, "╘", "╛", "═"
            symbols = [beg.ljust(width, fill), end],
        patterns = [(s[0] for s in values),
                    (s[1] for s in values),
                    ((str(1 + i//coef) if i % coef == 0 else '&' if (2*i % coef == 0) else '') for i in numbers)]
        for symbol in symbols:
            patterns.append(s for s, _ in zip(itertools.cycle(symbol), numbers))
        patterns = ["".join(v.ljust(width) for v in p).rstrip() for p in patterns]
        lines = "\n".join(p for p in patterns if p)
        part = self.part if self.part else "All"
        return HtmlFormatter.pre("%s: %d bpm, triplet:%d, denuminator:%d, %d measures\n%s" % (
                    part,
                    self.bpm,
                    self.is_triplet,
                    self.denuminator,
                    len(self.measures),
                    lines))

class GuitarTab(object):

    by_name = operator.attrgetter('song_name')
    by_artist = operator.attrgetter('artist_name')
    by_difficulty = operator.attrgetter('difficulty')
    by_type = operator.attrgetter('type_name')

    def get_link(self, display_artist=True, display_type=True, prefix=""):
        acoustic = "Acoustic " if self.is_acoustic else ""
        artist_name = " - %s" % self.artist_name if display_artist else ""
        type_name = " (%s%s)" % (acoustic, self.type_name) if display_type else ""
        return HtmlFormatter.a(href="#" + self.html_anchor, content="%s%s%s%s" % (prefix, self.song_name, artist_name, type_name))

    def get_header(self):
        anchor = HtmlFormatter.a(name=self.html_anchor)
        artist_link = HtmlFormatter.a(href=self.artist_url, content=self.artist_name)
        src_link = self.get_link_to_original()
        return """%s\n<h2 class="chapter">%s - %s (%s%s)</h2>\n%s<br />
""" % (anchor, self.song_name, artist_link, "Acoustic " if self.is_acoustic else "", self.type_name, src_link)

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
        if not self.chords:
            return ""
        alignment = max(len(c.name) for c in self.chords)
        return HtmlFormatter.pre("\n".join(c.get_short_html_content(alignment) for c in self.chords))

    def get_link_to_original(self):
        raise NotImplementedError

    def get_tab_content(self):
        raise NotImplementedError

    def get_strumming_content(self):
        raise NotImplementedError

    @classmethod
    def from_url(cls, url):
        return None

    @classmethod
    def from_list_url(cls, list_url):
        return []

class GuitarTabFromGuitarTabDotCom(GuitarTab):
    prefixes = 'https://www.guitaretab.com/',


class GuitarTabFromGuitarTabsDotCc(GuitarTab):
    prefixes = 'https://www.guitartabs.cc/',

class ChordsFromTabs4Acoustic(object):

    @classmethod
    def from_html_div(cls, div):
        return []


class GuitarTabFromTabs4Acoustic(GuitarTab):
    prefixes = 'https://www.tabs4acoustic.com/',

    def __init__(self, song_name, artist_name, url, tab_content, chord_div):
        self.song_name = song_name
        self.artist_name = artist_name
        self.url = url
        self.tab_content = tab_content
        self.is_acoustic = False
        self.type_name = "TODO type"
        self.html_anchor = "TODO anchor"
        self.artist_url = "TODO artist url"
        self.difficulty = "Unknown"
        self.capo = None
        self.tonality = None
        self.tuning = None
        self.chords = ChordsFromTabs4Acoustic.from_html_div(chord_div)

    @classmethod
    def from_url(cls, url):
        soup = urlCache.get_soup(url)
        return cls(song_name='toto',
                   artist_name='titi',
                   url=url,
                   tab_content=soup.find(id='tab_zone').find(class_="small-12 column"),
                   chord_div=soup.find(id="crd_zone"))

    def get_link_to_original(self):
        return HtmlFormatter.a(href=self.url, content="original")

    def get_tab_content(self):
        #for i, c in enumerate(self.tab_content.contents):
        #    print(i, c)
        #print(str(self.tab_content))
        #content = HtmlFormatter.pre(str(self.tab_content).replace('\r\n', '\n'))
        # [<a title="[ Picture of the guitar chord : E ]" href="https://www.tabs4acoustic.com/images/accords/photo-e-022100.jpg" class="viewchord hl_crd chord_diag tabtooltip"><span><img src="https://www.tabs4acoustic.com/images/crd/E[0,2,2,1,0,0]-0.png" alt="E " /></span>E</a>]
        return "toto"

    def get_strumming_content(self):
        return ""


class GuitarTabFromUltimateGuitar(GuitarTab):
    prefixes = 'https://tabs.ultimate-guitar.com/', 'https://www.ultimate-guitar.com/'

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
        soup = urlCache.get_soup(url)

        json_content = json.loads(soup.find("div", class_="js-store")["data-content"])
        page_data = json_content['store']['page']['data']
        tab = page_data['tab']
        tab_view = page_data['tab_view']
        tab_view_meta = tab_view['meta']
        if tab_view_meta == []:
            tab_view_meta = {}
        assert url == tab['tab_url']

        is_ukulele = tab['type_name'] == 'Ukulele'
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
            tab_content = tab_view['wiki_tab'].get('content', ''),
            chords = Chords.from_raw_data(tab_view['applicature'], is_ukulele),
            strummings = Strumming.from_raw_data(tab_view['strummings']),
            html_anchor = HtmlFormatter.string_to_html_id("tab" + str(tab['id']) + "-" + tab['song_name']),
        )

    @classmethod
    def from_list_url(cls, list_url):
        soup = urlCache.get_soup(list_url)
        json_content = json.loads(soup.find("div", class_="js-store")["data-content"])
        page_data = json_content['store']['page']['data']
        return [cls.from_url(t['tab_url']) for t in page_data['tabs']]

    def get_link_to_original(self):
        return HtmlFormatter.a(href=self.url, content="%s version %d from %s (rated %f / %d votes)" % (self.type_name, self.version, self.author, self.rating, self.votes))

    def get_tab_content(self):
        content = HtmlFormatter.pre(self.tab_content
            .replace('\r\n', '\n')
            .replace('[tab]', '')
            .replace('[/tab]', ''))
        for c in self.chords:
            content = content.replace("[ch]%s[/ch]" % c.name, c.get_link(display_type=False))
        return content

    def get_strumming_content(self):
        return "".join(s.get_html_content() for s in self.strummings)


class GuitarTabGetter(object):

    @classmethod
    def get_class_for_url(cls, url):
        print(url)
        for class_ in (GuitarTabFromUltimateGuitar,
                       GuitarTabFromGuitarTabDotCom,
                       GuitarTabFromTabs4Acoustic,
                       GuitarTabFromGuitarTabsDotCc):
            for prefix in class_.prefixes:
                if url.startswith(prefix):
                    return class_
        raise Exception("Unsupported URL %s" % url)

    @classmethod
    def from_url(cls, url):
        return cls.get_class_for_url(url).from_url(url)

    @classmethod
    def from_list_url(cls, url):
        return cls.get_class_for_url(url).from_list_url(url)


def my_groupby(iterable, key=None):
    return itertools.groupby(sorted(iterable, key=key), key=key)


header = """
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html;charset=utf-8">
<meta name='cover' content='empty.jpg'>
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
    if 1:
        tabs = [GuitarTabGetter.from_url(url) for url in urls]
    elif 0: # For debug purposes
        tabs = GuitarTabGetter.from_list_url('https://www.ultimate-guitar.com/top/tabs')
    elif 0: # For debug purposes
        tabs = []
        for order in ('order=hitsdaily_desc', 'order=hitstotal_desc', 'order=rating_desc', ''):
            for type_ in ('type=all', 'type=official', 'type=chords', 'type=tabs', 'type=guitar%20pro', 'type=power', 'type=bass', 'type=ukulele',  ''):
                url = "https://www.ultimate-guitar.com/top/tabs?" + order + '&' + type_
                tabs.extend(GuitarTab.from_list_url(url))
    tabs = [t for t in tabs  if t is not None]
    chords = Chords.get_all()

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
<h5><a href="#toc_chords_by_name">By name</a></h5>
<h5><a href="#toc_chords_by_type">By type</a></h5>
<h3><a name="toc_tabs" />
<a href="#tabs">Tabs</a></h3>
""")
        book.write("""<h4><a name="toc_tabs_by_title" />By title</h4>\n""")
        for t in sorted(tabs, key=GuitarTab.by_name):
            book.write(t.get_link() + "<br />\n")
        book.write("""<h4><a name="toc_tabs_by_artist" />By artist</h4>\n""")
        for artist, tabs_grouped in my_groupby(tabs, key=GuitarTab.by_artist):
            book.write("""<h5>%s</h5>\n""" % artist)
            for t in sorted(tabs_grouped, key=GuitarTab.by_name):
                book.write(t.get_link(display_artist=False) + "<br />\n")
        book.write("""<h4><a name="toc_tabs_by_diff" />By difficulty</h4>\n""")
        for diff, tabs_grouped in my_groupby(tabs, key=GuitarTab.by_difficulty):
            book.write("""<h5>%s</h5>\n""" % diff)
            for t in sorted(tabs_grouped, key=GuitarTab.by_name):
                book.write(t.get_link() + "<br />\n")
        book.write("""<h4><a name="toc_tabs_by_type" />By type</h4>\n""")
        for type_name, tabs_grouped in my_groupby(tabs, key=GuitarTab.by_type):
            book.write("""<h5>%s</h5>\n""" % type_name)
            for t in sorted(tabs_grouped, key=GuitarTab.by_name):
                book.write(t.get_link(display_type=False) + "<br />\n")
        book.write("""<h3><a name="toc_chords" /><a href="#chords">Chords</a></h3>\n""")
        book.write("""<h4><a name="toc_chords_by_name" />By name</h4>\n""")
        for c in sorted(chords, key=Chords.by_name):
            book.write(c.get_link(display_type=True) + "<br />\n")
        book.write("""<h4><a name="toc_chords_by_type" />By type</h4>\n""")
        for type_name, chords_grouped in my_groupby(chords, key=Chords.by_type):
            book.write("""<h5>%s</h5>\n""" % type_name)
            for c in sorted(chords_grouped, key=Chords.by_name):
                book.write(c.get_link(display_type=False) + "<br />\n")
        book.write(pagebreak)
        book.write(start)
        # tab content
        book.write("""<a name="tabs" />""")
        for t in sorted(tabs, key=GuitarTab.by_name):
            book.write(t.get_header())
            book.write(t.get_optional_field_content())
            book.write(t.get_strumming_content())
            book.write(t.get_chord_content())
            book.write(pagebreak)
            book.write(t.get_tab_content())
            book.write(t.get_link(prefix="Back to top of ") + "<br />\n")
            book.write(pagebreak)
        # chord content
        book.write("""<a name="chords" />""")
        for c in sorted(chords, key=Chords.by_name):
            book.write(c.get_html_content())
            book.write(pagebreak)

        # footer
        book.write(footer)

    print("Wrote in %s" % htmlfile)
    if make_mobi:
        subprocess.call([KINDLEGEN_PATH, '-verbose', '-dont_append_source', htmlfile])

make_book(URLS)
