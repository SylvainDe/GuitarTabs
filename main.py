from tabgetter import GuitarTabGetter
from chords import AbstractChords as Chords
from book import make_book

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

URL_LISTS = [
    "https://www.ultimate-guitar.com/top/tabs",
    "https://www.guitaretab.com/top_tabs.html",
    "https://www.guitartabs.cc/top_tabs.html",
    "https://www.tabs4acoustic.com/en/guitar-tabs/top-guitar-tabs.html",
]


def get_tabs(urls):
    if 1:
        tabs = [GuitarTabGetter.from_url(url) for url in urls]
    elif 0:  # For debug purposes
        tabs = GuitarTabGetter.from_list_url(URL_LISTS[0])
    return [t for t in tabs if t is not None]


tabs = get_tabs(URLS)
chords = Chords.get_all()
make_book(tabs, chords, htmlfile="wip_book.html", make_mobi=0)
