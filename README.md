
Collect tabs from various websites and group them into an ebook (for Kindle)

| Source \ Supported features | Basic content | Chord aligned | Chord short description | Chord long description |
|-----------------------------|---------------|---------------|-------------------------|------------------------|
| azchords.com                | Yes           | Yes           |                         |                        |
| boiteachansons.net          | Yes           |               |                         |                        |
| e-chords.com                | Yes           | Yes           | Yes                     | Yes                    |
| guitaretab.com              | Yes           | Yes           | Yes                     | Yes                    |
| guitartabs.cc               | Yes           | Yes           | Yes                     |                        |
| guitartabsexplorer.com      | Yes           | Yes           |                         |                        |
| songsterr.com               |               |               |                         |                        |
| tabs4acoustic.com           | Yes           | Yes           | Yes                     |                        |
| ultimate-guitar.com         | Yes           | Yes           | Yes                     | Yes                    |

The files in output correspond to the output with the file input_examples/list_of_urls_of_tabs.txt.

Usage
-----

python main.py -h
usage: main.py [-h] [--mobi] [--pdf] [--tabfile TABFILE] [--listfile LISTFILE] [--output OUTPUT]

Download tabs and generate HTML and/or PDF and/or Mobi files

optional arguments:
  -h, --help            show this help message and exit
  --mobi, -m            Generate mobi file
  --pdf, -p             Generate pdf file
  --tabfile TABFILE, -t TABFILE
                        File containing URL for tabs
  --listfile LISTFILE, -l LISTFILE
                        File containing URL for lists of tabs
  --output OUTPUT, -o OUTPUT
                        File containing URL for lists of tabs (".html" suffix not required)

