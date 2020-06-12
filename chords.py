import htmlformatter as HtmlFormatter
import re


class Chords(object):

    name_and_type_to_obj = dict()

    def by_name(self):
        return (self.name, self.is_ukulele)

    def by_type(self):
        return "Ukulele" if self.is_ukulele else "Guitar"

    def __init__(self, name, is_ukulele, short_content, long_content):
        self.name = name
        self.is_ukulele = is_ukulele
        self.short_content = short_content
        self.long_content = long_content
        index = self.register()
        self.html_anchor = HtmlFormatter.string_to_html_id("chord%s%s%s" % (
            self.name,
            "-ukulele" if self.is_ukulele else "",
            str(index) if index else ""))

    def __eq__(self, other):
        """Implement comparison.

        Consider Chords object to be identical if all fields conrresponding
        to content is equal. Additional generated data such as html_anchor
        is ignored (comparison is actually used to store chords in lists,
        get their index and thus, compute the html_anchor value)."""
        return (isinstance(other, self.__class__) and
                self.name == other.name and
                self.is_ukulele == other.is_ukulele and
                self.short_content == other.short_content and
                self.long_content == other.long_content)

    def __str__(self):
        return "%s(name:%s, is_ukulele:%d, short_content:%s)" % (
                self.__class__.__name__,
                self.name,
                self.is_ukulele,
                self.short_content)

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
        return [v
                for values in cls.name_and_type_to_obj.values()
                for v in values]

    def get_link(self, display_type):
        type_name = " (Ukulele)" if display_type and self.is_ukulele else ""
        return HtmlFormatter.a(
            href="#" + self.html_anchor,
            title=self.short_content,
            content=self.name + type_name)

    def get_short_html_content(self, alignment=10):
        padding = " " * (alignment - len(self.name))
        link = self.get_link(display_type=False)
        return "%s%s: %s" % (padding, link, self.short_content)

    def get_html_content(self, heading_level):
        type_name = " (Ukulele)" if self.is_ukulele else ""
        return HtmlFormatter.HtmlGroup(
            HtmlFormatter.a(name=self.html_anchor),
            "\n",
            HtmlFormatter.heading(heading_level, "%s%s" % (self.name, type_name)),
            self.long_content,
            HtmlFormatter.pagebreak)

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
        fretboard = [([beg.ljust(width, fill)] + [mid.ljust(width, fill)] * (nb_strings - 2) + [end]) for beg, mid, end, fill in symbols]

        row_start_index = 2
        for j, (fr, fi) in enumerate(zip(frets, fingers)):
            if fr > 0:
                assert fi in [0, 1, 2, 3, 4]
                fi_str = str(fi)
                if fret_offset:
                    fr -= fret_offset - 1
                i = row_start_index + ((fr - 1) * (height + 1)) + (height // 2)
                fretboard[i][j] = fi_str + fretboard[i][j][len(fi_str):]
            elif fr == 0:
                assert fi == 0
            elif fr == -1:
                assert fi == 0
                fi_str = "x"
                i = 0
                fretboard[i][j] = fi_str + fretboard[i][j][len(fi_str):]
            else:
                assert False

        return HtmlFormatter.pre("\n".join("".join(line).rstrip() for line in fretboard))

    @classmethod
    def get_long_content(cls, details):
        fret_details = [["x" if f < 0 else str(f) for f in reversed(detail['frets'])] for detail in details]
        return Chords.pretty_format_chords_variations(fret_details) + \
               cls.format_fingering_detail(details[0])

    @classmethod
    def from_json_data(cls, data, is_ukulele):
        if data:  # May be None or []
            for name, details in data.items():
                short_content = details[0]['id']
                long_content = cls.get_long_content(details)
                yield Chords(name, is_ukulele, short_content, long_content)


class ChordsGetterFromGuitarTabsDotCc():

    @classmethod
    def from_javascript(cls, data, is_ukulele):
        for line in data.splitlines():
            if "chords[" in line:
                # Extract and format data
                lst = line.split('"')
                name, short_content = lst[1], lst[3]
                long_content = Chords.pretty_format_chords_variations([short_content])
                yield Chords(name, is_ukulele, short_content, long_content)


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
                long_content = Chords.pretty_format_chords_variations(variations)

                # Initialise
                yield Chords(name, is_ukulele, short_content, long_content)


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
        long_content = Chords.pretty_format_chords_variations([finger_pos])

        # Initialise
        return Chords(name, is_ukulele, short_content, long_content)

    @classmethod
    def from_html_div(cls, div, is_ukulele):
        if div:
            for d in div.find_all('div', class_="small-3 column centered"):
                yield cls.from_html_inner_div(d, is_ukulele)
