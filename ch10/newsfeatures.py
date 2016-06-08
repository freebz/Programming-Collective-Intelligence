#-*- coding: utf-8 -*-

# 01: 뉴스 코퍼스

# 정보원 고르기

import feedparser
import re

feedlist=['http://today.reuters.com/rss/topNews',
          'http://today.reuters.com/rss/domesticNews',
          'http://today.reuters.com/rss/worldNews',
          'http://hosted.ap.org/lineups/TOPHEADS-rss_2.0.xml',
          'http://hosted.ap.org/lineups/USHEADS-rss_2.0.xml',
          'http://hosted.ap.org/lineups/WORLDHEADS-rss_2.0.xml',
          'http://hosted.ap.org/lineups/POLITICSHEADS-rss_2.0.xml',
          'http://www.nytimes.com/services/xml/rss/nyt/HomePage.xml',
          'http://www.nytimes.com/services/xml/rss/nyt/International.xml',
          'http://news.google.com/?output=rss',
          'http://feeds.salon.com/salon/news',
          'http://www.foxnews.com/xmlfeed/rss/0,4313,0,00.rss',
          'http://www.foxnews.com/xmlfeed/rss/0,4313,80,00.rss',
          'http://www.foxnews.com/xmlfeed/rss/0,4313,81,00.rss',
          'http://rss.cnn.com/rss/edition.rss',
          'http://rss.cnn.com/rss/edition_world.rss',
          'http://rss.cnn.com/rss/edition_us.rss']



# 정보원 다운로드

def stripHTML(h):
  p=''
  s=0
  for c in h:
    if c=='<': s=1
    elif c=='>':
      s=0
      p+=' '
    elif s==0: p+=c
  return p


def separatewords(text):
  splitter=re.compile('\\W*')
  return [s.lower() for s in splitter.split(text) if len(s)>3]


def getarticlewords():
  allwords={}
  articlewords=[]
  articletitles=[]
  ec=0
  # 모든 피드마다 루프를 돔
  for feed in feedlist:
    f=feedparser.parse(feed)

    # 모든 기사마다 루프를 돔
    for e in f.entries:
      # 동일함 기사는 무시함
      if e.title in articletitles: continue

      # 단어를 추출함
      txt=e.title.encode('utf8')+stripHTML(e.description.encode('utf8'))
      words=separatewords(txt)
      articlewords.append({})
      articletitles.append(e.title)

      # allwords나 articlewords에 이 단어의 출현 횟수를 증가시킴
      for word in words:
        allwords.setdefault(word,0)
        allwords[word]+=1
        articlewords[ec].setdefault(word,0)
        articlewords[ec][word]+=1
      ec+=1
  return allwords,articlewords,articletitles



# 행렬로 변환하기

def makematrix(allw,articlew):
  wordvec=[]

  # 너무 흔한지 않은 공통 단어만 선별함
  for w,c in allw.items():
    if c>3 and c<len(articlew)*0.6:
      wordvec.append(w)

  # 단어 행렬을 만듦
  l1=[[(word in f and f[word] or 0) for word in wordvec] for f in articlew]
  return l1,wordvec




# 02: 이전 방식들

# 베이지안 분류기

# 군집




# 04: 결과 출력하기

from numpy import *
def showfeatures(w,h,titles,wordvec,out='features.txt'):
  outfile=file(out,'w')
  pc,wc=shape(h)
  toppatterns=[[] for i in range(len(titles))]
  patternnames=[]

  # 모든 특성마다 루프를 돔
  for i in range(pc):
    slist=[]

    # 단어와 단어 가중치 목록을 만듦
    for j in range(wc):
      slist.append((h[i,j],wordvec[j]))
    # 단어 목록을 역순 정렬함
    slist.sort()
    slist.reverse()

    # 첫 6개 항목을 출력
    n=[s[1] for s in slist[0:6]]
    outfile.write(str(n)+'\n')
    patternnames.append(n)

    # 이 특성용 기사 목록을 생성함
    flist=[]
    for j in range(len(titles)):
      # 가중치와 함께 기사를 추가함
      flist.append((w[j,i],titles[j]))
      toppatterns[j].append((w[j,i],i,titles[j]))

    # 이 리스트를 역순 정렬함
    flist.sort()
    flist.reverse()

    # 상위 3개 기사를 출력함
    for f in flist[0:3]:
      outfile.write(str[f]+'\n')
    outfile.write('\n')

  outfile.close()
  # 나중을 위해 패턴 이름을 리턴함
  return toppatterns,patternnames




# 기사 출력하기

def showarticles(titles,toppatterns,patternnames,out='articles.txt'):
  outfile=file(out,'w')

  # 모든 기사마다 루프를 돔
  for j in range(len(titles)):
    outfile.write(titles[j].encode('utf8')+'\n')

    # 이 기사의 상위 특성들을 얻고 역순 정렬을 함
    toppatterns[j].sort()
    toppatterns[j].reverse()

    # 상위 세 개 패턴을 출력함
    for i in range(3):
      outfile.write(str(toppatterns[j][i][0])+' '+
                    str(patternnames[toppatterns[j][i][1]])+'\n')
    outfile.write('\n')

  outfile.close()
