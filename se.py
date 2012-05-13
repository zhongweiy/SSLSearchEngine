#! /usr/bin/python

import urllib

def get_page(url):
    try:
        return urllib.urlopen(url).read()
    except:
        return ""

def partition(pages, ranks, start, end):
    pivot = pages[start]
    pivot_pos = start
    for page in pages[pivot_pos + 1:end]:
        if ranks[page] >= ranks[pivot]:
            pages[pivot_pos], page = page, pages[pivot_pos]
            pivot_pos = pivot_pos + 1
    pivot, pages[pivot_pos] = pages[pivot_pos], pivot
    return pivot_pos

def quick_sort(pages, ranks, start, end):
    if end - start < 1:
        return
    pivot_pos = partition(pages, ranks, start, end);
    quick_sort(pages, ranks, start, pivot_pos - 1);
    quick_sort(pages, ranks, pivot_pos + 1, end);
    return

def ordered_search(index, ranks, keyword):
    pages = lookup(index, keyword)
    if not pages:
        print 'no pages found'
        return None
    quick_sort(pages, ranks, 0, len(pages))
    return pages

def get_next_target(page):
    start_link = page.find('<a href=')
    if start_link == -1: 
        return None, 0
    start_quote = page.find('"', start_link)
    end_quote = page.find('"', start_quote + 1)
    url = page[start_quote + 1:end_quote]
    return url, end_quote

def get_all_links(page):
    links = []
    while True:
        url, endpos = get_next_target(page)
        if url:
            links.append(url)
            page = page[endpos:]
        else:
            break
    return links


def union(a, b):
    for e in b:
        if e not in a:
            a.append(e)

def add_page_to_index(index, url, content):
    words = content.split()
    for word in words:
        add_to_index(index, word, url)
        
def add_to_index(index, keyword, url):
    if keyword in index:
        index[keyword].append(url)
    else:
        index[keyword] = [url]
    
def lookup(index, keyword):
    if keyword in index:
        return index[keyword]
    else:
        return None

def crawl_web(seed): # returns index, graph of inlinks
    tocrawl = [seed]
    crawled = []
    graph = {}  # <url>, [list of pages it links to]
    index = {} 
    while tocrawl: 
        page = tocrawl.pop()
        if page not in crawled:
            content = get_page(page)
            add_page_to_index(index, page, content)
            outlinks = get_all_links(content)
            graph[page] = outlinks
            union(tocrawl, outlinks)
            crawled.append(page)
    return index, graph

def compute_ranks(graph):
    d = 0.8 # damping factor
    numloops = 10
    
    ranks = {}
    npages = len(graph)
    for page in graph:
        ranks[page] = 1.0 / npages
    
    for i in range(0, numloops):
        newranks = {}
        for page in graph:
            newrank = (1 - d) / npages
            for node in graph:
                if page in graph[node]:
                    newrank = newrank + d * (ranks[node] / len(graph[node]))
            newranks[page] = newrank
        ranks = newranks
    return ranks

if __name__ == '__main__':
    index, graph = crawl_web('http://udacity.com/cs101x/urank/index.html')
    ranks = compute_ranks(graph)
    
    print ordered_search(index, ranks, 'Hummus')
#>>> ['http://udacity.com/cs101x/urank/kathleen.html', 
#    'http://udacity.com/cs101x/urank/nickel.html', 
#    'http://udacity.com/cs101x/urank/arsenic.html', 
#    'http://udacity.com/cs101x/urank/hummus.html', 
#    'http://udacity.com/cs101x/urank/index.html'] 

    print ordered_search(index, ranks, 'the')
#>>> ['http://udacity.com/cs101x/urank/nickel.html', 
#    'http://udacity.com/cs101x/urank/arsenic.html', 
#    'http://udacity.com/cs101x/urank/hummus.html', 
#    'http://udacity.com/cs101x/urank/index.html']


    print ordered_search(index, ranks, 'babaganoush')
#>>> None
