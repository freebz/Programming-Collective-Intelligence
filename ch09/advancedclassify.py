#-*- coding: utf-8 -*-

# 01: 중매 데이터 세트

class matchrow:
  def __init__(self,row,allnum=False):
    if allnum:
      self.data=[float(row[i]) for i in range(len(row)-1)]
    else:
      self.data=row[0:len(row)-1]
    self.match=int(row[len(row)-1])

def loadmatch(f,allnum=False):
  rows=[]
  for line in file(f):
    rows.append(matchrow(line.split(','),allnum))
  return rows




# 02: 데이터를 다루는 어려움

from pylab import *
def plotagematches(rows):
  xdm,ydm=[r.data[0] for r in rows if r.match==1],\
          [r.data[1] for r in rows if r.match==1]
  xdn,ydn=[r.data[0] for r in rows if r.match==0],\
          [r.data[1] for r in rows if r.match==0]

  plot(xdm,ydm,'go')
  plot(xdn,ydn,'ro')

  show()


# 의사결정트리 분류기




# 03: 기본 선형 분류

def lineartrain(rows):
  averages={}
  counts={}

  for row in rows:
    # 이 점의 범주를 구함
    cl=row.match

    averages.setdefault(cl,[0.0]*(len(row.data)))
    counts.setdefault(cl,0)

    # 이 점을 평균에 더함
    for i in range(len(row.data)):
      averages[cl][i]+=float(row.data[i])

    # 각 범주 내의 점 개수를 추적함
    counts[cl]+=1

  # 점 개수로 나눠 평균을 구함
  for cl,avg in averages.items():
    for i in range(len(avg)):
      avg[i]/=counts[cl]

  return averages



def dotproduct(v1,v2):
  return sum([v1[i]*v2[i] for i in range(len(v1))])

def veclength(v):
  return sum([p**2 for p in v])


def dpclassify(point,avgs):
  b=(dotproduct(avgs[1],avgs[1])-dotproduct(avgs[0],avgs[0]))/2
  y=dotproduct(point,avgs[0])-dotproduct(point,avgs[1])+b
  if y>0: return 0
  else: return 1




# 04: 분류 데이터의 특성

# 예/아니요 질문

def yesno(v):
  if v=='yes': return 1
  elif v=='no': return -1
  else: return 0


# 관심 목록

def matchcount(interest1,interest2):
  l1=interest1.split(':')
  l2=interest2.split(':')
  x=0
  for v in l1:
    if v in l2: x+=1
  return x



# 야후! 지도를 사용한 거리 계산

def milesdistance(a1,a2):
  return 0


"""
yahookey="Your Key Here"
from xml.dom.minidom import parseString
from urllib import urlopen,quote_plus

loc_cache={}
def getlocation(address):
  if address in loc_cache: return loc_cache[address]
  data=urlopen('http://api.local.yayoo.com/MapsService/V1/'+\
               'geocode?apiid=%s&location=%s' %
               (yahookey,quote_plus(address))).read()
  doc=parseString(data)
  lat=doc.getElementsByTagName('Latitude')[0].firstChild.nodeValue
  long=doc.getElementsByTagName('Longitude')[0].firstChild.nodeValue
  loc_cache[address]=(float(lat),float(long))
  return loc_cache[address]

def milesdistance(a1,a2):
  lat1,long1=getlocation(a1)
  lat2,long2=getlocation(a2)
  latdif=69.1*(lat2-lat1)
  longdif=53.0*(long2-long1)
  return (latdif**2+longdif**2)**.5
"""



# 새로운 데이터 세트 생성하기

def loadnumerical():
  oldrows=loadmatch('matchmaker.csv')
  newrows=[]
  for row in oldrows:
    d=row.data
    data=[float(d[0]),yesno(d[1]),yesno(d[2]),
          float(d[5]),yesno(d[6]),yesno(d[7]),
          matchcount(d[3],d[8]),
          milesdistance(d[4],d[9]),
          row.match]
    newrows.append(matchrow(data))
  return newrows




# 05: 데이터 추척 조정

def scaledata(rows):
  low=[999999999.0]*len(rows[0].data)
  high=[-999999999.0]*len(rows[0].data)
  # 최저값과 최고값을 찾음
  for row in rows:
    d=row.data
    for i in range(len(d)):
      if d[i]<low[i]: low[i]=d[i]
      if d[i]>high[i]: high[i]=d[i]

  # 데이터 축척 계산 함수를 생성함
  def scaleinput(d):
    #return [(d[i]-low[i])/(high[i]-low[i])
    #        for i in range(len(low))]
    result=[]
    for i in range(len(low)):
      if high[i]==low[i]:
        result.append(0)
      else:
        result.append((d[i]-low[i])/(high[i]-low[i]))
    return result
  
  # 모든 데이터 축척을 조정함
  newrows=[matchrow(scaleinput(row.data)+[row.match])
           for row in rows]

  # 새로운 데이터와 함수를 리턴함
  return newrows,scaleinput




# 06: 커널 기법 이해

# 커널 트릭

def rbf(v1,v2,gamma=20):
  dv=[v1[i]-v2[i] for i in range(len(v1))]
  l=veclength(dv)
  return math.e**(-gamma*l)



def nlclassify(point,rows,offset,gamma=10):
  sum0=0.0
  sum1=0.0
  count0=0
  count1=0

  for row in rows:
    if row.match==0:
      sum0+=rbf(point,row.data,gamma)
      count0+=1
    else:
      sum1+=rbf(point,row.data,gamma)
      count1+=1
  y=(1.0/count0)*sum0-(1.0/count1)*sum1+offset

  if y>0: return 0
  else: return 1

def getoffset(rows,gamma=10):
  l0=[]
  l1=[]
  for row in rows:
    if row.match==0: l0.append(row.data)
    else: l1.append(row.data)
  sum0=sum(sum([rbf(v1,v2,gamma) for v1 in l0]) for v2 in l0)
  sum1=sum(sum([rbf(v1,v2,gamma) for v1 in l1]) for v2 in l1)

  return (1.0/(len(l1)**2))*sum1-(1.0/(len(l0)**2))*sum0
