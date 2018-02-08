import requests
import json

data = [{'name': '', 'children': [],'start-count': 0}]
to_call_urls = ['https://ucsd.edu']
called_urls = []
parsed_urls = ['https://ucsd.edu']
broken = 0

def find_first(delim, str, pos):
    m = 1000000
    for delimeter in delim:
        loc = str.find(delimeter, pos)
        if loc != -1:
            m = min(loc, m)
    return m

def parse_url(pieces, base):
    children = []
    if pieces[0] != base:
        subdomain = pieces[0].split(".")[:-2]
        for sub in subdomain:
            if sub != 'www':
                children.append({'name':sub, 'children':[]})
    
    good = True # if a url has a number: "ucsd.edu/resources/1234/image.jpg" ignore it
    if len(pieces) > 1:
        for piece in pieces[1:]:
            piece = piece.strip()
            try:
                k = int(piece)
                good = False
            except:
                if '.' not in piece and piece != "": # prevent ucsd.edu/resources/picture.png
                    children.append({'name':piece, 'children':[]})
    return children, good

def curl_url(url):
    urls = []
    try:
        r = requests.get(url)
    except requests.exceptions.SSLError:
        try:
            r = requests.get(url.replace('http', 'https'))
        except: 
            broken += 1
            print("Broken url %i: %s" %(broken, url))
            return []
    except:
        broken += 1
        print("Broken url %i: %s" %(broken, url))
        return []
    # make response more uniform
    text = r.text.replace("'", '"')
    text = text.replace("https://", "http://")

    pos = 0
    while pos != -1:
        pos = text.find('http://', pos)
        if pos != -1:
            end = find_first(["'", '"', "<", ")", " ", "&", ">"], text, pos)
            if end != -1:
                if text[end-1].isalpha():
                    found_url = text[pos:end]
                else:
                    found_url = text[pos:end-1]
                # don't allow duplicates in a single page
                if "#" in found_url:
                    found_url = found_url[:found_url.find("#")]
                if "?" in found_url:
                    found_url = found_url[:found_url.find("?")]
                if len(found_url) > 0 and found_url[-1] == "/":
                    found_url = found_url[:-1]
                if found_url not in urls and len(found_url) > 0:
                    urls.append(found_url)
                pos += 1
    return urls
            
def parse_urls(urls, base):
    for url in urls:
        # example url: http://students.ucsd.edu/admissions/freshman/index.html
        pieces = url[8:].split('/')     # ignore https://
        if base not in pieces[0] or url in parsed_urls:       
            # eg. ['ucsd.edu', 'admissions'] or ['students.ucsd.edu', 'admissions']
            continue

        children, good = parse_url(pieces, base)
        # children = [{students, []}, {admissions, []}, {freshman, []}]
        if not good:
            continue

        parent = data[0]
        for child in children:
            found = False
            for index, value in enumerate(parent['children']):
                if value['name'] == child['name']:
                    found = True
                    parent = value
            if not found:
                parent['children'].append(child)
                parent = parent['children'][-1]
        parsed_urls.append(url)
        # don't call the same url twice
        if url not in to_call_urls and url not in called_urls:
            if "." not in pieces[-1]:
                to_call_urls.append(url)
            elif ".html" in pieces[-1]:
                to_call_urls.append(url)




def printer(tree, index=0):
    # print name at index indents
    print("\t" * index + "name:%s" %tree['name'])
    # print children recursively
    if len(tree['children']) > 0:
        for child in tree['children']:
            printer(child, index + 1)


base = 'ucsd.edu'
count = 0
while len(to_call_urls) > 0:
    url = to_call_urls.pop()
    print(url)
    found_urls = curl_url(url)
    parse_urls(found_urls, base)
    called_urls.append(url)
    count += 1
    if count > 100:
        with open('data.txt', 'w') as outfile:
            json.dump(data, outfile)
        count = 0
printer(data[0])