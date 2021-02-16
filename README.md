# degoogle
search Google and extract result urls directly. skip all the click-through links and other sketchiness

contributions welcome

---
install with pip:
`pip install degoogle`

or
```
git clone
cd degoogle
pip install .
```

---
| command line usage | script usage |
|-|-|
| `degoogle "query here"` | make a `dg` object, execute queries with `run()`|

```
usage: degoogle [-h] [-o OFFSET] [-p PAGES] [-t TIME_WINDOW] [-j] query

Search and extract google results.

positional arguments:
  query                 search query

optional arguments:
  -h, --help            show this help message and exit
  -o OFFSET, --offset OFFSET
                        page offset to start from
  -p PAGES, --pages PAGES
                        specify multiple pages
  -t TIME_WINDOW, --time-window TIME_WINDOW
                        time window
  -j, --exclude-junk    exclude junk (yt, fb, quora)

```

*note that `time window` follows a syntax used by google's `tbs` parameter with the `qdr` option (read someone explain how it works [here](https://support.google.com/websearch/thread/7860817?hl=en&msgid=7865083))*

#### examples:
1. find `.txt` files on `.edu` sites within the past `3 months`:

`degoogle "site:edu filetype:txt" -t m3`

![image](https://user-images.githubusercontent.com/47490856/86186391-f69e7880-bb06-11ea-8006-b21a54819beb.png)

2. with one `dg` instance, update `query` in a loop to perform multiple searches:

```
from degoogle import dg
degoogler = dg()
queries = ["site:edu", "site:gov", "filetype:txt"]
for query in queries:
	print(query)
	degoogler.query = query
	results = degoogler.run()
	for result in results:
		print(result)
	print()
```

![image](https://user-images.githubusercontent.com/47490856/86186801-ffdc1500-bb07-11ea-8c64-b539ed4a0579.png)

3. one liner: make `dg` instance (query set in constructor), search across 5months, format + print results, end:

`[print(result['desc'],": ",result['url'],"\n") for result in (dg("intext:'begin rsa' site:*.edu.*",time_window="m5").run())]`

![image](https://user-images.githubusercontent.com/47490856/86186862-30bc4a00-bb08-11ea-9a40-d8b3f96fe387.png)

---


this is an experiment meant to have benefits for both user privacy and broadened osint capabilities

idea: when you search google normally, your results will appear to be direct links to the target site, but what you're really getting is more like this:

> `https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=3ahUWEwjVn87AHIEHeyMAsIQFjAZegQIWARN&url=https%3A%2F%2Fexample.com%2F&usg=BOvWas1Dcw1x9iNBCBHvWL8rWGgJO4`

by using a link like this to access `example.com`, you are providing more information about yourself than necessary. they don't need to know what is done with the results after they are served; their job is done, the click-through is merely a suggestion.

`example.com` can identify that google was your referer; the page you're clicking through from includes your search query as part of the URL, so they probably know what you searched for too. whether or not they're looking at it is another question

if you navigate to `example.com` directly, without a referer like google, `example.com` knows that you have visited, but not where you came from, and google knows even less - even if you originally found out about `example.com` by spotting it in a google search at some point.

google will obviously always know that the search took place, and which results were served, but I prefer to access results directly and not give anyone that click-through confirmation.

there are also utility benefits here for dorking - you might find a super juicy link on page 10 with a bunch of strange parameters cached, but when you follow google's click-through you're redirected to an index page or 404 without even having a chance to copy the link from the result to research more.

there are times where visually inspecting a URL is just as valuable as accessing the link. this tool ganks the good stuff, URL decodes and normalizes, and returns just the scraped URL + description
