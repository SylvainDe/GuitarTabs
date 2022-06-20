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
    args = parser.parse_args()
    tabs = []
    for filename in args.tabfile:
        for url in get_lines_from_file(filename):
            tabs.append(GuitarTabGetter.from_url(url))
    for filename in args.listfile:
        for url in get_lines_from_file(filename):
            tabs.extend(GuitarTabGetter.from_list_url(url))
    tabs = [t for t in tabs if t is not None]
    book.make_book(
        tabs,
        chords.Chord.get_all(),
        htmlfile="dest/wip_book.html",
        make_mobi=args.mobi,
        make_pdf=args.pdf,
    )


if __name__ == "__main__":
    main()
