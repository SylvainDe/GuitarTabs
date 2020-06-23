import itertools
import hashlib
import urllib.parse
import re
import json
import operator
import html as htmlmodule

from bs4 import BeautifulSoup

import urlfunctions
import htmlformatter as HtmlFormatter
import chords

urlCache = urlfunctions.UrlCache("cache")

# Debug flag to be able to disable retrieval of all tabs and corresponding logging
# to be able to focus on a single getter class
IN_DEV = False


def clean_whitespace(string):
    return "\n".join(l.rstrip() for l in string.splitlines())


class AbstractGuitarTab(object):

    by_name = operator.attrgetter('song_name')
    by_artist = operator.attrgetter('artist_name')
    by_difficulty = operator.attrgetter('difficulty')
    by_type = operator.attrgetter('type_name')
    by_src = operator.attrgetter('src')
    by_name_and_url = operator.attrgetter('song_name', 'url')

    def __init__(self, url, song_name, artist_name, artist_url, chords, tab_id):
        self.url = url
        self.song_name = song_name
        self.artist_name = artist_name
        self.artist_url = artist_url
        self.chords = chords
        self.type_name = "Tab"
        self.part = ""
        self.is_acoustic = False
        self.capo = None
        self.tonality = None
        self.key = None
        self.difficulty = "Unknown"
        self.tuning = None
        self.src = self.__class__.website
        if tab_id is None:
            tab_id = abs(int(hashlib.sha512(url.encode('utf-8')).hexdigest(), 16)) % (10 ** 8)
        self.html_anchor = HtmlFormatter.string_to_html_id("tab" + str(tab_id) + "-" + song_name)
        for c in chords:
            c.add_tab(self)

    def get_link(self, display_artist=True, display_type=True, display_src=True, prefix=""):
        part = " " + self.part if self.part else ""
        artist_name = " - %s" % self.artist_name if display_artist else ""
        from_ = ""
        if display_type or display_src:
            acoustic = "Acoustic " if self.is_acoustic else ""
            type_name = "%s%s" % (acoustic, self.type_name) if display_type else ""
            src = "from %s" % self.src if display_src else ""
            space = " " if (display_type and display_src) else ""
            from_ = " (" + type_name + space + src + ")"
        return HtmlFormatter.a(href="#" + self.html_anchor, content="%s%s%s%s%s" % (prefix, self.song_name, part, artist_name, from_))

    def get_header(self, heading_level):
        acoustic = "Acoustic " if self.is_acoustic else ""
        artist_link = HtmlFormatter.a(href=self.artist_url, content=self.artist_name)
        return HtmlFormatter.HtmlGroup(
            HtmlFormatter.a(name=self.html_anchor),
            "\n",
            HtmlFormatter.heading(heading_level, "%s - %s (%s%s)" % (self.song_name, artist_link, acoustic, self.type_name)),
            self.get_link_to_original(content=self.get_text_for_link_to_original()),
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
        sorted_chords = sorted(self.chords, key=chords.Chord.by_name)
        if not sorted_chords:
            return ""
        alignment = max(len(c.name) for c in sorted_chords)
        return HtmlFormatter.pre("\n".join(c.get_short_html_content(alignment) for c in sorted_chords))

    def get_html_content(self, heading_level):
        return HtmlFormatter.HtmlGroup(
            self.get_header(heading_level),
            self.get_optional_field_content(),
            self.get_strumming_content(),
            self.get_chord_content(),
            HtmlFormatter.pagebreak,
            self.get_tab_content(),
            self.get_link(prefix="Back to top of ", display_type=False, display_src=False),
            HtmlFormatter.new_line,
            HtmlFormatter.pagebreak)

    def get_link_to_original(self, content):
        return HtmlFormatter.a(href=self.url, content=content)

    def get_text_for_link_to_original(self):
        return "From %s" % self.website

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
        print("%s.from_url(%s) returned []" % (cls.__name__, list_url))
        return []


class GuitarTabFromGuitarTabDotCom(AbstractGuitarTab):
    prefixes = 'https://www.guitaretab.com/',
    website = 'guitaretab.com'

    def __init__(self, song_name, artist_name, url, artist_url, rating, votes, tab_content, chords, tab_id):
        super().__init__(url, song_name, artist_name, artist_url, chords, tab_id)
        self.rating = rating
        self.votes = votes
        self.tab_content = tab_content

    def get_text_for_link_to_original(self):
        return "Version from %s (rated %s / %d votes)" % (self.website, self.rating, self.votes)

    def get_tab_content(self):
        dict_chord = {c.name: str(c.get_link(display_type=False)) for c in self.chords}
        content = self.tab_content
        for t in content.find_all('span', class_="js-tab-row js-empty-tab-row"):
            t.decompose()
        for t in content.find_all(style="display: block"):
            t.insert_after('\n')
        for t in content.find_all():
            if " ".join(t.attrs.get('class', [])) != "gt-chord js-tab-ch js-tapped":
                t.unwrap()
            else:
                t.replace_with(BeautifulSoup(dict_chord[t.string], "html.parser"))
        content = "".join(str(t) for t in content.contents)
        return HtmlFormatter.pre(clean_whitespace(content))

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
            song_name=song_name,
            artist_name=by_artist['name'],
            url=url,
            artist_url=by_artist['url'],
            rating=aggregate_rating['ratingValue'],
            votes=int(aggregate_rating['reviewCount']),
            tab_content=soup.find('pre', class_="js-tab-fit-to-screen"),
            chords=list(chords.ChordsGetterFromApplicature.from_json_data(json_content2['applicature'], is_ukulele=False)),
            tab_id=json_content2['tabId'])

    @classmethod
    def from_list_url(cls, list_url):
        soup = urlCache.get_soup(list_url)
        return [cls.from_url(urllib.parse.urljoin(list_url, a['href']))
                for a in soup.find_all("a", class_="gt-link gt-link--primary")]


class GuitarTabFromGuitarTabsExplorer(AbstractGuitarTab):
    prefixes = 'https://www.guitartabsexplorer.com'
    website = 'guitartabsexplorer.com'

    def __init__(self, song_name, artist_name, url, artist_url, rating, votes, tab_content, chords, author, tab_id):
        super().__init__(url, song_name, artist_name, artist_url, chords, tab_id)
        self.rating = rating
        self.votes = votes
        self.tab_content = tab_content
        self.author = author

    def get_tab_content(self):
        content = self.tab_content
        for t in content.find_all('img'):
            t.decompose()
        for t in content.find_all('h2'):
            t.decompose()
        for t in content.find_all("div", class_="gptslot"):
            t.decompose()
        for t in content.find_all(class_="hide-for-print"):
            t.decompose()
        for t in content.find_all("span", class_="dropt"):
            for t2 in t.find_all("span"):
                t2.decompose()
        for t in content.find_all():
            t.unwrap()
        content = "".join(str(t) for t in content.contents)
        return HtmlFormatter.pre(clean_whitespace(content))

    def get_text_for_link_to_original(self):
        return "%s version from %s (rated %s / %d votes)" % (self.website, self.author, self.rating, self.votes)

    @classmethod
    def from_url(cls, url):
        if IN_DEV:
            return None
        soup = urlCache.get_soup(url)
        song_name = soup.find_all("span", itemprop="name")[-1].string
        json_content = json.loads(soup.find('script', type="application/ld+json").string)
        by_artist = json_content['byArtist']
        aggregate_rating = json_content.get('aggregateRating', {'ratingValue': 0, 'ratingCount': 0})
        author = json_content.get('author', {'name': 'Unknown'})
        return cls(
            song_name=song_name,
            artist_name=by_artist['name'],
            url=url,
            author=author['name'],
            artist_url=by_artist['url'],
            rating=aggregate_rating['ratingValue'],
            votes=int(aggregate_rating['ratingCount']),
            tab_content=soup.find('article'),
            chords=[],
            tab_id=None)


class GuitarTabFromGuitarTabsDotCc(AbstractGuitarTab):
    prefixes = 'https://www.guitartabs.cc/',
    website = 'guitartabs.cc'

    def __init__(self, song_name, artist_name, type_name, url, version, tab_content, votes, artist_url, chords):
        super().__init__(url, song_name, artist_name, artist_url, chords, tab_id=None)
        self.version = version
        self.votes = votes
        self.type_name = type_name
        self.tab_content = tab_content

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
        chords_jscript_tag = soup.find('script', text=re.compile(".*var chords.*"))
        chords_jscript = chords_jscript_tag.string if chords_jscript_tag else ""
        return cls(
            song_name=song_data['songName'],
            artist_name=song_data['artistName'],
            url=url,
            artist_url=artist_url,
            type_name=type_name,
            version=version,
            votes=votes,
            tab_content=tab_content,
            chords=list(chords.ChordsGetterFromGuitarTabsDotCc.from_javascript(chords_jscript, is_ukulele=False)))

    def get_text_for_link_to_original(self):
        return "%s version %d from %s (%s)" % (self.type_name, self.version, self.website, self.votes)

    def get_tab_content(self):
        dict_chord = {c.name: str(c.get_link(display_type=False)) for c in self.chords}
        content = self.tab_content
        for t in content.find_all('span'):
            t.decompose()
        for t in content.find_all('a'):
            t.replace_with(BeautifulSoup(dict_chord[t.string], "html.parser"))
        content = "".join(str(t) for t in content.contents)
        return HtmlFormatter.pre(clean_whitespace(content))

    @classmethod
    def from_list_url(cls, list_url):
        soup = urlCache.get_soup(list_url)
        return [cls.from_url(urllib.parse.urljoin(list_url, a['href']))
                for a in soup.find_all("a", class_="ryzh22")]


class GuitarTabFromTabs4Acoustic(AbstractGuitarTab):
    prefixes = 'https://www.tabs4acoustic.com/',
    website = 'tabs4acoustic.com'

    def __init__(self, song_name, artist_name, url, artist_url, tab_content, chords, author, strummings, key, timesig, tempo):
        super().__init__(url, song_name, artist_name, artist_url, chords, tab_id=None)
        self.tab_content = tab_content
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
        return cls(
            song_name=song_link.string,
            artist_name=artist_name,
            url=url,
            artist_url=urllib.parse.urljoin(url, artist_link['href']),
            tab_content=soup.find(id='tab_zone'),
            chords=list(chords.ChordsGetterFromTabs4Acoustic.from_html_div(soup.find(id="crd_zone"), is_ukulele=False)),
            author=soup.find("meta", attrs={'name': "author"})["content"],
            strummings=soup.find("div", id="tab_rhy"),
            key=key,
            timesig=timesig,
            tempo=tempo)

    def get_text_for_link_to_original(self):
        return "%s from %s" % (self.type_name, self.author)

    def get_tab_content(self):
        dict_chord = {c.name: str(c.get_link(display_type=False)) for c in self.chords}
        if self.tab_content is None:
            return HtmlFormatter.pre("No tab content")
        content = self.tab_content.find(class_="small-12 column")
        for t in content.find_all('span'):
            t.unwrap()
        for t in content.find_all('a'):
            v = dict_chord.get(list(t.strings)[0], None)
            if v is not None:
                t.replace_with(BeautifulSoup(v, "html.parser"))
            else:
                t.unwrap()
        for t in content.find_all('img'):
            t.unwrap()
        return HtmlFormatter.pre(clean_whitespace(str(content)))

    def get_strumming_content(self):
        begin = "Tempo: %s, Time signature: %s\n" % (self.tempo, self.timesig)
        content = self.strummings
        if content is None:
            return HtmlFormatter.pre("No strumming content")
        for t in content.find_all('h3'):
            t.decompose()
        for t in content.find_all('span', class_="tab_help"):
            t.decompose()
        for t in content.find_all("br"):
            t.replace_with("\n")
        for t in content.find_all():
            t.unwrap()
        return HtmlFormatter.pre(begin + "".join(content.contents).strip())

    @classmethod
    def from_list_url(cls, list_url):
        soup = urlCache.get_soup(list_url)
        hrefs = []
        content = soup.find(id="page_content")
        table = content.find("table")
        if table:
            for tr in table.find_all("tr"):
                tds = tr.find_all("td")
                if tds:
                    hrefs.append(tds[1].find("a")["href"])
            return [cls.from_url(urllib.parse.urljoin(cls.prefixes[0], href)) for href in hrefs]
        else:
            for a in content.find_all("a"):
                hrefs.append(a["href"])
        return [cls.from_url(urllib.parse.urljoin(cls.prefixes[0], href)) for href in hrefs]


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
            1: (' ', '↓'),
            101: (' ', '↑'),
            202: (' ', ' '),
            3: ('>', '↓'),  # arrow with a small >
            103: ('>', '↑'),  # arrow with a small >
            2: ('x', '↓'),  # arrow with a small x
            102: ('x', '↑'),  # arrow with a small x
            201: (' ', 'x'),
            203: (' ', '𝄥'),  # the pause symbol
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
                    ((str(1 + i // coef) if i % coef == 0 else '&' if (2 * i % coef == 0) else '') for i in numbers)]
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


class GuitarTabFromUltimateGuitar(AbstractGuitarTab):
    prefixes = 'https://www.ultimate-guitar.com/', 'https://tabs.ultimate-guitar.com/'
    website = 'ultimate-guitar.com'

    def __init__(self, song_name, part, artist_name, url, artist_url, type_name, version, author, rating, votes, is_acoustic, capo, tonality, difficulty, tuning, tab_content, chords, strummings, tab_id):
        super().__init__(url, song_name, artist_name, artist_url, chords, tab_id)
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
            song_name=song_name,
            part=tab['part'].capitalize(),
            artist_name=tab['artist_name'],
            url=url,
            artist_url=tab['artist_url'],
            type_name=tab['type_name'],
            version=tab['version'],
            author=tab['username'],
            rating=tab['rating'],
            votes=tab['votes'],
            is_acoustic=tab['recording']['is_acoustic'],
            capo=tab_view_meta.get('capo', None),
            tonality=tab_view_meta.get('tonality', None),
            difficulty=tab_view_meta.get('difficulty', None),
            tuning=tab_view_meta.get('tuning', dict()).get('name', None),
            tab_content=tab_view['wiki_tab'].get('content', ''),
            chords=list(chords.ChordsGetterFromApplicature.from_json_data(tab_view['applicature'], is_ukulele)),
            strummings=Strumming.from_raw_data(tab_view['strummings']),
            tab_id=tab['id'],
        )

    @classmethod
    def from_list_url(cls, list_url):
        soup = urlCache.get_soup(list_url)
        json_content = json.loads(soup.find("div", class_="js-store")["data-content"])
        page_data = json_content['store']['page']['data']
        if 'tabs' in page_data:
            return [cls.from_url(t['tab_url']) for t in page_data['tabs']]
        elif 'results' in page_data:
            return [cls.from_url(t['tab_url']) for t in page_data['results'] if "&" not in t['tab_url']]
        elif 'songbook' in page_data:
            return [cls.from_url(t['tab']['tab_url']) for t in page_data['songbook']['tabs']]
        else:
            raise NotImplementedError

    def get_text_for_link_to_original(self):
        return "%s version %d from %s (rated %f / %d votes)" % (self.type_name, self.version, self.author, self.rating, self.votes)

    def get_tab_content(self):
        dict_chord = {c.name: str(c.get_link(display_type=False)) for c in self.chords}
        content = (self.tab_content
                   .replace('\r\n', '\n')
                   .replace('[tab]', '')
                   .replace('[/tab]', '')
                   .replace('>', '&gt;')
                   .replace('<', '&lt;'))
        for chord, link in dict_chord.items():
            content = content.replace("[ch]%s[/ch]" % chord, link)
        return HtmlFormatter.pre(clean_whitespace(content))

    def get_strumming_content(self):
        return "".join(str(s.get_html_content()) for s in self.strummings)


class GuitarTabFromEChords(AbstractGuitarTab):
    prefixes = 'https://www.e-chords.com/',
    website = 'e-chords.com'

    def __init__(self, url, song_name, artist_name, artist_url, chords, tab_id, key, capo, difficulty, tab_content, type_name):
        super().__init__(url, song_name, artist_name, artist_url, chords, tab_id)
        self.key = key
        self.capo = capo
        self.difficulty = difficulty
        self.tab_content = tab_content
        self.type_name = type_name

    def get_tab_content(self):
        dict_chord = {c.name: str(c.get_link(display_type=False)) for c in self.chords}
        content = self.tab_content
        for t in content.find_all():
            if t.name == 'u':
                v = dict_chord.get(t.string, None)
                if v is not None:
                    t.replace_with(BeautifulSoup(v, "html.parser"))
                else:
                    t.unwrap()
            else:
                t.unwrap()
        return HtmlFormatter.pre("".join(str(t) for t in content.contents))

    @classmethod
    def from_url(cls, url):
        if IN_DEV:
            return None
        if url in ("https://www.e-chords.com/chords/lewis-capaldi/someone-you-loved", "https://www.e-chords.com/tabs/ewan-dobson/time-2"):
            return None
        soup = urlCache.get_soup(url)
        # Dirty extract of javascript values
        js_prefix = "var base_href = "
        jscript = soup.find('script', text=re.compile(".*%s.*" % js_prefix)).string
        raw_data = {k:v for (k, v) in (
            re.findall('var ([^ ]*) = "([^"]*)";', jscript) +
            re.findall("var ([^ ]*) = '([^']*)';", jscript) +
            re.findall("var ([^ ]*) = ([^'\";]*);", jscript))
        }
        chords_jscript = jscript.splitlines()[-2]
        instrument = raw_data['typeInstrument']
        type_name = raw_data['tipoTab']
        if instrument != type_name:
            type_name = instrument + " " + type_name
        is_ukulele = (instrument == 'ukulele')
        return cls(
            url=url,
            song_name=raw_data['title'],
            artist_name=raw_data['artist'],
            artist_url= "https://www.e-chords.com/" + raw_data['cod_artist'],
            tab_id=raw_data['idSong'],
            key=raw_data['strKey'],
            capo=raw_data['keycapo'],
            difficulty=soup.find("span", style="color: #999;font-style:italic").string,
            tab_content=soup.find("pre", id="core"),
            chords=list(chords.ChordsGetterFromEChords.from_javascript(chords_jscript, is_ukulele)),
            type_name=type_name.title(),
        )

    @classmethod
    def from_list_url(cls, list_url):
        soup = urlCache.get_soup(list_url)
        hrefs = [p.find("a")["href"] for p in soup.find_all("p", class_="nome-musica")]
        if not hrefs:
            results = soup.find(id="results")
            hrefs = [p.find("a")["href"] for p in results.find_all("p", class_="h1")]
        return [cls.from_url(h) for h in hrefs]


class GuitarTabFromSongsterr(AbstractGuitarTab):
    prefixes = 'https://www.songsterr.com/',
    website = 'songsterr.com'

    def __init__(self, url, song_name, artist_name, artist_url, chords, tab_id, tab_content, difficulty, capo):
        super().__init__(url, song_name, artist_name, artist_url, chords, tab_id)
        self.tab_content = tab_content
        self.difficulty = difficulty
        self.capo = capo

    @classmethod
    def from_url(cls, url):
        if IN_DEV:
            return None
        soup = urlCache.get_soup(url)

        json_content = json.loads(soup.find("script", id="state").string)
        json_meta = json_content['meta']
        json_route = json_content['route']
        json_track = json_content['track']
        json_data = json_content['data']
        # json_lyrics = json_data['lyrics']
        # if json_lyrics is not None:
        #     print(len(json_lyrics))
        #     for lyr in json_lyrics:
        #         for beats in lyr['beats']:
        #             for lyr2 in beats['lyrics']:
        #                 print(lyr2['text'])
        # Note: tuning is available: json_track['tuning']
        # Note: bpm is available: json_data['part']['automations']['tempo']
        return cls(
            url=url,
            song_name=json_meta["title"],
            artist_name=json_meta["artist"],
            artist_url="https://www.songsterr.com/a/wsa/foo-bar-a%s" % (json_meta["artistId"]),
            chords=[],
            tab_id="s%st%s" % (json_route["songId"], json_route["partId"]),
            tab_content=soup.find('section', id="tablature"),
            difficulty=json_track['difficulty'],
            capo=json_data["part"]["capo"],
    )

    @classmethod
    def from_list_url(cls, list_url):
        soup = urlCache.get_soup(list_url)
        script_state = soup.find("script", id="state")
        if script_state:
            json_content = json.loads(script_state.string)
            json_search_songs = json_content["search"]["songs"]
            urls = ["https://www.songsterr.com/a/wsa/foo-bar-s%st%d" % (s["songId"], 0) for s in json_search_songs]
            return [cls.from_url(url) for url in urls]
        return [cls.from_url(urllib.parse.urljoin(list_url, a['href'])) for a in soup.find_all("a", class_="tab-link")]


class GuitarTabFromAzChords(AbstractGuitarTab):
    prefixes = 'https://www.azchords.com/',
    website = 'azchords.com'

    @classmethod
    def from_url(cls, url):
        if IN_DEV:
            return None
        soup = urlCache.get_soup(url)
        return None
