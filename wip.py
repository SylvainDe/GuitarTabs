import json
import urlfunctions
import operator
import subprocess
import itertools
import re
import hashlib
import urllib.parse
import html as htmlmodule
from bs4 import BeautifulSoup
import htmlformatter as HtmlFormatter

# https://kdp.amazon.com/en_US/help/topic/G200673180 "Supported HTML Tags in Book Content "
# http://www.amazon.com/kindleformat/kindlegen
KINDLEGEN_PATH = 'Kindlegen/kindlegen'

urlCache = urlfunctions.UrlCache("cache")

# Debug flag to be able to disable retrieval of all tabs and corresponding logging
# to be able to focus on a single getter class
IN_DEV=False

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
    "https://tabs.ultimate-guitar.com/tab/neil-young/harvest-moon-chords-73",
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
    "https://tabs.ultimate-guitar.com/tab/nirvana/mtv-unplugged-in-new-york-chords-98258",
    "https://tabs.ultimate-guitar.com/tab/travis/sing-chords-1334",
    "https://tabs.ultimate-guitar.com/tab/travis/sing-tabs-2749659",
    "https://tabs.ultimate-guitar.com/tab/simon-garfunkel/the-sound-of-silence-chords-159157",
    "https://tabs.ultimate-guitar.com/tab/simon-garfunkel/the-sound-of-silence-tabs-58064",
    "https://tabs.ultimate-guitar.com/tab/simon-garfunkel/the-sound-of-silence-tabs-2655012",
    "https://tabs.ultimate-guitar.com/tab/depeche-mode/enjoy-the-silence-chords-891725",
    "https://tabs.ultimate-guitar.com/tab/the-handsome-family/far-from-any-road-chords-1457192",
    "https://tabs.ultimate-guitar.com/tab/the-handsome-family/far-from-any-road-tabs-2094741",
    "https://tabs.ultimate-guitar.com/tab/the-handsome-family/far-from-any-road-true-detective-theme-chords-1493932",
    "https://www.guitaretab.com/g/greta-van-fleet/389642.html",
    "https://www.guitaretab.com/r/rem/15914.html",
    "https://www.guitaretab.com/r/rem/238402.html",
    "https://www.guitaretab.com/r/rem/176094.html",
    "https://www.guitartabs.cc/tabs/b/beatles/blackbird_tab_ver_12.html",
    "https://www.guitartabs.cc/tabs/e/eagles/hotel_california_tab.html",
    "https://www.guitartabs.cc/tabs/g/gotye/somebody_that_i_used_to_know_crd_ver_5.html",
    "https://www.guitartabs.cc/tabs/a/adele/someone_like_you_crd.html",
    "https://www.guitartabs.cc/tabs/a/adele/someone_like_you_tab_ver_2.html",
    "https://www.tabs4acoustic.com/en/guitar-tabs/the-eagles-tabs/hotel-california-acoustic-tab-67.html",
    "https://www.tabs4acoustic.com/en/guitar-tabs/jeff-buckley-tabs/hallelujah-acoustic-tab-213.html",
    "https://www.tabs4acoustic.com/en/guitar-tabs/izrael-kamakawiwo-ole-tabs/over-the-rainbow-acoustic-tab-319.html",
    "https://www.tabs4acoustic.com/en/guitar-tabs/david-bowie-tabs/space-oddity-acoustic-tab-407.html",
    "https://www.tabs4acoustic.com/en/guitar-tabs/ben-e-king-tabs/stand-by-me-acoustic-tab-442.html",
    "https://www.tabs4acoustic.com/en/guitar-tabs/bob-marley-tabs/redemption-song-acoustic-tab-133.html",
    "https://www.tabs4acoustic.com/en/free-riffs/led-zeppelin-black-dog-185.html",
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


class AbstractChords(object):

    name_and_type_to_obj = dict()
    by_name = lambda c: (c.name, c.is_ukulele)
    by_type = lambda c: "Ukulele" if c.is_ukulele else "Guitar"

    def __init__(self, name, is_ukulele, short_content):
        self.name = name
        self.is_ukulele = is_ukulele
        self.short_content = short_content
        # Note: don't forget to call register_and_build_html_anchor

    def register_and_build_html_anchor(self):
        # To be called from constructor ONLY when all fields are initialised
        index = self.register()
        self.html_anchor = HtmlFormatter.string_to_html_id("chord%s%s%s" % (self.name, "-ukulele" if self.is_ukulele else "", str(index) if index else ""))

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
            self.name == other.name and
            self.is_ukulele == other.is_ukulele and
            self.short_content == other.short_content)

    def register(self):
        key = (self.name, self.is_ukulele)
        data = self.name_and_type_to_obj.setdefault(key, [])
        for i, obj in enumerate(data):
            if self == obj:
                return i
        data.append(self)
        return len(data) - 1

    @classmethod
    def get_all(cls):
        return [v for values in cls.name_and_type_to_obj.values() for v in values]

    def get_link(self, display_type):
        type_name = " (Ukulele)" if display_type and self.is_ukulele else ""
        return HtmlFormatter.a(href="#" + self.html_anchor, title=self.short_content, content=self.name + type_name)

    def get_short_html_content(self, alignment=10):
        padding = " " * (alignment - len(self.name))
        return "%s%s: %s" % (padding, self.get_link(display_type=False), self.short_content)

    def get_html_content(self):
        type_name = " (Ukulele)" if self.is_ukulele else ""
        return HtmlFormatter.HtmlGroup(
                    HtmlFormatter.a(name=self.html_anchor),
                    "\n",
                    HtmlFormatter.h(2, "%s%s" % (self.name, type_name)),
                    self.get_specific_content(),
                    HtmlFormatter.pagebreak)

    def get_specific_content(self):
        return HtmlFormatter.comment("TODO: No real content for %s.get_specific_content" % self.__class__.__name__)


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


class AbstractGuitarTab(object):

    by_name = operator.attrgetter('song_name')
    by_artist = operator.attrgetter('artist_name')
    by_difficulty = operator.attrgetter('difficulty')
    by_type = operator.attrgetter('type_name')

    def __init__(self, url, song_name, artist_name, artist_url, tab_id):
        self.url = url
        self.song_name = song_name
        self.artist_name = artist_name
        self.artist_url = artist_url
        self.type_name = "Tab"
        self.part = ""
        self.is_acoustic = False
        self.capo = None
        self.tonality = None
        self.key = None
        self.difficulty = "Unknown"
        self.tuning = None
        if tab_id is None:
            tab_id = abs(int(hashlib.sha512(url.encode('utf-8')).hexdigest(), 16)) % (10 ** 8)
        self.html_anchor = HtmlFormatter.string_to_html_id("tab" + str(tab_id) + "-" + song_name)

    def get_link(self, display_artist=True, display_type=True, prefix=""):
        acoustic = "Acoustic " if self.is_acoustic else ""
        part = " " + self.part if self.part else ""
        artist_name = " - %s" % self.artist_name if display_artist else ""
        type_name = " (%s%s)" % (acoustic, self.type_name) if display_type else ""
        return HtmlFormatter.a(href="#" + self.html_anchor, content="%s%s%s%s%s" % (prefix, self.song_name, part, artist_name, type_name))

    def get_header(self):
        acoustic = "Acoustic " if self.is_acoustic else ""
        artist_link = HtmlFormatter.a(href=self.artist_url, content=self.artist_name)
        return HtmlFormatter.HtmlGroup(
                HtmlFormatter.a(name=self.html_anchor),
                "\n",
                HtmlFormatter.h(2, "%s - %s (%s%s)" % (self.song_name, artist_link, acoustic, self.type_name)),
                self.get_link_to_original(),
                HtmlFormatter.new_line)

    def get_optional_field_content(self):
        opt_fields = [
            ('capo', 'Capo'),
            ('tonality', 'Tonality'),
            ('key', 'Key'),
            ('difficulty', 'Difficulty'),
            ('tuning', 'Tuning'),
        ]
        s = ""
        for opt_field, opt_name in opt_fields:
            val = getattr(self, opt_field)
            if val is not None:
                s += "%s: %s%s" % (opt_name, val, HtmlFormatter.new_line)
        return s

    def get_chord_content(self):
        if not self.chords:
            return ""
        alignment = max(len(c.name) for c in self.chords)
        return HtmlFormatter.pre("\n".join(c.get_short_html_content(alignment) for c in self.chords))

    def get_html_content(self):
        return HtmlFormatter.HtmlGroup(
                self.get_header(),
                self.get_optional_field_content(),
                self.get_strumming_content(),
                self.get_chord_content(),
                HtmlFormatter.pagebreak,
                self.get_tab_content(),
                self.get_link(prefix="Back to top of "),
                HtmlFormatter.new_line,
                HtmlFormatter.pagebreak)

    def get_link_to_original(self):
        return HtmlFormatter.comment("No link to original (%s.get_link_to_original to be implemented)" % self.__class__.__name__)

    def get_tab_content(self):
        return HtmlFormatter.comment("No tab content (%s.get_tab_content to be implemented)" % self.__class__.__name__)

    def get_strumming_content(self):
        return HtmlFormatter.comment("No strumming content (%s.get_strumming_content to be implemented)" % self.__class__.__name__)

    @classmethod
    def from_url(cls, url):
        print("%s.from_url(%s) returned None" % (cls.__name__, url))
        return None

    @classmethod
    def from_list_url(cls, list_url):
        return []


class ChordsFromApplicature(AbstractChords):

    def __init__(self, name, is_ukulele, details):
        super().__init__(name=name, is_ukulele=is_ukulele, short_content=details[0]['id'])
        self.details = details
        self.register_and_build_html_anchor()

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
            self.name == other.name and
            self.is_ukulele == other.is_ukulele and
            self.short_content == other.short_content and
            self.details == other.details) # Do not use html_anchor

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

    def get_specific_content(self):
        debug = self.format_fingering_detail(self.name, self.details[0])
        idx_width = len(str(len(self.details)))
        fret_details = [["x" if f < 0 else str(f) for f in reversed(detail['frets'])] for detail in self.details]
        fret_width = max(len(f) for frets in fret_details for f in frets)
        content = "\n".join("%s:%s" % (str(i + 1).rjust(idx_width), "".join(f.rjust(1 + fret_width) for f in frets)) for i, frets in enumerate(fret_details))
        return HtmlFormatter.pre(content) + debug

    @classmethod
    def from_json_data(cls, data, is_ukulele):
        if data is None:
            data = dict()
        if data == []:
            data = dict()
        return sorted((cls(name, is_ukulele, details) for name, details in data.items()), key=cls.by_name)



class GuitarTabFromGuitarTabDotCom(AbstractGuitarTab):
    prefixes = 'https://www.guitaretab.com/',

    def __init__(self, song_name, artist_name, url, artist_url, rating, votes, tab_content, chords, tab_id):
        super().__init__(url, song_name, artist_name, artist_url, tab_id)
        self.rating = rating
        self.votes = votes
        self.tab_content = tab_content
        self.chords = chords

    def get_link_to_original(self):
        return HtmlFormatter.a(href=self.url, content="Version from guitartab.com (rated %s / %d votes)" % (self.rating, self.votes))

    def get_tab_content(self):
        dict_chord = { c.name: str(c.get_link(display_type=False)) for c in self.chords }
        content = self.tab_content
        for t in content.find_all('span', class_="js-tab-row js-empty-tab-row"):
            t.decompose()
        for t in content.find_all(style="display: block"):
            t.insert_after('\n')
        for t in content.find_all():
            if " ".join(t.attrs['class']) != "gt-chord js-tab-ch js-tapped":
                t.unwrap()
            else:
                t.replace_with(BeautifulSoup(dict_chord[t.string], "html.parser"))
        return HtmlFormatter.pre("".join(str(t) for t in content.contents))

    @classmethod
    def from_url(cls, url):
        if IN_DEV:
            return None
        soup = urlCache.get_soup(url)
        json_content = json.loads(soup.find('script', type="application/ld+json").string)
        by_artist = json_content['byArtist']
        aggregate_rating = json_content['aggregateRating']
        assert url == json_content['url']
        # Dirty extract of javascript values
        js_prefix = "window.UGAPP.store.page = "
        jscript = soup.find('script', text=re.compile(".*%s.*" % js_prefix)).string
        json_raw = jscript[jscript.find(js_prefix) + len(js_prefix):].replace("'", '"')
        for k in ('applicature', 'tabId', 'tokenName', 'tokenValue'):
            json_raw = json_raw.replace("%s:" % k, '"%s":' % k)
        json_content2 = json.loads(json_raw)
        song_name = json_content['name']
        return cls(
                song_name = song_name,
                artist_name = by_artist['name'],
                url = url,
                artist_url = by_artist['url'],
                rating = aggregate_rating['ratingValue'],
                votes = int(aggregate_rating['reviewCount']),
                tab_content = soup.find('pre', class_="js-tab-fit-to-screen"),
                chords = ChordsFromApplicature.from_json_data(json_content2['applicature'], is_ukulele=False),
                tab_id = json_content2['tabId'])




class ChordsFromGuitarTabsDotCc(AbstractChords):

    def __init__(self, name, is_ukulele, short_content):
        super().__init__(name=name, is_ukulele=is_ukulele, short_content=short_content)
        self.register_and_build_html_anchor()

    def get_specific_content(self):
        return HtmlFormatter.pre(self.short_content)

    @classmethod
    def from_javascript(cls, data, is_ukulele):
        chords = []
        for line in data.splitlines():
            if "chords[" in line:
                lst = line.split('"')
                name, short_content = lst[1], lst[3]
                chords.append(cls(name, is_ukulele=is_ukulele, short_content=short_content) )
        return chords

class GuitarTabFromGuitarTabsDotCc(AbstractGuitarTab):
    prefixes = 'https://www.guitartabs.cc/',

    def __init__(self, song_name, artist_name, type_name, url, version, tab_content, votes, artist_url, chords):
        super().__init__(url, song_name, artist_name, artist_url, tab_id=None)
        self.version = version
        self.votes = votes
        self.type_name = type_name
        self.tab_content = tab_content
        self.chords = chords

    @classmethod
    def from_url(cls, url):
        if IN_DEV:
            return None
        soup = urlCache.get_soup(url)
        titles = soup.find_all(class_="rightbrdr t_title")
        artist_url = urllib.parse.urljoin(url, titles[0].find('a')['href'])
        version = int(str(titles[1].find('b').string))
        type_name = titles[2].find('strong').string
        votes = titles[3].string
        tab_content = soup.find("div", class_="tabcont").find("font", style="line-height:normal").find("pre")
        # Dirty extract of javascript values
        # Song metadata
        song_js_prefix = "window.tpAd('exitCampaign', {songData: "
        song_jscript = soup.find('script', text=re.compile(".*%s.*" % re.escape(song_js_prefix))).string
        song_json_raw = song_jscript[song_jscript.find(song_js_prefix) + len(song_js_prefix):][:-5]
        song_data = json.loads(song_json_raw)
        # Chords content
        chords_jscript = soup.find('script', text=re.compile(".*var chords.*")).string
        return cls(
            song_name = song_data['songName'],
            artist_name = song_data['artistName'],
            url = url,
            artist_url = artist_url,
            type_name = type_name,
            version = version,
            votes = votes,
            tab_content = tab_content,
            chords = ChordsFromGuitarTabsDotCc.from_javascript(chords_jscript, is_ukulele=False))

    def get_link_to_original(self):
        return HtmlFormatter.a(href=self.url, content="%s version %d (%s)" % (self.type_name, self.version, self.votes))

    def get_tab_content(self):
        dict_chord = { c.name: str(c.get_link(display_type=False)) for c in self.chords }
        content = self.tab_content
        for t in content.find_all('span'):
            t.decompose()
        for t in content.find_all('a'):
            t.replace_with(BeautifulSoup(dict_chord[t.string], "html.parser"))
        return HtmlFormatter.pre("".join(str(t) for t in content.contents))


class ChordsFromTabs4Acoustic(AbstractChords):

    def __init__(self, name, is_ukulele, finger_pos):
        short_content = "".join(finger_pos)
        super().__init__(name=name, is_ukulele=is_ukulele, short_content=short_content)
        self.finger_pos = finger_pos
        self.register_and_build_html_anchor()

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
            self.name == other.name and
            self.is_ukulele == other.is_ukulele and
            self.short_content == other.short_content and
            self.finger_pos == self.finger_pos) # Do not use html_anchor

    def get_specific_content(self):
        fret_width = max(len(fret) for fret in self.finger_pos)
        content = "".join(f.rjust(1 + fret_width) for f in self.finger_pos).strip()
        return HtmlFormatter.pre(content)

    @classmethod
    def from_html_div(cls, div, is_ukulele):
        chords = []
        if div:
            for d in div.find_all('div', class_="small-3 column centered"):
                img = d.find('img')
                alt, src = img['alt'], img['src']
                link = d.find('a')
                href, title = link['href'], link['title']
                # TODO: print(alt, src, href, title)
                _, name, fingers = alt.split(" ")
                finger_pos = fingers[1: -1].split(",")
                chords.append(cls(name, is_ukulele=is_ukulele, finger_pos=finger_pos))
        return chords


class GuitarTabFromTabs4Acoustic(AbstractGuitarTab):
    prefixes = 'https://www.tabs4acoustic.com/',

    def __init__(self, song_name, artist_name, url, artist_url, tab_content, chords, author, strummings, key, timesig, tempo):
        super().__init__(url, song_name, artist_name, artist_url, tab_id=None)
        self.tab_content = tab_content
        self.chords = chords
        self.author = author
        self.strummings = strummings
        self.key = key
        self.timesig = timesig
        self.tempo = tempo

    @classmethod
    def from_url(cls, url):
        if IN_DEV:
            return None
        soup = urlCache.get_soup(url)
        breadcrumbs_links = soup.find("div", id="breadcrumbs").find_all('a')
        song_link = breadcrumbs_links[3]
        artist_link = breadcrumbs_links[2]
        artist_str = artist_link.string
        artist_name = artist_str[:artist_str.rfind(" ")]
        album, year, timesig, key, tempo = None, None, None, None, None
        for t in soup.find("div", id="tags").find_all("a"):
            href = t['href']
            if "/album/" in href:
                album = t.string
            elif "/year/" in href:
                year = t.string
            elif "/time-signature/" in href:
                timesig = t.string
            elif "/key/" in href:
                key = t.string
            elif "/tempos/" in href:
                tempo = t.string
        return cls(song_name=song_link.string,
            artist_name=artist_name,
            url=url,
            artist_url=urllib.parse.urljoin(url, artist_link['href']),
            tab_content=soup.find(id='tab_zone'),
            chords=ChordsFromTabs4Acoustic.from_html_div(soup.find(id="crd_zone"), is_ukulele=False),
            author=soup.find("meta", attrs={'name': "author"})["content"],
            strummings=soup.find("div", id="tab_rhy"),
            key=key,
            timesig=timesig,
            tempo=tempo)

    def get_link_to_original(self):
        return HtmlFormatter.a(href=self.url, content="%s from %s" % (self.type_name, self.author))

    def get_tab_content(self):
        dict_chord = { c.name: str(c.get_link(display_type=False)) for c in self.chords }
        if self.tab_content is None:
            return "No tab content"
        content = self.tab_content.find(class_="small-12 column")
        for t in content.find_all('span'):
             t.unwrap()
        for t in content.find_all('a'):
            str_content = list(t.strings)[0]
            if str_content in dict_chord:
                t.replace_with(BeautifulSoup(dict_chord[str_content], "html.parser"))
            else:
                t.unwrap()
        return HtmlFormatter.pre(str(content).replace("\r", "\n"))

    def get_strumming_content(self):
        begin = "Tempo: %s, Time signature: %s\n" % (self.tempo, self.timesig)
        content = self.strummings
        if content is None:
            return "No strumming content"
        for t in content.find_all('h3'):
            t.decompose()
        for t in content.find_all('span', class_="tab_help"):
            t.decompose()
        for t in content.find_all("br"):
            t.replace_with("\n")
        for t in content.find_all():
             t.unwrap()
        return HtmlFormatter.pre(begin + "".join(content.contents).strip())


class GuitarTabFromUltimateGuitar(AbstractGuitarTab):
    prefixes = 'https://tabs.ultimate-guitar.com/', 'https://www.ultimate-guitar.com/'

    def __init__(self, song_name, part, artist_name, url, artist_url, type_name, version, author, rating, votes, is_acoustic, capo, tonality, difficulty, tuning, tab_content, chords, strummings, tab_id):
        super().__init__(url, song_name, artist_name, artist_url, tab_id)
        self.part = part
        self.type_name = type_name
        self.version = version
        self.author = author
        self.rating = rating
        self.votes = votes
        self.is_acoustic = is_acoustic
        self.capo = capo
        self.tonality = tonality
        if difficulty is not None:
            self.difficulty = difficulty
        self.tuning = tuning
        self.tab_content = tab_content
        self.chords = chords
        self.strummings = strummings

    @classmethod
    def from_url(cls, url):
        if IN_DEV:
            return None
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
        song_name = tab['song_name']
        return cls(
            song_name = song_name,
            part = tab['part'].capitalize(),
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
            difficulty = tab_view_meta.get('difficulty', None),
            tuning = tab_view_meta.get('tuning', dict()).get('name', None),
            tab_content = tab_view['wiki_tab'].get('content', ''),
            chords = ChordsFromApplicature.from_json_data(tab_view['applicature'], is_ukulele),
            strummings = Strumming.from_raw_data(tab_view['strummings']),
            tab_id = tab['id'],
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
        content = (self.tab_content
            .replace('\r\n', '\n')
            .replace('[tab]', '')
            .replace('[/tab]', ''))
        content = htmlmodule.escape(content)
        for c in self.chords:
            content = content.replace("[ch]%s[/ch]" % c.name, str(c.get_link(display_type=False)))
        return HtmlFormatter.pre(content)

    def get_strumming_content(self):
        return "".join(str(s.get_html_content()) for s in self.strummings)


class GuitarTabGetter(object):

    @classmethod
    def get_class_for_url(cls, url):
        if not IN_DEV:
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


def get_html_head():
    return HtmlFormatter.head()\
          .add(HtmlFormatter.meta(attrs={'http-equiv': "Content-type", 'content': "text/html;charset=utf-8"}))\
          .add(HtmlFormatter.meta(attrs={'name': "cover", 'content': "empty.jpg"}))\
          .add(HtmlFormatter.title(content="Tabs and Chords"))\
          .add(HtmlFormatter.link(rel="stylesheet", href="default.css", type="text/css"))


def get_html_body(tabs, chords):
    heading = HtmlFormatter.h
    link = HtmlFormatter.a
    body = HtmlFormatter.body()
    body.add(heading(1, "Tabs and Chords"))  # TODO: Add 'generated by'
    body.add(HtmlFormatter.pagebreak)
    # table of content
    body.add(link(id="TOC"))
    body.add("\n")
    body.add(heading(2, "Table of contents"))
    body.add(heading(3, link(href="#tabs", content="Meta table of content")))
    body.add(heading(4, link(href="#toc_tabs", content="Tabs")))
    body.add(heading(5, link(href="#toc_tabs_by_title", content="By title")))
    body.add(heading(5, link(href="#toc_tabs_by_artist", content="By artist")))
    body.add(heading(5, link(href="#toc_tabs_by_diff", content="By difficulty")))
    body.add(heading(5, link(href="#toc_tabs_by_type", content="By type")))
    body.add(heading(4, link(href="#toc_chords", content="Chords")))
    body.add(heading(5, link(href="#toc_chords_by_name", content="By name")))
    body.add(heading(5, link(href="#toc_chords_by_type", content="By type")))
    body.add(heading(3, link(href="#toc_tabs") + link(href="#tabs", content="Tabs")))
    body.add(link(name="toc_tabs"))
    body.add(heading(4, link(name="toc_tabs_by_title") + "By title"))
    for t in sorted(tabs, key=AbstractGuitarTab.by_name):
        body.add(t.get_link())
        body.add(HtmlFormatter.new_line)
    body.add(heading(4, link(name="toc_tabs_by_artist") + "By artist"))
    for artist, tabs_grouped in my_groupby(tabs, key=AbstractGuitarTab.by_artist):
        body.add(heading(5, artist))
        for t in sorted(tabs_grouped, key=AbstractGuitarTab.by_name):
            body.add(t.get_link(display_artist=False))
            body.add(HtmlFormatter.new_line)
    body.add(heading(4, link(name="toc_tabs_by_diff") + "By difficulty"))
    for diff, tabs_grouped in my_groupby(tabs, key=AbstractGuitarTab.by_difficulty):
        body.add(heading(5, diff))
        for t in sorted(tabs_grouped, key=AbstractGuitarTab.by_name):
            body.add(t.get_link())
            body.add(HtmlFormatter.new_line)
    body.add(heading(4, link(name="toc_tabs_by_type") + "By type"))
    for type_name, tabs_grouped in my_groupby(tabs, key=AbstractGuitarTab.by_type):
        body.add(heading(5, type_name))
        for t in sorted(tabs_grouped, key=AbstractGuitarTab.by_name):
            body.add(t.get_link(display_type=False))
            body.add(HtmlFormatter.new_line)
    body.add(heading(3, link(name="toc_chords") + link(href="#chords", content="Chords")))
    body.add(heading(4, link(name="toc_chords_by_name") + "By name"))
    for c in sorted(chords, key=AbstractChords.by_name):
        body.add(c.get_link(display_type=True))
        body.add(HtmlFormatter.new_line)
    body.add(heading(4, link(name="toc_chords_by_type") + "By type"))
    for type_name, chords_grouped in my_groupby(chords, key=AbstractChords.by_type):
        body.add(heading(5, type_name))
        for c in sorted(chords_grouped, key=AbstractChords.by_name):
            body.add(c.get_link(display_type=False))
            body.add(HtmlFormatter.new_line)
    body.add(HtmlFormatter.pagebreak)
    body.add(link(name="start") + "\n")
    # tab content
    body.add(link(name="tabs"))
    for t in sorted(tabs, key=AbstractGuitarTab.by_name):
        body.add(t.get_html_content())
    # chord content
    body.add(link(name="chords"))
    for c in sorted(chords, key=AbstractChords.by_name):
        body.add(c.get_html_content())

    return body


def get_tabs(urls):
    if 1:
        tabs = [GuitarTabGetter.from_url(url) for url in urls]
    elif 0: # For debug purposes
        tabs = GuitarTabGetter.from_list_url('https://www.ultimate-guitar.com/top/tabs')
    elif 0: # For debug purposes
        tabs = []
        for order in ('order=hitsdaily_desc', 'order=hitstotal_desc', 'order=rating_desc', ''):
            for type_ in ('type=all', 'type=official', 'type=chords', 'type=tabs', 'type=guitar%20pro', 'type=power', 'type=bass', 'type=ukulele',  ''):
                url = "https://www.ultimate-guitar.com/top/tabs?" + order + '&' + type_
                tabs.extend(AbstractGuitarTab.from_list_url(url))
    return [t for t in tabs  if t is not None]


def make_book(tabs, chords, htmlfile="wip_book.html", make_mobi=True):
    html = HtmlFormatter.html().add(get_html_head()).add(get_html_body(tabs, chords))
    with open(htmlfile, 'w+') as book:
        book.write(HtmlFormatter.doctype + str(html))
    print("Wrote in %s" % htmlfile)
    if make_mobi:
        subprocess.call([KINDLEGEN_PATH, '-verbose', '-dont_append_source', htmlfile])

tabs = get_tabs(URLS)
chords = AbstractChords.get_all()
make_book(tabs, chords, make_mobi=0)
