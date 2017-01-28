#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon

import sys
import urllib
import urllib2
import simplejson as json

from StringIO import StringIO
import gzip

reload(sys) 
sys.setdefaultencoding('utf8')

settings = xbmcaddon.Addon(id='plugin.video.lrytas.lt')

LRYTAS_URL = 'http://tv.lrytas.lt'
LRYTAS_API2_URL = 'http://kolumbus-api.lrytas.lt/query/?count=20&type=Video&'
LRYTAS_LATEST_VIDEOS = LRYTAS_API2_URL +'order=props.pubfromdate_local-&ret_fields=props.categories[0].name__AS__category,props.href__AS__href,props.title__AS__title,props.media[1].otheralternate.ssurl.href__AS__ssurl,props.contributors[0].name__AS__contributors,props.kpm3id__AS__kpm3id,props.summary__AS__summary,props.media[indexof(x.type=%27media%27%20for%20x%20in%20props.media)].otheralternate.1280x720.href__AS__thumb,props.pubfromdate__AS__date&page='
LRYTAS_POPULAR_VIDEOS = LRYTAS_API2_URL + 'order=read_count-&ret_fields=props.categories[0].name__AS__category,props.href__AS__href,props.title__AS__title,props.media[1].otheralternate.ssurl.href__AS__ssurl,props.contributors[0].name__AS__contributors,props.kpm3id__AS__kpm3id,props.summary__AS__summary,props.media[indexof(x.type=%27media%27%20for%20x%20in%20props.media)].otheralternate.1280x720.href__AS__thumb,props.pubfromdate__AS__date&page='
LRYTAS_NEWS_VIDEOS = LRYTAS_API2_URL + 'order=props.pubfromdate_local-&ret_fields=props.categories[0].name__AS__category,props.href__AS__href,props.title__AS__title,props.media[1].otheralternate.ssurl.href__AS__ssurl,props.contributors[0].name__AS__contributors,props.kpm3id__AS__kpm3id,props.summary__AS__summary,props.media[indexof(x.type=%27media%27%20for%20x%20in%20props.media)].otheralternate.1280x720.href__AS__thumb,props.pubfromdate__AS__date&categoryterm=%2Flrytas%2Fvideo%2Fzinios*&page='
LRYTAS_VIDEOTEKA = 'http://kolumbus-api.lrytas.lt//sections.json'
LRYTAS_LIVE = 'http://ssb.lrytas.lt/live/smil:lrytas.smil/playlist.m3u8'
LRYTAS_EPG = 'http://tv2.lrytas.lt/api/?what=tvprog'
LRYTAS_IMG = 'http://img.lrytas.lt/show_foto/?id=%s&s=6&f=5'

from HTMLParser import HTMLParser
import htmlentitydefs

class HTMLTextExtractor(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    self.result = [ ]

  def handle_data(self, d):
    self.result.append(d)

  def handle_charref(self, number):
    codepoint = int(number[1:], 16) if number[0] in (u'x', u'X') else int(number)
    self.result.append(unichr(codepoint))

  def handle_entityref(self, name):
    codepoint = htmlentitydefs.name2codepoint[name]
    self.result.append(unichr(codepoint))

  def get_text(self):
    return u''.join(self.result)

def html_to_text(html):
    s = HTMLTextExtractor()
    s.feed(html)
    return s.get_text()

def getParameters(parameterString):
  commands = {}
  splitCommands = parameterString[parameterString.find('?') + 1:].split('&')
  for command in splitCommands:
    if (len(command) > 0):
      splitCommand = command.split('=')
      key = splitCommand[0]
      value = splitCommand[1]
      commands[key] = value
  return commands

def getURL(url):
  
  request = urllib2.Request(url)
  request.add_header('Accept-encoding', 'gzip')
  response = urllib2.urlopen(request)
  if response.info().get('Content-Encoding') == 'gzip':
    buf = StringIO(response.read())
    f = gzip.GzipFile(fileobj=buf)
    return f.read()  
  
  return response.read()

def build_main_directory():
  
  listitem = xbmcgui.ListItem('Naujausi video')
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=1&page=1', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem('Populiariausi video')
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=2&page=1', listitem = listitem, isFolder = True, totalItems = 0)

  listitem = xbmcgui.ListItem('Žinios')
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=3&page=1', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem('Gyvai')
  listitem.setProperty('IsPlayable', 'true')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=4&page=1', listitem = listitem, isFolder = False, totalItems = 0)
  
  listitem = xbmcgui.ListItem('Videoteka')
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=5&page=1', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem('Paieška')
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=7&page=1', listitem = listitem, isFolder = True, totalItems = 0)

  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(515)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def latest_videos(page=1):
  loadData(LRYTAS_LATEST_VIDEOS + str(page))

def popular_videos(page=1):
  loadData(LRYTAS_POPULAR_VIDEOS + str(page))

def news_videos(page=1):
  loadData(LRYTAS_NEWS_VIDEOS + str(page))

def loadData(url, m_url=None):
  
  html = getURL(url)
  js = json.loads(html)
  
  if 'result' not in js:
    return
  
  for video in js['result']:
    listitem = xbmcgui.ListItem(video['title'])
    listitem.setProperty('IsPlayable', 'true')
    listitem.setThumbnailImage(video['thumb'])
    
    info = { 'title': video['title'], 'plot': html_to_text(video['summary']), 'aired' : video['date'], 'genre' : video['category']}
    
    listitem.setInfo(type = 'video', infoLabels = info )
    
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = video['ssurl'], listitem = listitem, isFolder = False, totalItems = 0)
    
  if len(js['result']) >= 20:
    listitem = xbmcgui.ListItem("[Daugiau... ] %d" % page)
    listitem.setProperty('IsPlayable', 'false')
      
    u = {}
    u['mode'] = mode
    u['page'] = page + 1
    if m_url:
      u['url'] = m_url
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?' + urllib.urlencode(u), listitem = listitem, isFolder = True, totalItems = 0)
  
  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(503)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def liveError():
  dialog = xbmcgui.Dialog()
  ok = dialog.ok( "Lietuvo ryto TV" , 'Nepavyko paleisti vaizdo įrašo!' ) 
  

def live():
  
  html = getURL(LRYTAS_EPG)
  
  js = json.loads(html)
  
  if 's' not in js:
    liveError()
    return
  
  data = js['s'][0]
  
  if not data:
    liveError()
    return
  
  listitem = xbmcgui.ListItem(data['PAVADINIMAS'])
  listitem.setPath(LRYTAS_LIVE)
  listitem.setThumbnailImage(LRYTAS_IMG % data['FOTO_ID'])
  
  info = { 'title': data['PAVADINIMAS'], 'plot': data['TEKSTAS'], 'aired' : data['DAT'], 'genre' : data['SKILTIS_PAV']}
  listitem.setInfo(type = 'video', infoLabels = info )
  
  xbmcplugin.setResolvedUrl(handle = int(sys.argv[1]), succeeded = True, listitem = listitem)
  

def tv_shows():
  
  html = getURL(LRYTAS_VIDEOTEKA)
  
  js = json.loads(html)
  
  if 'categories' not in js:
    return
  
  for tv in js['categories']:
    
    if tv['parentTerm'] != '/lrytas/video/laidos':
      continue
    
    u = {}
    u['mode'] = 6
    u['url'] = tv['term']
    u['page'] = 1
    listitem = xbmcgui.ListItem(tv['label'])
    listitem.setProperty('IsPlayable', 'false')
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?' + urllib.urlencode(u), listitem = listitem, isFolder = True, totalItems = 0)
    
  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(515)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def loadShow(url, page):
  
  loadData(LRYTAS_LATEST_VIDEOS + str(page) + '&categoryterm=' + urllib.quote_plus(url) + '*')

def search(url=None, page=1):
  key = url
  
  if not key:
    dialog = xbmcgui.Dialog()
    key = dialog.input('Vaizdo įrašo paieška', type=xbmcgui.INPUT_ALPHANUM).strip()
    
  if not key:
    return
  
  loadData(LRYTAS_LATEST_VIDEOS + str(page) + '&q=' + urllib.quote_plus(key), key)


# **************** main ****************

path = sys.argv[0]
params = getParameters(sys.argv[2])
mode = None
page = None
url = None

try:
  mode = int(params["mode"])
except:
  pass

try:
  page = int(params["page"])
except:
  pass

try:
  url = urllib.unquote_plus(params["url"])
except:
  pass

if mode == None:
  build_main_directory()
elif mode == 1:
  latest_videos(page)
elif mode == 2:
  popular_videos(page)
elif mode == 3:
  news_videos(page)
elif mode == 4:
  live()
elif mode == 5:
  tv_shows()
elif mode == 6:
  loadShow(url, page)
elif mode == 7:
  search(url, page)
  