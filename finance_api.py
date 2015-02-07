"""
Copyright (C) 2013-2014  Bryant Moscon - bmoscon@gmail.com
 
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


import urllib.request as req
from div_parse import DivParse as DivParse
import re
import datetime

start_string = "google.finance.data = "
stop_string = "}]}};"



def get_quote(exchange, symbol):    
    html = req.urlopen("http://google.com/finance/?q="+exchange+":"+symbol).read()
    html = html.decode("UTF-8", errors='ignore')
    ret = {}
    
    parser = DivParse(html)
    data = parser.parse("id-market-data-div")

    ret['price'] = data['pr'][0]
    if 'chg' in data:
        ret['change'] = data['chg'][0]
        ret['change_pct'] = data['chg'][1][1:-1]
    elif 'chr' in data:
        ret['change'] = data['chr'][0]
        ret['change_pct'] = data['chr'][1][1:-1]
    else:
        ret['change'] = None
        ret['change_pct'] = None
    if 'nwp' in data:
        if 'Close' not in data['nwp'][0]:
            ret['timestamp'] = data['nwp'][1]
            ret['mkt_status'] = 'Open'
        else:
            ret['timestamp'] = None
            ret['mkt_status'] = 'Closed'
    else:
        ret['timestamp'] = None
        ret['mkt_status'] = None

    start = html.find(start_string) + len(start_string)
    stop = html.find(stop_string) + len(stop_string)
    finance_data = html[start:stop]
    
    news_sections = re.findall(r'a:\[(.*?)\],', finance_data)
    news = []
    for section in news_sections:
        url = re.search(r'u:\"(.*?)\"', section).group(1)
        timestamp = re.search(r'tt:\"(.*?)\"' ,section).group(1)
        title = re.search(r't:\"(.*?)\"', section).group(1)
        news.append(News(timestamp, title, url))

    ret['news'] = news
    return ret




class News(object):
    def __init__(self, timestamp, title, url):
        self.t = title
        self.tt = timestamp
        self.url = url

    def info(self):
        return (self.tt, self.t, self.url)

    def __str__(self):
        d = ""
        if self.tt:
            d = datetime.datetime.fromtimestamp(int(self.tt)).strftime("%Y-%m-%d %H:%M:%S")
        return d + " " + self.t + ": " + self.url
    
    def __repr__(self):
        return self.__str__()


