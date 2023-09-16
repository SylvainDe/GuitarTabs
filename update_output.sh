# python main.py -m -p -t input_examples/list_of_urls_of_tabs.txt -o output/book
# python main.py -m -p -t input_examples/list_perso.txt -o output/tab_perso.html
# python main.py -m -p -l input_examples/list_of_tops_tabs.txt -o output/toptabs
# python main.py -m -p -l input_examples/list_of_urls_of_list.txt -o output/megabook

python main.py -t input_examples/list_of_urls_of_tabs.txt -o output/book -f &&
python main.py -t input_examples/list_perso.txt -o output/tab_perso.html -f &&
python main.py -l input_examples/list_of_tops_tabs.txt -o output/toptabs -f &&
python main.py -l input_examples/list_of_urls_of_list.txt -o output/megabook -f

# tidy output/book.html
