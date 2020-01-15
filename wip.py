import json
import urlfunctions
import operator
import subprocess
import itertools

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
    "https://tabs.ultimate-guitar.com/tab/r-e-m-/losing-my-religion-chords-114345",
    "https://tabs.ultimate-guitar.com/tab/radiohead/karma-police-chords-103398",
    "https://tabs.ultimate-guitar.com/tab/elton-john/rocket-man-chords-10744",
    "https://tabs.ultimate-guitar.com/tab/america/a-horse-with-no-name-chords-59609",
    "https://tabs.ultimate-guitar.com/tab/the-beatles/blackbird-tabs-56997",
    "https://tabs.ultimate-guitar.com/tab/the-beatles/across-the-universe-chords-202167",
    "https://tabs.ultimate-guitar.com/tab/the-beatles/i-want-to-hold-your-hand-chords-457088",
    "https://tabs.ultimate-guitar.com/tab/nirvana/the-man-who-sold-the-world-chords-841325",
    "https://tabs.ultimate-guitar.com/tab/travis/sing-chords-1334",
    "https://tabs.ultimate-guitar.com/tab/travis/sing-tabs-2749659",
]



def string_to_html_id(s):
    # Pretty buggy - in particular for chords
    return "".join(c if c.isalnum() else '-' for c in s)


class GuitarTab(object):
    def __init__(self, song_name, artist_name, url, artist_url, type_name, version, author, rating, votes, capo, tonality, difficulty, tuning, tab_content, chords, html_anchor):
        self.song_name = song_name
        self.artist_name = artist_name
        self.url = url
        self.artist_url = artist_url
        self.type_name = type_name
        self.version = version
        self.author = author
        self.rating = rating
        self.votes = votes
        self.capo = capo
        self.tonality = tonality
        self.difficulty = difficulty
        self.tuning = tuning
        self.tab_content = tab_content
        self.chords = chords
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
        assert url == tab['tab_url']

        if False:  # for debug
            with open('debug.json', 'w+') as f:
                json.dump(tab_view, f, indent=4, sort_keys=True)

        indiv_chords = tab_view['applicature']

        # TODO: strumming
        strummings = tab_view['strummings']
        if strummings and True:
            strum_values = {
                1:   '↓',
                101: '↑',
                202: ' ',
                3:   '↓', # with a small >
                103: '↑', # with a small >
                2:   '↓', # with a small x
                102: '↑', # with a small x
                201: 'x',
                203: '"', # the pause symbol
            }
            # print(tab['song_name'], url)
            for s in strummings:
                # print(s.keys())  # dict_keys(['part', 'denuminator', 'bpm', 'is_triplet', 'measures'])
                # print(s['part'], s['bpm'], s['is_triplet'], s['denuminator'], len(s['measures']))
                values = [m['measure'] for m in s['measures']]
                # print('-'.join(strum_values[v] for v in values))
            # print()

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
            capo = tab_view_meta.get('capo', None),
            tonality = tab_view_meta.get('tonality', None),
            difficulty = tab_view_meta.get('difficulty', 'Unknown'),
            tuning = tab_view_meta.get('tuning', dict()).get('name', None),
            tab_content = tab_view['wiki_tab']['content'],
            chords = indiv_chords if indiv_chords is not None else dict(),
            html_anchor = str(tab['id']) + "-" + string_to_html_id(tab['song_name']),
        )

    @classmethod
    def from_list_url(cls, list_url='https://www.ultimate-guitar.com/top/tabs'):
        soup = urlCache.get_soup(list_url)
        json_content = json.loads(soup.find("div", class_="js-store")["data-content"])
        page_data = json_content['store']['page']['data']
        if True:  # for debug
            with open('debug.json', 'w+') as f:
                json.dump(page_data, f, indent=4, sort_keys=True)
        return [cls.from_url(t['tab_url']) for t in page_data['tabs']]


    def __getitem__(self, k):
        # Temporary - to make transition easier
        return getattr(self, k)


    def get_link(self, display_artist=True, display_type=True):
        artist_name = " - %s" % self.artist_name if display_artist else ""
        type_name = " (%s)" % self.type_name if display_type else ""
        return """<a href="#tab%s">%s%s%s</a><br />
""" % (self.html_anchor, self.song_name, artist_name, type_name)


    def get_header(self):
        return """<a name="tab%s" />
<h2 class="chapter">%s - <a href="%s">%s</a> (%s)</h2>
<a href="%s">%s version %d from %s (rated %f / %d votes)</a><br />
""" % (self.html_anchor, self.song_name, self.artist_url, self.artist_name, self.type_name, self.url, self.type_name, self.version, self.author, self.rating, self.votes)



htmlfile = "wip_book.html"
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

tabs = [GuitarTab.from_url(url) for url in URLS]
tabs.sort(key=operator.itemgetter('song_name'))  # Or any other criteria

all_chords = dict()
for t in tabs:
    for name, details in t.chords.items():
        if name in all_chords:
            assert details == all_chords[name]
        else:
            all_chords[name] = details

chord_anchors = { name: string_to_html_id(name) for name in all_chords }

opt_fields = [
    ('capo', 'Capo'),
    ('tonality', 'Tonality'),
    ('difficulty', 'Difficulty'),
    ('tuning', 'Tuning'),
]

def my_groupby(iterable, key=None):
    return itertools.groupby(sorted(iterable, key=key), key=key)

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
    for t in sorted(tabs, key=operator.itemgetter('song_name')):
        book.write(t.get_link())
    book.write("""<h4><a name="toc_tabs_by_artist" />By artist</h4>\n""")
    for artist, tabs_grouped in my_groupby(tabs, key=operator.itemgetter('artist_name')):
        book.write("""<h5>%s</h5>\n""" % artist)
        for t in sorted(tabs_grouped, key=operator.itemgetter('song_name')):
            book.write(t.get_link(display_artist=False))
    book.write("""<h4><a name="toc_tabs_by_diff" />By difficulty</h4>\n""")
    for diff, tabs_grouped in my_groupby(tabs, key=operator.itemgetter('difficulty')):
        book.write("""<h5>%s</h5>\n""" % diff)
        for t in sorted(tabs_grouped, key=operator.itemgetter('song_name')):
            book.write(t.get_link())
    book.write("""<h4><a name="toc_tabs_by_type" />By type</h4>\n""")
    for type_name, tabs_grouped in my_groupby(tabs, key=operator.itemgetter('type_name')):
        book.write("""<h5>%s</h5>\n""" % type_name)
        for t in sorted(tabs_grouped, key=operator.itemgetter('song_name')):
            book.write(t.get_link(display_type=False))
    book.write("""<h3><a name="toc_chords" /><a href="#chords">Chords</a></h3>\n""")
    for c in sorted(all_chords):
        book.write("""<a href="#chord%s">%s</a><br />
""" % (chord_anchors[c], c))
    book.write(pagebreak)
    book.write(start)
    # tab content
    book.write("""<a name="tabs" />""")
    for t in tabs:
        book.write(t.get_header())
        for opt_field, opt_name in opt_fields:
            val = t[opt_field]
            if val is not None:
                book.write("""%s: %s<br />
""" % (opt_name, val))
        for c, val in sorted(t.chords.items()):
            book.write("""%s<a href="#chord%s">%s</a>: %s<br />
""" % ("&nbsp;" * (10 - len(c)), chord_anchors[c], c, val[0]['id']))
        book.write(pagebreak)
        book.write("""<p class="noindent">
%s
</p>""" % t.tab_content
            .replace(' ', '&nbsp;')
            .replace('\r\n', '<br/>\r\n')
            .replace('[tab]', '')
            .replace('[/tab]', '')
            .replace('[ch]', '')
            .replace('[/ch]', '')
        )
        book.write(pagebreak)
    # chord content
    book.write("""<a name="chords" />""")
    for c in sorted(all_chords):
        values = all_chords[c]
        book.write("""<a name="chord%s" />
<h2>%s</h2>""" % (chord_anchors[c], c))
        for i, v in enumerate(values):
            book.write("%d: %s<br/>\n" % (i, v['id']))
        book.write(pagebreak)

    # footer
    book.write(footer)

print("Wrote in %s" % htmlfile)

subprocess.call([KINDLEGEN_PATH, '-verbose', '-dont_append_source', htmlfile])
