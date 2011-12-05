# -*- coding: utf-8 -*-

import sys
import urllib
import urlparse
import re
import simplejson

class TedHelper(object):
    def __init__(self, urlTed):
        self._url = validate_url(urlTed)
        self._html_ted = urllib.urlopen(self._url).read()
        self._videoPara = self.get_video_parameters()
        self._sub_languages = self.get_languages()

    def download_srt_from_ted_url(self, languageCode):
        urlSub = 'http://www.ted.com/talks/subtitles/id/%d/lang/%s/format/text' \
                % (int(self._videoPara['ti'].strip('"')), languageCode)

        jsonFile = urllib.urlopen(urlSub)

        jsonDict = simplejson.loads(jsonFile.readline())
        jsonList = jsonDict['captions']

        self._introDuration = int(self._videoPara['introDuration'])

        srtList = map(self.map_srt_from_json, jsonList, range(len(jsonList)))

        srtName = 'sub_%s.srt' %languageCode
        srtFile = open(srtName, 'w')
        for eachEntry in srtList:
            srtFile.write(eachEntry.encode('UTF-8'))

    def map_srt_from_json(self, entryDict, index):
        startTime = entryDict['startTime']+ self._introDuration
        duration = entryDict['duration']
        content = entryDict['content']
        return '%d\n%s --> %s\n%s\n\n' % (index+1, get_time(startTime),\
            get_time(startTime+ duration), content)

    def get_video_parameters(self):
        var = re.search('flashVars = {\n([^}]+)}', self._html_ted)
        if var is not None:
            var = var.group(1)
        else:
            return None

        var = [eachVar.strip().strip(',') for eachVar in var.split('\n')]
        var = var[:len(var)-2]
        var = [eachVar.split(':', 1) for eachVar in var]

        return dict(var)

    def get_languages(self):
        pattern = re.compile(r'<select name="languageCode" id="languageCode">([\s\S]*?)</select>')
        var = pattern.search(self._html_ted)
        if var is not None:
            var = var.group(1)
        else:
            return None
    
        var = [eachOption.strip() for eachOption in var.split('\n')]
        var = var[:len(var)-1]
        var = [eachOption[15:-9] for eachOption in var]
        var = [re.split('".*?>', eachOption) for eachOption in var]

        return dict(var)

def validate_url(url):
    parseRes = urlparse.urlparse(url)
    if parseRes.scheme == '':
        url = 'http://%s' % url
    
    return url

def get_time(millseconds):
    hours = millseconds/ 3600000
    millseconds -= hours* 3600000
    minutes = millseconds/ 60000
    millseconds -= minutes* 60000
    seconds = millseconds/ 1000
    millseconds -= seconds* 1000
    return '%02d:%02d:%02d,%03d' % (hours, minutes, seconds, millseconds)

def main():
    if len(sys.argv)< 2:
        ted_url = raw_input('Copy&Paste Ted URL: ')
    elif len(sys.argv)< 3:
        ted_url = sys.argv[1]
    else:
        ted_url = sys.argv[1]
        languageCode = sys.argv[2]

    teddownloader = TedHelper(ted_url)
    if 'languageCode' not in dir():
        print 'Languages Available:'
        languages = teddownloader.get_languages()
        for each in languages:
            print '%s(%s)' %(languages[each], each)
        languageCode = raw_input('Enter Language Code(en for example)')
    
    teddownloader.download_srt_from_ted_url(languageCode)
    

if __name__ == '__main__':
    # http://www.ted.com/talks/johnny_lee_demos_wii_remote_hacks.html
    # www.ted.com/talks/johnny_lee_demos_wii_remote_hacks.html
    main()
