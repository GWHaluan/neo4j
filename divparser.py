from html.parser import HTMLParser
import os
import pathlib
import re
import string
import csv

# disclaimer: don't judge my overflow-driven python development :)

# some globals because it's easier with the scope of class variables and
# inherited methods.
global number_of_tiddlers
number_of_tiddlers = 0

# these are the nodes.
global div_entries
div_entries = []

global current_div
current_div = {}

global in_div
in_div = False

class Divparser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if (tag == "div"):
            # encountered a div start tag
            if (attrs[0][0] == "tiddler" and attrs[1][0] == "tags" and (attrs[1][1] == "stylesheet" or attrs[1][1] == "Twine.image")):
                continue
            else:
                if (attrs[0][0] == "tiddler"):
                    global div_entries
                    global current_div
                    global in_div
                    current_div["incoming"] = attrs[0][1]
                    in_div = True

    def handle_data(self, data):
        global div_entries
        global current_div
        global in_div
        if (in_div):
            # inside div, this is the text node data.
            current_div["text"] = data

    def handle_endtag(self, tag):
        if (tag == "div"):
            # encountered a div end tag.
            global div_entries
            global current_div
            global number_of_tiddlers
            global in_div
            if ("incoming" in current_div.keys() and "text" in current_div.keys()):
                # add it only if the div has both fields.
                div_entries.append(current_div)
                number_of_tiddlers = number_of_tiddlers + 1
            current_div = {}
            in_div = False

parser = Divparser()
filepath= os.path.join("The Terror Aboard The Speedwell 1.2.html")
# test file is short.html, with just a couple of divs:
#filepath= os.path.join("short.html")
file = open(filepath, 'r+')
# .read() because it's easier for a limited file.
the_html = file.read()
parser.feed(the_html)

# get rid of problematic special characters.
def normalize_story_string(story_string):
    normalized_story_string = story_string.replace("“", "\"").replace("”","\"").replace("\"", "\"\"").replace("…", "...").replace("’", "'")
    return normalized_story_string

# create a csv file with the nodes.
f = open("nodes.csv", "w")
the_csv = "incoming,text\n"
for div in div_entries:
    div_inc = normalize_story_string(div["incoming"])
    div_text = normalize_story_string(div["text"])
    div_text_without_html = re.sub('<[^<]+?>', '', div_text)
    the_csv = the_csv +"\""+ div_inc +"\",\""+div_text_without_html+"\"\n"
f.write(the_csv)
f.close()

edges = []

# get the edges from the nodes.
for div in div_entries:
    div_text = div["text"]
    for match in re.finditer(r"\[\[(.*?)\]\]", div_text):
        edges.append([div["incoming"], match.group(1)])

# create a csv file with the edges.
f = open("edges.csv", "w")
the_csv = "from,to\n"
for edge in edges:
    edge_from = normalize_story_string(edge[0])
    edge_to = normalize_story_string(edge[1])
    the_csv = the_csv +"\""+ edge_from +"\",\""+edge_to+"\"\n"
f.write(the_csv)
f.close()
