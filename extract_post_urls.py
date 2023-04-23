import argparse

from bs4 import BeautifulSoup

def get_arg_parser():
    parser = argparse.ArgumentParser(description='Extracts community post URLs from a dump of the community post tab.')
    parser.add_argument('communitypage',
                        help='An HTML file containing a dump of the list of community posts')
    parser.add_argument('-o', '--outfile',
                        help='Output file')
   # parser.add_argument('--cookies',
     #                   help='Cookies needed to access members posts (does nothing rn)')
    return parser

def read_tag_soup(filepath):
    with open(filepath) as infile:
        html = infile.read()

    return BeautifulSoup(html, "html.parser")
    
    
def parse_links(tag_soup):
    a_tags = tag_soup.select('a[aria-label]')
    return [atag.get("href") for atag in a_tags if atag.get("aria-label") == "Go to post detail"]

def print_full_links(links, baseurl="https://www.youtube.com"):
    for l in links:
        print(f"{baseurl}{l}")

def write_full_links(outfilepath, links, baseurl="https://www.youtube.com"):
    with open(outfilepath, 'w') as outfile:
        for l in links:
            outfile.write(f"{baseurl}{l}\n")

if __name__ == "__main__":
    args = get_arg_parser().parse_args()
    tag_soup = read_tag_soup(args.communitypage)
    links = parse_links(tag_soup)
    if args.outfile:
        write_full_links(args.outfile, links)
    else:
        print_full_links(links)


""" id="published-time-text" """