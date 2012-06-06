#!/usr/bin/env python3.2
"""Sitemap parser - parses titles from sitemap.xml"""
import sys, urllib.request, re, threading, queue, time
sitemapurl = 'http://www.zadornov.net/sitemap.xml'

THREAD_LIMIT = 10
output = list()
jobs = queue.Queue(0)
 
def parse_array(text, beg_tag, end_tag):
    """Parse all text between tags."""
    pattern = beg_tag+b'(.*?)'+end_tag
    matches = re.findall(pattern, text, re.DOTALL)
    return matches
 
def return_between(text, beg_tag, end_tag):
    """Return text between tags."""
    start = text.find(beg_tag)+len(beg_tag)
    end = text.find(end_tag, start)
    return text[start:end]
 
def parse_sitemap(url):
    """get all urls between loc"""
    try:
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.7.62 Version/11.01'),
                            ('Accept', 'text/html, application/xml;q=0.9, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*;q=0.1'),
                            ('Accept-Language', 'ru-RU,ru;q=0.9,en;q=0.8'),
                            ('Accept-Encoding','identity')]
        sitemap = opener.open(url).read()
        #sitemap = urllib.request.urlopen(url).read()
    except urllib.error.HTTPError as e:
        print("ERROR CODE "+str(e.code))
        return False
    start = b'<loc>'
    end = b'</loc>'
    urls = parse_array(sitemap, start, end)
    return urls
 
def parse_page(url):
    """get title"""
    global output
    url = url.replace(b'\\',b'/')
    print ('Downloading', url.decode('utf-8'))
    try:
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.7.62 Version/11.01'),
                            ('Accept', 'text/html, application/xml;q=0.9, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*;q=0.1'),
                            ('Accept-Language', 'ru-RU,ru;q=0.9,en;q=0.8'),
                            ('Accept-Encoding','identity')]
        page = opener.open(url.decode('utf-8')).read()
        if b'<title>' in page:
            title = return_between(page, b'<title>', b'</title>')
            output.append(title.strip()+b';'+url)
    except urllib.error.HTTPError as e2:
        output.append(str(e2.code).encode('ascii')+b';'+url)

 
def thread():
    while True:
        try:
            url = jobs.get(False)
        except queue.Empty:
            return
        parse_page(url)
 
#check command line
try:
    sitemapurl = sys.argv[1].strip()
except:
    pass

domainr = re.compile("http://([A-z0-9-.]+)/")
m = domainr.search(sitemapurl)
if not m:
    print("domain not found! use link as http://.../")
    sys.exit()
map_file = m.group(1)+".csv"
print(map_file)
foldr = re.compile("http://([A-z0-9-.]+)/?(.+)?/")
m2 = foldr.search(sitemapurl)
if not m2:
    print("could not get folder")
    sys.exit()

page_urls = parse_sitemap(m2.group(0)+"sitemap.xml")
#page_urls = parse_sitemap(sitemapurl)
if not page_urls:
    print("error on net")
    sys.exit()
print ('Total', len(page_urls), 'in sitemap')
#sys.exit() 
#Making job queue
for url in page_urls:
    jobs.put(url.strip())
 
#Running threads
for n in range(THREAD_LIMIT):
    t = threading.Thread(target=thread)
    t.start()
while threading.active_count() > 1:
    time.sleep(1) # Wait to finish

print("saving to file: "+map_file)

with open(map_file, 'wb') as fout:
    fout.write(b'\n'.join(output))