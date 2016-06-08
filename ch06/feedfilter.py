# -*- coding: utf-8 -*-

# 08: 블로그 피드 필터링

import feedparser
import re

# 블로그 피드 URL을 담은 파일 이름을 받아 글을 분류함
def read(feed,classifier):
  # 피드 내의 글을 얻고 루프를 돔
  f=feedparser.parse(feed)
  for entry in f['entries']:
    print
    print '-----'
    # 글의 내용을 출력함
    print 'Title:     '+entry['title'].encode('utf-8')
    print 'Publisher: '+entry['publisher'].encode('utf-8')
    print
    print entry['summary'].encode('utf-8')

    # 모든 텍스트를 결합하여 분류용 항목을 만듦
    fulltext='%s\n%s\n%s' % (entry['title'],entry['publisher'],entry['summary'])

    # 현재 분류에 대한 추정 값을 출력함
    #print 'Guess: '+str(classifier.classify(fulltext))
    # 현재 분류에 대한 최적 수정을 출력함
    print 'Guess: '+str(classifier.classify(entry))

    # 사용자에게 분류가 맞는지 묻고 학습함
    cl=raw_input('Enter category: ')
    #classifier.train(fulltext,cl)
    classifier.train(entry,cl)




# 09: 향상된 특성 검출법

def entryfeatures(entry):
  splitter=re.compile('\\W*')
  f={}

  # 제목에서 단어를 추출해서 특성 주석을 붙임
  titlewords=[s.lower() for s in splitter.split(entry['title'])
              if len(s)>2 and len(s)<20]
  for w in titlewords: f['Title:'+w]=1

  # 요약에서 단어를 추출함
  summarywords=[s.lower() for s in splitter.split(entry['summary'])
                if len(s)>2 and len(s)<20]

  # 대문자 단어 수를 셈
  uc=0
  for i in range(len(summarywords)):
    w=summarywords[i]
    f[w]=1
    if w.isupper(): uc+=1
    
    # 요약에서 단어 쌍을 특성으로 추출함
    if i<len(summarywords)-1:
      twowords=' '.join(summarywords[i:i+1])
      f[twowords]=1

  # 작성자와 배포자는 그대로 유지함
  f['Publisher:'+entry['publisher']]=1
  
  # UPPERCASE는 가상 단어로, 외치는 정도를 나타냄
  if float(uc)/len(summarywords)>0.3: f['UPPERCASE']=1

  return f



