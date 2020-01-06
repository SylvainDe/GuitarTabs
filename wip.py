import json
import urlfunctions

urlCache = urlfunctions.UrlCache("cache")
for url in [
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
"https://tabs.ultimate-guitar.com/tab/neil-young/heart-of-gold-chords-56555",
"https://tabs.ultimate-guitar.com/tab/joan-baez/diamonds-and-rust-chords-1044414",
        ]:
    print(url)
    soup = urlCache.get_soup(url)
    title = soup.find("meta", property="og:title")["content"]
    print(title)
    desc = soup.find("meta", property="og:description")["content"]
    print(desc)
    json_content = json.loads(soup.find("div", class_="js-store")["data-content"])
    print(json_content.keys())
    print(json.dumps(json_content, indent=4, sort_keys=True))
    break

