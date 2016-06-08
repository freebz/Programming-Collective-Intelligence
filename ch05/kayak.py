#-*- coding: utf-8 -*-

# 비행편 검색

import time
import urllib2
import xml.dom.minidom

kayakkey='YOUREKYHERE'

def getkayaksession():
  # 세션을 시작할 URL을 생성함
  url='http://www.kayak.com/k/ident/apisession?koken=%s&version=1' % kayakkey

  # 결과로 나온 XML을 파싱함
  doc=xml.dom.minidom.parseString(urllib2.urlopen(url).read())

  #<sid>xxxxxx</sid>를 찾음
  sid=doc.getElementsByTagName('sid')[0].firstChild.data
  return sid


def flightsearch(sid,origin,destination,depart_date):

  # 검색 URL을 생성함
  url='http://www.kayak.com/s/apisearch?basicmode=true&oneway=y&origin=%s' % origin
  
  url+='&destination=%s&depart_date=%s' % (destination,depart_date)
  url+='&return_date=none&depart_time=a&return_time=a'
  url+='&travelers=1&cabin=e&action=doFlights&apimode=1'

  # XML을 얻음
  doc=xml.dom.minidom.parseString(urllib2.urlopen(url).read())

  # 검색 ID를 추출함
  searchid=doc.getElementsByTagName('searchid')[0].firstChild.data

  return searchid


def flightsearchresults(sid,searchid):

  # 앞에 $, 콤마를 없애고 숫자를 실수로 변환함
  def parseprice(p):
    return float(p[1:].replace(',',''))
    
  # 확인 루프를 돔
  while 1:
    time.sleep(2)

    # 확인용 URL을 생성함
    url='http://www.kayak.com/s/basic/flight?'
    url+='searchid=%s&c=5&apimode=1&_sid_=%s&version=1' % (searchid,sid)
    doc=xml.dom.minidom.parseString(urllib2.urlopen(url).read())

    # moredepending 태그를 찾고 true가 아닐 때까지 기다림
    morepending=doc.getElementsByTagName('morepending')[0].firstChild
    if morepending==None or morepending.data=='false': break

  # 이제 완전한 목록을 다운로드함
  url='http://www.kayak.com/s/basic/flight?'
  url+='searchid=%s&c=999&apimode=1&_sid_=%s&version=1' % (searchid,sid)
  doc=xml.dom.minidom.parseString(urllib2.urlopen(url).read())

  # 여러 요소들을 리스트로 얻음
  prices=doc.getElementsByTagName('price')
  departures=doc.getElementsByTagName('depart')
  arrivals=doc.getElementsByTagName('arrive')

  # 이들을 합침
  return zip([p.firstChild.data.split(' ')[1] for p in departures],
             [p.firstChild.data.split(' ')[1] for p in arrivals],
             [parseprice(p.firstChild.data) for p in prices])


def createschedule(people,dest,dep,ret):
  # 이 검색용 세션 id를 얻음
  sid=getkayaksession()
  flights={}

  for p in people:
    name,origin=p

    # 출발 비행편
    searchid=flightsearch(sid,origin,dest,dep)
    flights[(origin,dest)]=flightsearchresults(sid,searchid)

    # 도착 비행편
    searchid=flightsearch(sid,dest,origin,ret)
    flights[(dest,origin)]=flightsearchresults(sid,searchid)

  return flights
