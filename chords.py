import htmlformatter as HtmlFormatter
import re
import tabs

# Having a list of tab using a given chord may be only slightly useful
# to the user but it can be highly useful to the developer trying to
# debug logic related to chords.
DISPLAY_TAB_LIST_IN_CHORD_DESCR = True


class RawChordData(object):
    """Raw data describing a chord object."""

    def __init__(self, name, is_ukulele, short_content, long_content):
        self.name = name
        self.is_ukulele = is_ukulele
        self.short_content = short_content
        self.long_content = long_content
        self.str_id = "%s%s" % (name, "-ukulele" if is_ukulele else "")

    def __eq__(self, other):
        """Implement comparison."""
        return (
            isinstance(other, self.__class__)
            and self.name == other.name
            and self.is_ukulele == other.is_ukulele
            and self.short_content == other.short_content
            and self.long_content == other.long_content
            and self.str_id == other.str_id
        )

    def __str__(self):
        return "%s(name:%s, is_ukulele:%d, short_content:%s)" % (
            self.__class__.__name__,
            self.name,
            self.is_ukulele,
            self.short_content,
        )

    def get_title(self, display_type):
        type_name = " (Ukulele)" if display_type and self.is_ukulele else ""
        return "%s%s" % (self.name, type_name)

    def get_type(self):
        return "Ukulele" if self.is_ukulele else "Guitar"


class Chord(object):
    """Chord wraps RawChordData and adds features which are not really
    relevant to the Chord data as such but more relevant to the way we use
    it. In particular:
     - Chord objects are reused from different contexts (different tabs
    using the same chord)
     - An HTML anchor is generated for each chord. In order to do so, chords
    are provided an index to be able to remove the ambiguity between chords
    with similar descriptions but different underlying data (usually, the same
    chord from different sources)."""

    id_to_obj = dict()

    def by_name(self):
        return (self.raw.name, self.raw.is_ukulele)

    def by_type(self):
        return self.raw.get_type()

    @classmethod
    def get_from(cls, name, is_ukulele, short_content, long_content):
        """Return a Chord object, either from the cache or newly created.

        As we want to use a single Chord reference from different places,
        a cache is created and queried to be able to either reuse already
        existing object or to create a new one."""
        raw = RawChordData(name, is_ukulele, short_content, long_content)
        data = cls.id_to_obj.setdefault(raw.str_id, [])
        for i, obj in enumerate(data):
            if raw == obj.raw:
                return obj
        new_obj = cls(raw, len(data))
        data.append(new_obj)
        return new_obj

    def __init__(self, raw, index):
        """Constructor for Chord object. (Use Chord.get_from instead)."""
        self.raw = raw
        self.html_anchor = HtmlFormatter.string_to_html_id(
            "chord%s%s" % (self.raw.str_id, str(index) if index else "")
        )
        self.tabs = []

    def add_tab(self, tab):
        self.tabs.append(tab)

    @property
    def name(self):
        return self.raw.name

    def __eq__(self, other):
        """Implement comparison.."""
        return (
            isinstance(other, self.__class__)
            and self.raw == other.raw
            and self.html_anchor == other.html_anchor
            and self.tabs == other.tabs
        )

    @classmethod
    def get_all(cls):
        return [v for values in cls.id_to_obj.values() for v in values]

    def get_link(self, display_type):
        return HtmlFormatter.a(
            href="#" + self.html_anchor,
            title=self.raw.short_content,
            content=self.raw.get_title(display_type),
        )

    def get_short_html_content(self, alignment=10):
        padding = " " * (alignment - len(self.raw.name))
        link = self.get_link(display_type=False)
        return "%s%s: %s" % (padding, link, self.raw.short_content)

    def get_tab_list(self):
        if not DISPLAY_TAB_LIST_IN_CHORD_DESCR or not self.tabs:
            return ""
        sorted_tabs = sorted(self.tabs, key=tabs.AbstractGuitarTab.by_name_and_url)
        return HtmlFormatter.HtmlGroup(
            "From:\n",
            HtmlFormatter.ul(
                HtmlFormatter.HtmlGroup(
                    *(
                        HtmlFormatter.li(
                            HtmlFormatter.HtmlGroup(
                                t.get_link(display_type=False, display_src=False),
                                " from ",
                                t.get_link_to_original(t.website),
                            )
                        )
                        for t in sorted_tabs
                    )
                )
            ),
        )

    def get_html_content(self, heading_level):
        return HtmlFormatter.HtmlGroup(
            HtmlFormatter.a(name=self.html_anchor),
            "\n",
            HtmlFormatter.heading(heading_level, self.raw.get_title(display_type=True)),
            self.raw.long_content,
            self.get_tab_list(),
            HtmlFormatter.pagebreak,
        )

    @classmethod
    def pretty_format_chords_variations(cls, fret_details):
        """Format variations of a same chords: handle indices and alignment."""
        idx_width = len(str(len(fret_details)))
        fret_width = max(len(f) for frets in fret_details for f in frets)
        return HtmlFormatter.pre(
            "\n".join("%s:%s" % (
                str(i).rjust(idx_width),
                "".join(f.rjust(1 + fret_width) for f in frets)
            )
            for i, frets in enumerate(fret_details, start=1)))


class ChordsGetterFromApplicature():

    @classmethod
    def format_fingering_detail(cls, fingering):
        show_finger_number_on_tab = False
        show_finger_number_below_tab = True
        frets = list(reversed(fingering['frets']))
        fingers = list(reversed(fingering['fingers']))
        fret_offset = fingering['fret']
        nb_strings = len(frets)
        nb_frets = 5
        width = 2
        height = 1

        # Drawing:   (beg, mid, end, fill)
        empty =      ("",  "",  " ", " ")
        top =        ("┍", "┯", "┑", "━")
        mid =        ("├", "┼", "┤", "─")
        bottom =     ("└", "┴", "┘", "─")
        vert_lines = ("│", "│", "│", " ")
        symbols = []
        symbols.append(empty)
        symbols.append(top)
        for i in range(nb_frets - 1):
            symbols.extend([vert_lines] * height + [mid])
        symbols.extend([vert_lines] * height + [bottom])
        if show_finger_number_below_tab:
            symbols.append(empty)
        fretboard = [([beg.ljust(width, fill)] + [mid.ljust(width, fill)] * (nb_strings - 2) + [end]) for beg, mid, end, fill in symbols]

        def set_fretboard_content_by_position(s, i, j):
            fretboard[i][j] = s + fretboard[i][j][len(s):]

        row_start_index = 2
        for j, (fr, fi) in enumerate(zip(frets, fingers)):
            if fr > 0:
                assert fi in [0, 1, 2, 3, 4]
                if fret_offset:
                    fr += 2 - fret_offset
                i = row_start_index + ((fr - 1) * (height + 1)) + (height // 2)
                fi_str = str(fi) if show_finger_number_on_tab else "O"
                set_fretboard_content_by_position(fi_str, i, j)
                if show_finger_number_below_tab:
                    set_fretboard_content_by_position(str(fi), -1, j)
            elif fr == 0:
                assert fi == 0
            elif fr == -1:
                assert fi == 0
                set_fretboard_content_by_position("x", 0, j)
            else:
                assert False

        return HtmlFormatter.pre("\n".join("".join(line).rstrip() for line in fretboard))

    @classmethod
    def get_long_content(cls, details):
        fret_details = [["x" if f < 0 else str(f) for f in reversed(detail['frets'])] for detail in details]
        return Chord.pretty_format_chords_variations(fret_details) + \
               cls.format_fingering_detail(details[0])

    @classmethod
    def from_json_data(cls, data, is_ukulele):
        if data:  # May be None or []
            for name, details in data.items():
                if details:
                    short_content = details[0]['id']
                    long_content = cls.get_long_content(details)
                    yield Chord.get_from(name, is_ukulele, short_content, long_content)


class ChordsGetterFromGuitarTabsDotCc():

    @classmethod
    def from_javascript(cls, data, is_ukulele):
        for line in data.splitlines():
            if "chords[" in line:
                # Extract and format data
                lst = line.split('"')
                name, short_content = lst[1], lst[3]
                long_content = Chord.pretty_format_chords_variations([short_content])
                yield Chord.get_from(name, is_ukulele, short_content, long_content)


class ChordsGetterFromEChords():

    @classmethod
    def from_javascript(cls, data, is_ukulele):
        for line in data.split(";"):
            m = re.match("chords\[\"(.*)\"\].variations = '(.*)'", line)
            if m:
                # Extract data
                name, variations = m.groups()

                # Format data
                variations = [v.split(",") for v in variations.split()]
                short_content = "".join(variations[0])
                long_content = Chord.pretty_format_chords_variations(variations)

                # Initialise
                yield Chord.get_from(name, is_ukulele, short_content, long_content)


class ChordsGetterFromTabs4Acoustic():

    @classmethod
    def from_html_inner_div(cls, div, is_ukulele):
        # Extract data
        img = div.find('img')
        alt, src = img['alt'], img['src']
        link = div.find('a')
        if link:
            href, title = link['href'], link['title']
        else:
            href, title = None, None
        # TODO: print(alt, src, href, title)
        _, name, fingers = alt.split(" ")
        finger_pos = fingers[1: -1].split(",")

        # Format data
        short_content = "".join(finger_pos)
        long_content = Chord.pretty_format_chords_variations([finger_pos])

        # Initialise
        return Chord.get_from(name, is_ukulele, short_content, long_content)

    @classmethod
    def from_html_div(cls, div, is_ukulele):
        if div:
            for d in div.find_all('div', class_="small-3 column centered"):
                yield cls.from_html_inner_div(d, is_ukulele)
