#!/usr/bin/env python3

import argparse
import re
import sys
import urllib.parse

import requests

# todo ####################
# > better junk exclusion
# > infile outfile
# > further filtering
# > max results? made redundant by pages? more useful if/when meaningful filtering options exist beyond junk_strings
# > also just make this not a hot mess anymore. what are exceptions?

class dg():

    # for excluding youtube, quora, facebook results
    # disable with -j flag, or overwrite default by setting exclude_junk's action to store_true
    junk_strings = ['facebook.com/', 'pinterest.com/', 'quora.com/', 'youtube.com/', 'youtu.be/']
    junk_exclusion = r"(?:" + "|".join(junk_strings).replace(".", "\.") + ")"

    def __init__(self, query="", pages=1, offset=0, time_window='a', exclude_junk=True):
        self.query = query
        self.pages = pages
        self.offset = offset
        self.time_window = time_window
        self.exclude_junk = exclude_junk

    # normalize + run search.. supports page, offset, timeframe (tbs parameter)
    def search(self, page):
        if not self.query:
            print("query needs to be set.")
            return
        pg = (self.offset*10) + (page*10) # offset factored in
        # since the digit piece is variable, i can't use argparse.choices :(
        if (self.time_window[0] not in ('a', 'd', 'h', 'm', 'n', 'w', 'y')) or (len(self.time_window) > 1 and not self.time_window[1:].isdigit()):
            # TODO meaningful output
            print("invalid time interval specified.")
            return()

        normalized_query = re.sub(r' |%20', '+', self.query)
        normalized_query = re.sub(r'"|\"', '%22', normalized_query)
        url = f"https://google.com/search?start={pg}&tbs=qdr:{self.time_window}&q={normalized_query}&filter=0"

        return requests.get(url)


    # validate, split, normalize entries.. return list with the extracted url+desc for each search result
    def extract_fields(self, entries):
        valid_entries = []
        search_results = [] # where your final results will live

        for entry in entries: # find segments that ends with one of these pieces i cant remember why right now though
            if entry[-11:] == '</div></h3>' or entry[-6:] == '</div>' or entry[-7:] == '</span>' or entry[-12:] == '</span></h3>':
                valid_entries.append(entry)

        if valid_entries:
            for entry in valid_entries:
                url = ""
                desc = ""
                find_url = re.split('<a href="/url\?q=|&amp;(sa|usg|ved)=', entry)
                for segment in find_url:
                    if segment and segment[0:4] == 'http':
                        # lazy exclusion for some junk results
                        if self.exclude_junk and re.search(self.junk_exclusion, segment):
                            continue
                        url = segment
                if not url: # If no url, don't bother trying to extract a description
                    continue
                else:
                    find_desc = re.split('<[spandiv]{3,4} class=".+?(?=">)">|</[spandiv]{3,4}>', entry)
                    for segment in find_desc:
                        if segment and segment[0] != "<":
                            desc = segment

                # normalize result link
                if url and desc:
                    url = re.sub(r'%20', '+', url)
                    url = urllib.parse.unquote(url)
                    url = re.sub(r'\|', '%7C', url)
                    url = re.sub(r'\"', '%22', url)
                    url = re.sub(r'\>', '%3E', url)
                    url = re.sub(r'\<', '%3C', url)
                    if url[-1] == '.':
                        url = url[0:-1] + '%2E'
                    desc = re.sub(r'&amp;', '&', desc)
                    result = {'desc': desc, 'url': url}
                    search_results.append(result)

        return search_results


    # for each page desired, run google search + grab result entries form page contents.. returns a list of entries
    def process_query(self):
        pages = []
        entries = [] # 1 entry = 1 (url,description)
        # capture a result entry like this:
        match_entry = r'<a href="/url\?q=http.+?(?="><[spandiv]{3,4})"><[spandiv]{3,4} class="[A-Za-z\d ]+">.*?(?=<[spandiv]{3,4})'

        # run the search for each desired page until (pages+offset) reached or until a page with no results is found
        for page in range(0, self.pages):
            r = self.search(page)
            if "did not match any documents" in r.text: # no results on this page, we can skip those that follow
                break
            pages.append(r.text)

        # grab result entries on each page. they will still need to be split into url and description
        for page in pages:
            page_entries = re.findall(match_entry, page) # grab entry matches on this page and append uniques to master entries list
            [entries.append(page_entry) for page_entry in page_entries if page_entry not in entries]

        return entries


    # dg.py "query matchthis -notthis filetype:whatever"
    # search google for your query and return search_results, all cleaned URLs + descriptions from each page
    def run(self):
        try:
            results = self.extract_fields(self.process_query()) # query -> process_query -> search for all pages -> extract_fields -> results
            return results
        except Exception as e:
            print(e)
            return

def parse_args():
    """Parse command line interface arguments."""
    parser = argparse.ArgumentParser(
        description="Search and extract google results.", prog="degoogle"
    )
    parser.add_argument('query', type=str, help='search query')
    parser.add_argument('-o', '--offset', dest='offset', type=int, default=0, help='page offset to start from')
    parser.add_argument('-p', '--pages', dest='pages', type=int, default=1, help='specify multiple pages')
    parser.add_argument('-t', '--time-window', dest='time_window', type=str, default='a', help='time window')
    parser.add_argument('-j', '--exclude-junk', dest='exclude_junk', action='store_false', help='exclude junk (yt, fb, quora)')
    return parser.parse_args()

def main():
    args = parse_args()

################################################################################################
# example/demo output... erase me! VVV

    # usage: make a dg object to run queries through #

    # object using command line args
    dg1 = dg(args.query, args.pages, args.offset, args.time_window, args.exclude_junk)

    # object with query set in constructor. note all other params have default values.. you can overwrite them or leave them alone
    dg2 = dg("dg2.query test")

    # if you want to run a sequence of queries but leave your other params the same,
    # you can use 1 dg instance and loop over your queries, setting googler.query = this_query then calling dg.run()

    search_results = dg1.run()
    #more_results = dg2.run()

    if not search_results:
        print("no results")
    else:
        final_string = "-- %i results --\n\n" % len(search_results)
        for result in search_results:
            final_string += result['desc'] + '\n' + result['url'] + '\n\n'
        if final_string[-2:] == '\n\n':
            final_string = final_string[:-2]
        print(final_string)
################################################################################################

if __name__ == '__main__':
    main()