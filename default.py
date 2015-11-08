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
import re

from StringIO import StringIO
import gzip

reload(sys) 
sys.setdefaultencoding('utf8')

settings = xbmcaddon.Addon(id='plugin.video.lrytas.lt')

LRYTAS_URL = 'http://tv.lrytas.lt'
LRYTAS_LATEST_VIDEOS = LRYTAS_URL + '/api/?what=new&sid=1%2C2&kiek=50&page='
LRYTAS_POPULAR_VIDEOS = LRYTAS_URL + '/api/?what=pop&tema=0&d=7&sid=1&kiek=45&page='
LRYTAS_NEWS_VIDEOS = LRYTAS_URL + '/api/?what=new&sid=1&kiek=50&page='
LRYTAS_VIDEOTEKA_VIDEOS = LRYTAS_URL + '/api/?what=new&page=%d&sid=3&tema=%s&kiek=45'
LRYTAS_SEARCH = LRYTAS_URL + '/api/?q=%s&what=search&page=%d&kiek=45'
LRYTAS_VIDEOTEKA = LRYTAS_URL + '/archyvas/'
LRYTAS_LIVE = LRYTAS_URL + '/live/'
LRYTAS_IMG = 'http://img.lrytas.lt/show_foto/?id=%s&s=6&f=5'

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
  
  if 's' not in js:
    return
  
  for video in js['s']:
    listitem = xbmcgui.ListItem(video['PAVADINIMAS'])
    listitem.setProperty('IsPlayable', 'true')
    listitem.setThumbnailImage(LRYTAS_IMG % video['FOTO_ID'])
    
    info = { 'title': video['PAVADINIMAS'], 'plot': video['TEKSTAS'], 'aired' : video['DAT'], 'genre' : video['SKILTIS_PAV']}
    
    listitem.setInfo(type = 'video', infoLabels = info )
    
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = video['VIDEO_FILE_URL'], listitem = listitem, isFolder = False, totalItems = 0)
    
  if len(js['s']) > 30:
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
  
def live():
  
  html = getURL(LRYTAS_LIVE)
  
  url = None
  thumb = None
  title = None
  
  parts = re.findall('<video id="content_video"[^<>]*poster="([^"]*)"[^<>]*><source src="([^"]*)"', html, re.DOTALL)
  
  if parts:
    thumb = parts[0][0]
    url = parts[0][1]
    
  parts = re.findall('<div class=\'desc\'><h1>([^<]*)<\/h1>', html, re.DOTALL)
  if parts:
    title = parts[0]
  
  if not url:
    dialog = xbmcgui.Dialog()
    ok = dialog.ok( "Lietuvo ryto TV" , 'Nepavyko paleisti vaizdo įrašo!' )
    return
  
  if not title:
    title = "Lietuvo ryto TV"
  
  listitem = xbmcgui.ListItem(label = title)
  listitem.setPath(url)
  if thumb:
    listitem.setThumbnailImage(thumb)
  xbmcplugin.setResolvedUrl(handle = int(sys.argv[1]), succeeded = True, listitem = listitem)
  

def tv_shows():
  
  html = getURL(LRYTAS_VIDEOTEKA)
  
  section = re.findall('<section class=\'archive\'>(.*?)</section>', html, re.DOTALL)
  if not section:
    return
  
  tv_items = re.findall('<a href=\'([^\']*)\'>([^<]*)</a>', section[0], re.DOTALL)
  
  for tv in tv_items:
    u = {}
    u['mode'] = 6
    u['url'] = tv[0]
    u['page'] = 1
    listitem = xbmcgui.ListItem(tv[1].strip())
    listitem.setProperty('IsPlayable', 'false')
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?' + urllib.urlencode(u), listitem = listitem, isFolder = True, totalItems = 0)
    
  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(515)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def loadShow(url, page):
  
  data_tema = settings.getSetting(url)

  if not data_tema:

    html = getURL(LRYTAS_URL + url)
    
    data_tema = re.findall('<a[^<>]*data-tema=\'(\d*)\'', html, re.DOTALL)
    
    if not data_tema:
      return
    
    data_tema = data_tema[0]
    settings.setSetting(url, data_tema)
    
  loadData(LRYTAS_VIDEOTEKA_VIDEOS % (page, data_tema), url)

def search(url=None, page=1):
  key = url
  
  if not key:
    dialog = xbmcgui.Dialog()
    key = dialog.input('Vaizdo įrašo paieška', type=xbmcgui.INPUT_ALPHANUM).strip()
    
  if not key:
    return
  
  loadData(LRYTAS_SEARCH % (urllib.quote_plus(key), page), key)


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
  