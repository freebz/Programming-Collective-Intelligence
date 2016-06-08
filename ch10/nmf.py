#-*- coding: utf-8 -*-

# 03: 비음수 행렬 인수분해

# 행렬 수학 소개

# 기사 행렬로 무엇을 할 수 있나?

# 넘피(NumPy) 사용하기

# 알고리즘

from numpy import *

def difcost(a,b):
  dif=0
  # 행렬 내 모든 가로줄과 세로줄마다 루프를 돔
  for i in range(shape(a)[0]):
    for j in range(shape(a)[1]):
      # 차이를 더함
      dif+=pow(a[i,j]-b[i,j],2)
  return dif



def factorize(v,pc=10,iter=50):
  ic=shape(v)[0]
  fc=shape(v)[1]
  
  # 가중치 행렬과 특성 행렬을 무작위 값으로 초기화함
  w=matrix([[random.random() for i in range(pc)] for i in range(ic)])
  h=matrix([[random.random() for i in range(fc)] for i in range(pc)])

  # 최대 반복 횟수만큼 수행함
  for i in range(iter):
    wh=w*h
    
    # 현재의 차이를 계산함
    cost=difcost(v,wh)

    if i%10==0: print cost
    
    # 행렬이 완전히 인수분해되면 종료함
    if cost==0: break
    
    # 특성 행렬을 갱신함
    hn=(transpose(w)*v)
    hd=(transpose(w)*w*h)

    h=matrix(array(h)*array(hn)/array(hd))

    # 가중치 행렬을 갱신함
    wn=(v*transpose(h))
    wd=(w*h*transpose(h))

    w=matrix(array(w)*array(wn)/array(wd))

  return w,h
