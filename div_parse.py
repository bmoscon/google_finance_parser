"""
Copyright (C) 2015  Bryant Moscon - bmoscon@gmail.com
 
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to 
 deal in the Software without restriction, including without limitation the 
 rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 sell copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 1. Redistributions of source code must retain the above copyright notice, 
    this list of conditions, and the following disclaimer.

 2. Redistributions in binary form must reproduce the above copyright notice, 
    this list of conditions and the following disclaimer in the documentation 
    and/or other materials provided with the distribution, and in the same 
    place and form as other copyright, license and disclaimer information.

 3. The end-user documentation included with the redistribution, if any, must 
    include the following acknowledgment: "This product includes software 
    developed by Bryant Moscon (http://www.bryantmoscon.org/)", in the same 
    place and form as other third-party acknowledgments. Alternately, this 
    acknowledgment may appear in the software itself, in the same form and 
    location as other such third-party acknowledgments.

 4. Except as contained in this notice, the name of the author, Bryant Moscon,
    shall not be used in advertising or otherwise to promote the sale, use or 
    other dealings in this Software without prior written authorization from 
    the author.


 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
 THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN 
 THE SOFTWARE.
"""




import re


class DivParse(object):
    def __init__(self, html):
        self.html = html
        self.normalized = self._strip_encoded(self._normalize(html, [('<span', '</span')], ('<div', '</div')))

    '''
    converts tags

    s: input html
    from_tags: array of pairs. Each pair should be in format (open tag, close tag)
    to_tag: single pair in format (open tag, to tag)
    '''
    def _normalize(self, s, from_tags, to_tag):
        for p in from_tags:
            s = s.replace(p[0], to_tag[0])
            s = s.replace(p[1], to_tag[1])
        return s

    '''
    same as split, but this one omits empty strings
    '''
    def _split2(self, s, delim=None):
        return [t for t in s.split(delim) if t]


    '''
    gets ID from the ids list. Ignores empty/placeholder IDs
    '''
    def _get_id(self, ids):
        index = -1
        while ids[index] == '*':
            index -= 1
        return ids[index]


    '''
    parses out identifier from HTML tag
    '''
    def _find_id(self, s, ident='class='):
        s = s.replace("\"", '')
        start = s.find(ident)
        s = s[start + 6:]
        return s[:s.find(" ")]

    '''
    remove HTML entities
    ''' 
    def _strip_encoded(self, s):
        if "&" in s:
            s = re.sub(r'&.+;', '', s)
        return s

    '''
    main parser
    '''
    def parse(self, div_id):
        html = self.normalized
        html = html.replace('\n', '')
        html = re.sub(r'>', '>\n', html)
        html = re.sub(r'<', '\n<', html)
    
        parsed = {}
        ids = []
        count = 0
        start = False
        for e in self._split2(html, "\n"):
            if start is False:
                start = ("<div" in e) and (div_id in e) 
                continue
            if "</div>" in e:
                ids.pop()
                count -= 1
            elif "<div" in e:
                if "class" in e:
                    ids.append(self._find_id(e))
                else:
                    ids.append("*")
                count += 1
            else:
                if "<" not in e:
                    curr_id = self._get_id(ids)
                    if curr_id in parsed:
                        parsed[curr_id].append(e)
                    else:
                        parsed[curr_id] = [e]
            if count == 0:
                break
    
        return parsed
