import htmlformatter as HtmlFormatter

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



