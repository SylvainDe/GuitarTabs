from tabgetter import GuitarTabGetter
import chords
import book


def get_lines_from_file(filename):
    with open(filename) as f:
        for line in f:
            if not line.startswith("#"):
                yield line.strip()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Download tabs and generate HTML and/or PDF and/or Mobi files"
    )
    parser.add_argument("--mobi", "-m", action="store_true", help="Generate mobi file")
    parser.add_argument("--pdf", "-p", action="store_true", help="Generate pdf file")
    parser.add_argument(
        "--tabfile",
        "-t",
        action="append",
        help="File containing URL for tabs",
        default=[],
    )
    parser.add_argument(
        "--listfile",
        "-l",
        action="append",
        help="File containing URL for lists of tabs",
        default=[],
    )
    parser.add_argument(
        "--output",
        "-o",
        help='File containing URL for lists of tabs (".html" suffix not required)',
        default="output/book",
    )
    parser.add_argument(
        "--name",
        "-n",
        help="Name for for generated book",
        default="Tabs and Chords",
    )
    # TODO: Add options for content such as cover
    args = parser.parse_args()
    tabs = []
    for filename in args.tabfile:
        lines = list(get_lines_from_file(filename))
        nb_urls = str(len(lines))
        for i, url in enumerate(lines, start=1):
            tab = GuitarTabGetter.from_url(url, "%d/%s" % (i, nb_urls))
            if tab is not None:
                tabs.append(tab)
    for filename in args.listfile:
        lines = list(get_lines_from_file(filename))
        nb_urls = str(len(lines))
        for i, url in enumerate(lines, start=1):
            tabs.extend(GuitarTabGetter.from_list_url(url, "%d/%s" % (i, nb_urls)))
    book.make_book(
        tabs,
        chords.Chord.get_all(),
        base_filename=args.output,
        make_mobi=args.mobi,
        make_pdf=args.pdf,
        title=args.name,
    )


if __name__ == "__main__":
    main()
