#-*- coding: utf-8 -*-

# 01: 스팸 필터링
# 02: 문서와 단어

import re
import math
#from pysqlite2 import dbapi2 as sqlite
import sqlite3 as sqlite


def getwords(doc):
  splitter=re.compile('\\W*')
  # 텍스트를 알파벳이 아닌 문자로 분리함
  words=[s.lower() for s in splitter.split(doc)
         if len(s)>2 and len(s)<20]

  # 유일한 단어들만 리턴
  return dict([(w,1) for w in words])


def sampletrain(cl):
  cl.train('Nobody owns the water.','good')
  cl.train('the quick rabbit jumps fences','good')
  cl.train('buy pharmaceuticals now','bad')
  cl.train('make quick money atthe online casino','bad')
  cl.train('the quick brown fox jumps','good')



# 03: 분류기 훈련시키기

class classifier:
  def __init__(self,getfeatures,filename=None):
    # 특성/분류 조합 수를 셈
    self.fc={}
    
    # 각 분류별 문서 수를 셈
    self.cc={}
    self.getfeatures=getfeatures


  
  # 특성/분류 쌍 횟수를 증가시킴
  def incf(self,f,cat):
    self.fc.setdefault(f,{})
    self.fc[f].setdefault(cat,0)
    self.fc[f][cat]+=1

  # 분류 횟수를 증가시킴
  def incc(self,cat):
    self.cc.setdefault(cat,0)
    self.cc[cat]+=1

  # 한 특성이 특정 분류에 출현한 횟수
  def fcount(self,f,cat):
    if f in self.fc and cat in self.fc[f]:
      return float(self.fc[f][cat])
    return 0.0

  # 분류당 항목 개수
  def catcount(self,cat):
    if cat in self.cc:
      return float(self.cc[cat])
    return 0

  # 항목 전체 개수
  def totalcount(self):
    return sum(self.cc.values())

  # 전체 분류 목록
  def categories(self):
    return self.cc.keys()


  def train(self,item,cat):
    features=self.getfeatures(item)
    # 이 분류 내 모든 특성 횟수를 증가시킴
    for f in features:
      self.incf(f,cat)

    # 이 분류 횟수를 증가시킴
    self.incc(cat)
    self.con.commit()



# 04: 확률 계산

  def fprob(self,f,cat):
    if self.catcount(cat)==0: return 0

    # 해당 분류에서 특성이 나타난 횟수를 그 분류에 있는 전체 항목 개수로 나눔
    return self.fcount(f,cat)/self.catcount(cat)


# 적당히 추정하기

  def weightedprob(self,f,cat,prf,weight=1.0,ap=0.5):
    # 현재의 확률을 계산함
    basicprob=prf(f,cat)

    # 모든 분류에 이 특성이 출현한 횟수를 계산함
    totals=sum([self.fcount(f,c) for c in self.categories()])

    # 가중편균을 계산함
    bp=((weight*ap)+(totals*basicprob))/(weight+totals)
    return bp


# 07: 학습 정보 저장

  def setdb(self,dbfile):
    self.con=sqlite.connect(dbfile)
    self.con.execute('create table if not exists fc(feature,category,count)')
    self.con.execute('create table if not exists cc(category,count)')



  def incf(self,f,cat):
    count=self.fcount(f,cat)
    if count==0:
      self.con.execute("insert into fc values ('%s','%s',1)"
                       % (f,cat))
    else:
      self.con.execute(
        "update fc set count=%d where feature='%s' and category='%s'"
        % (count+1,f,cat))

  def fcount(self,f,cat):
    res=self.con.execute(
      'select count from fc where feature="%s" and category="%s"'
      %(f,cat)).fetchone()
    if res==None: return 0
    else: return float(res[0])

  def incc(self,cat):
    count=self.catcount(cat)
    if count==0:
      self.con.execute("insert into cc values ('%s',1)" % (cat))
    else:
      self.con.execute("update cc set count=%d where category='%s'"
                       % (count+1,cat))

  def catcount(self,cat):
    res=self.con.execute('select count from cc where category="%s"'
                         %(cat)).fetchone()
    if res==None: return 0
    else: return float(res[0])



  def categories(self):
    cur=self.con.execute('select category from cc');
    return [d[0] for d in cur]

  def totalcount(self):
    res=self.con.execute('select sum(count) from cc').fetchone();
    if res==None: return 0
    return res[0]




# 05: 기본 분류기

# 전체 문서 확률

class naivebayes(classifier):
  def docprob(self,item,cat):
    features=self.getfeatures(item)

    # 모든 특성의 확률을 곱함
    p=1
    for f in features: p*=self.weightedprob(f,cat,self.fprob)
    return p


# 베이스 정리에 대한 간략한 소개

  def prob(self,item,cat):
    catprob=self.catcount(cat)/self.totalcount()
    docprob=self.docprob(item,cat)
    return docprob*catprob


# 분류 선택하기

  def __init__(self,getfeatures):
    classifier.__init__(self,getfeatures)
    self.thresholds={}



  def setthreshold(self,cat,t):
    self.thresholds[cat]=t

  def getthreshold(self,cat):
    if cat not in self.thresholds: return 1.0
    return self.thresholds[cat]



  def classify(self,item,default=None):
    probs={}
    # 가장 높은 확률을 가진 분류를 찾음
    max=0.0
    for cat in self.categories():
      probs[cat]=self.prob(item,cat)
      if probs[cat]>max:
        max=probs[cat]
        best=cat

    # 확률 값이 threshold*next best를 초과하는지 확인함
    for cat in probs:
      if cat==best: continue
      if probs[cat]*self.getthreshold(best)>probs[best]: return default
    return best



# 06: 피셔 방식

# 특성별 분류 확률

class fisherclassifier(classifier):
  def cprob(self,f,cat):
    # 이 분류 내 이 특성의 빈도
    clf=self.fprob(f,cat)
    if clf==0: return 0
    
    # 모든 분류에서 이 특성의 빈도
    freqsum=sum([self.fprob(f,c) for c in self.categories()])
    
    # 확률은 이 분류 내 빈도를 전체 빈도로 나눈 값임
    p=clf/(freqsum)

    return p



# 확률 결합

  def fisherprob(self,item,cat):
    # 모든 확률을 곱함
    p=1
    features=self.getfeatures(item)
    for f in features:
      p*=(self.weightedprob(f,cat,self.cprob))
      
    # 자연로그를 취하고 -2를 곱함
    fscore=-2*math.log(p)

    # 역 chi2 함수를 사용해서 최종 확률을 계산함
    return self.invchi2(fscore,len(features)*2)



  def invchi2(self,chi,df):
    m = chi / 2.0
    sum = term = math.exp(-m)
    for i in range(1, df//2):
      term *= m / i
      sum += term
    return min(sum,1.0)



# 항목 분류

  def __init__(self,getfeatures):
    classifier.__init__(self,getfeatures)
    self.mininums={}

    

  def setmininum(self,cat,min):
    self.mininums[cat]=min

  def getmininum(self,cat):
    if cat not in self.mininums: return 0
    return self.mininums[cat]



  def classify(self,item,default=None):
    # 최적 결과를 찾기 위해 루프를 돔
    best=default
    max=0.0
    for c in self.categories():
      p=self.fisherprob(item,c)
      # 최소값을 초과하는지 확인함
      if p>self.getmininum(c) and p>max:
        best=c
        max=p
    return best
