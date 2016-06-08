#-*- coding: utf-8 -*-

# 01: 예제 데이터 세트 만들기

from random import random,randint
import math


def wineprice(rating,age):
  peak_age=rating-50

  # 등급에 따라 가격을 계산함
  price=rating/2
  if age>peak_age:
    # 최적 연도가 지나면 5년 단위로 가격이 저하됨
    price=price*(5-(age-peak_age))
  else:
    # 최적 연도에 근접하면 원래 가격의 5배까지 증가함
    price=price*(5*((age+1)/peak_age))
  if price<0: price=0
  return price



def wineset1():
  rows=[]
  for i in range(300):
    # 무작위로 나이(숙성 기간)와 등급을 생성함
    rating=random()*50+50
    age=random()*50

    # 가격을 얻음
    price=wineprice(rating,age)
    
    # 노이즈를 부가함
    price*=(random()*0.4+0.8)

    # 데이터 세트에 추가함
    rows.append({'input':(rating,age),
                 'result':price})
  return rows




# 02: kNN

# 이웃 개수

# 유사도 결정하기

def euclidean(v1,v2):
  d=0.0
  for i in range(len(v1)):
    d+=(v1[i]-v2[i])**2
  return math.sqrt(d)



# kNN 코드

def getdistances(data,vec1):
  distancelist=[]
  for i in range(len(data)):
    vec2=data[i]['input']
    distancelist.append((euclidean(vec1,vec2),i))
  distancelist.sort()
  return distancelist



def knnestimate(data,vec1,k=3):
  # 정렬된 거리들을 얻음
  dlist=getdistances(data,vec1)
  avg=0.0

  # 상위 k개 결과의 평균을 구함
  for i in range(k):
    idx=dlist[i][1]
    avg+=data[idx]['result']
  avg=avg/k
  return avg




# 03: 물품 가중치

# 역 함수

def inverseweight(dist,num=1.0,const=0.1):
  return num/(dist+const)


# 빼기 함수

def subtractweight(dist,const=1.0):
  if dist>const:
    return 0
  else:
    return const-dist


# 가우스 함수

def gaussian(dist,sigma=1.0):
  return math.e**(-dist**2/(2*sigma**2))



# 가중 kNN 

def weightedknn(data,vec1,k=5,weightf=gaussian):
  # 거리를 구함
  dlist=getdistances(data,vec1)
  avg=0.0
  totalweight=0.0
  
  # 가중평균을 구함
  for i in range(k):
    dist=dlist[i][0]
    idx=dlist[i][1]
    weight=weightf(dist)
    avg+=weight*data[idx]['result']
    totalweight+=weight
  if totalweight==0: return 0
  avg=avg/totalweight
  return avg




# 04: 교차검증

def dividedata(data,test=0.05):
  trainset=[]
  testset=[]
  for row in data:
    if random()<test:
      testset.append(row)
    else:
      trainset.append(row)
  return trainset,testset



def testalgorithm(algf,trainset,testset):
  error=0.0
  for row in testset:
    guess=algf(trainset,row['input'])
    error+=(row['result']-guess)**2
  return error/len(testset)



def crossvalidate(algf,data,trials=100,test=0.05):
  error=0.0
  for i in range(trials):
    trainset,testset=dividedata(data,test)
    error+=testalgorithm(algf,trainset,testset)
  return error/trials




# 05: 이질 변수

# 데이터 세트에 추가하기

def wineset2():
  rows=[]
  for i in range(300):
    # 무작위로 나이(숙성 기간)와 등급을 생성함
    rating=random()*50+50
    age=random()*50
    
    aisle=float(randint(1,20))
    bottlesize=[375.0,750.0,1500.0,3000.0][randint(0,3)]

    # 가격을 얻음
    price=wineprice(rating,age)
    price*=(bottlesize/750)
    
    # 노이즈를 부가함
    price*=(random()*0.9+0.2)

    # 데이터 세트에 추가함
    rows.append({'input':(rating,age,aisle,bottlesize),
                 'result':price})
  return rows




# 축척 조정

def rescale(data,scale):
  scaleddata=[]
  for row in data:
    scaled=[scale[i]*row['input'][i] for i in range(len(scale))]
    scaleddata.append({'input':scaled,'result':row['result']})
  return scaleddata




# 06: 축척 최적화

def createcostfunction(algf,data):
  def costf(scale):
    sdata=rescale(data,scale)
    return crossvalidate(algf,sdata,trials=10)
  return costf



weightdomain=[(0,20)]*4




# 07: 불균등 분포

def wineset3():
  rows=wineset1()
  for row in rows:
    if random()<0.5:
      # 이 와인을 활인점에서 구매함
      row['result']*=0.6
  return rows



# 확률 밀도 추정하기

def probguess(data,vec1,low,high,k=5,weightf=gaussian):
  dlist=getdistances(data,vec1)
  nweight=0.0
  tweight=0.0

  for i in range(k):
    dist=dlist[i][0]
    idx=dlist[i][1]
    weight=weightf(dist)
    v=data[idx]['result']

    # 범위 안에 있는가?
    if v>=low and v<=high:
      nweight+=weight
    tweight+=weight
  if tweight==0: return 0

  # 확률은 범위 내의 가중치를 모든 가중치로 나눈 값임
  return nweight/tweight



# 확률 그래프 그리기

from pylab import *

def cumulativegraph(data,vec1,high,k=5,weightf=gaussian):
  t1=arange(0.0,high,0.1)
  cprob=array([probguess(data,vec1,0,v,k,weightf) for v in t1])
  plot(t1,cprob)
  show()



def probabilitygraph(data,vec1,high,k=5,weightf=gaussian,ss=5.0):
  # 가격 범위를 생성함
  t1=arange(0.0,high,0.1)
  
  # 전체 범위의 확률을 구함
  probs=[probguess(data,vec1,v,v+0.1,k,weightf) for v in t1]
  
  # 주변 확률들의 가우스 값을 더하여 부드럽게 함
  smoothed=[]
  for i in range(len(probs)):
    sv=0.0
    for j in range(0,len(probs)):
      dist=abs(i-j)*0.1
      weight=gaussian(dist,sigma=ss)
      sv+=weight*probs[j]
    smoothed.append(sv)
  smoothed=array(smoothed)
  
  plot(t1,smoothed)
  show()
