import json
import re
RE_P0 = re.compile('<!--.*?-->', re.DOTALL | re.UNICODE)  # comments
RE_P1 = re.compile('<ref([> ].*?)(</ref>|/>)', re.DOTALL | re.UNICODE)  # footnotes
RE_P2 = re.compile("(\n\[\[[a-z][a-z][\w-]*:[^:\]]+\]\])+$", re.UNICODE)  # links to languages
RE_P3 = re.compile("{{([^}{]*)}}", re.DOTALL | re.UNICODE)  # template
RE_P4 = re.compile("{{([^}]*)}}", re.DOTALL | re.UNICODE)  # template
RE_P5 = re.compile('\[(\w+):\/\/(.*?)(( (.*?))|())\]', re.UNICODE)  # remove URL, keep description
RE_P6 = re.compile("\[([^][]*)\|([^][]*)\]", re.DOTALL | re.UNICODE)  # simplify links, keep description
RE_P7 = re.compile('\n\[\[[iI]mage(.*?)(\|.*?)*\|(.*?)\]\]', re.UNICODE)  # keep description of images
RE_P8 = re.compile('\n\[\[[fF]ile(.*?)(\|.*?)*\|(.*?)\]\]', re.UNICODE)  # keep description of files
RE_P9 = re.compile('<nowiki([> ].*?)(</nowiki>|/>)', re.DOTALL | re.UNICODE)  # outside links
RE_P10 = re.compile('<math([> ].*?)(</math>|/>)', re.DOTALL | re.UNICODE)  # math content
RE_P11 = re.compile('<(.*?)>', re.DOTALL | re.UNICODE)  # all other tags
RE_P12 = re.compile('\n(({\|)|(\|-)|(\|}))(.*?)(?=\n)', re.UNICODE)  # table formatting
RE_P13 = re.compile('\n(\||\!)(.*?\|)*([^|]*?)', re.UNICODE)  # table cell formatting
RE_P14 = re.compile('\[\[Category:[^][]*\]\]', re.UNICODE)  # categories
# Remove File and Image template
RE_P15 = re.compile('\[\[([fF]ile:|[iI]mage)[^]]*(\]\])', re.UNICODE)

with open("test.json") as json_file:

    json_data = json.load(json_file)
    #print(json_data[0]['Text'])
    #print(len(json_data))

#json_data[0]['CleanText']= json_data[0]['Text']
#print(json_data['Subject'])
r = 0
while r !=len(json_data):
    y = json_data[r]['Text'].find(json_data[r]['Subject'])
    #print(y)
    t = y + len(json_data[r]['Subject'])
    #print(t)
    #print(json_data[r]['Text'][t])
    if(json_data[r]['Text'][t] == "]"):

        t = y + len(json_data[r]['Subject'])
        json_data[r]['SubjectInText'] = json_data[r]['Text'][y:t]
        print(json_data[r]['Text'][y:t])
    elif(json_data[r]['Text'][t] == ")"):

        z = y+1 + len(json_data[r]['Subject'])

        while json_data[r]['Text'][y + 1] != "]":
            y += 1

        json_data[r]['SubjectInText'] = json_data[r]['Text'][z + 1:y + 1]
        print(json_data[r]['Text'][z + 1:y + 1])

    else:
        z = y+len(json_data[r]['Subject'])
        print(z)
    #json_data[0]['Text'] = json_data[0]['Text'][:z+1] + "html" + json_data[0]['Text'][z+1:]

        while json_data[r]['Text'][y+1] != "]":
            y+=1

    #json_data[0]['Text'] = json_data[0]['Text'][:y+1] + "html" + json_data[0]['Text'][y+1:]
    #print(json_data['Text'])
        json_data[r]['SubjectInText'] = json_data[r]['Text'][z+1:y+1]
        print(json_data[r]['Text'][z+1:y+1])

    def remove_file(s):
        """Remove the 'File:' and 'Image:' markup, keeping the file caption.
        Return a copy of `s` with all the 'File:' and 'Image:' markup replaced by
        their corresponding captions. See http://www.mediawiki.org/wiki/Help:Images
        for the markup details.
        """
        # The regex RE_P15 match a File: or Image: markup
        for match in re.finditer(RE_P15, s):
            m = match.group(0)
            caption = m[:-2].split('|')[-1]
            s = s.replace(m, caption, 1)
        return s



    def remove_template(s):
        """Remove template wikimedia markup.
        Return a copy of `s` with all the wikimedia markup template removed. See
        http://meta.wikimedia.org/wiki/Help:Template for wikimedia templates
        details.
        Note: Since template can be nested, it is difficult remove them using
        regular expresssions.
        """

        # Find the start and end position of each template by finding the opening
        # '{{' and closing '}}'
        n_open, n_close = 0, 0
        starts, ends = [], []
        in_template = False
        prev_c = None
        for i, c in enumerate(iter(s)):
            if not in_template:
                if c == '{' and c == prev_c:
                    starts.append(i - 1)
                    in_template = True
                    n_open = 1
            if in_template:
                if c == '{':
                    n_open += 1
                elif c == '}':
                    n_close += 1
                if n_open == n_close:
                    ends.append(i)
                    in_template = False
                    n_open, n_close = 0, 0
            prev_c = c

        # Remove all the templates
        s = ''.join([s[end + 1:start] for start, end in
                     zip(starts + [None], [-1] + ends)])

        return s



    def remove_markup(text):
        text = re.sub(RE_P2, "", text)  # remove the last list (=languages)
        # the wiki markup is recursive (markup inside markup etc)
        # instead of writing a recursive grammar, here we deal with that by removing
        # markup in a loop, starting with inner-most expressions and working outwards,
        # for as long as something changes.
        text = remove_template(text)
        text = remove_file(text)
        iters = 0
        while True:
            old, iters = text, iters + 1
            text = re.sub(RE_P0, "", text)  # remove comments
            text = re.sub(RE_P1, '', text)  # remove footnotes
            text = re.sub(RE_P9, "", text)  # remove outside links
            text = re.sub(RE_P10, "", text)  # remove math content
            text = re.sub(RE_P11, "", text)  # remove all remaining tags
            text = re.sub(RE_P14, '', text)  # remove categories
            text = re.sub(RE_P5, '\\3', text)  # remove urls, keep description
            text = re.sub(RE_P6, '\\2', text)  # simplify links, keep description only
            # remove table markup
            text = text.replace('||', '\n|')  # each table cell on a separate line
            text = re.sub(RE_P12, '\n', text)  # remove formatting lines
            text = re.sub(RE_P13, '\n\\3', text)  # leave only cell content
            # remove empty mark-up
            text = text.replace('[]', '')
            if old == text or iters > 2:  # stop if nothing changed between two iterations or after a fixed number of iterations
                break

        # the following is needed to make the tokenizer see '[[socialist]]s' as a single word 'socialists'
        # TODO is this really desirable?
        text = text.replace('[', '').replace(']', '')  # promote all remaining markup to plain text


        return text
    json_data[r]['CleanText'] = remove_markup(json_data[r]['Text'])
    #print(remove_markup(json_data[0]['Text']))
    with open('data.json', 'w') as outfile:
        outfile.write(str(json_data[r]))#.encode('utf8')
    print(json_data[r])
    r+=1
