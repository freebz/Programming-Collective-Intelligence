#-*- coding: utf-8 -*-

# 05: 주식시장 데이터 사용하기

# 거래량이란?

# 야휴! 금융에서 데이터 다운로드받기

import nmf
import urllib2
from numpy import *

tickers=['YHOO','AVP','BIIB','BP','CL','CVX',
         'DNA','EXPE','GOOG','PG','XOM','AMGN']

shortest=300
prices={}
dates=None

for t in tickers:
  # URL을 염
  rows=urllib2.urlopen('http://ichart.finance.yahoo.com/table.csv?'+\
                       's=%s&d=11&e=26&f=2006&g=d&a=3&b=12&c=1996'%t +\
                       '&ignore=.csv').readlines()

  # 모든 줄에서 거래량 필드를 추출함
  prices[t]=[float(r.split(',')[5]) for r in rows[1:] if r.strip()!='']
  if len(prices[t])<shortest: shortest=len(prices[t])

  if not dates:
    dates=[r.split(',')[0] for r in rows[1:] if r.strip()!='']




# 행렬 준비하기

l1=[[prices[tickers[i]][j]
     for i in range(len(tickers))]
    for j in range(shortest)]



# NMF 실행하기

w,h= nmf.factorize(matrix(l1),pc=5)

print h
print w




# 결과 출력하기

# 모든 특성마다 루프를 돔
for i in range(shape(h)[0]):
  print "Feature %d" %i

  # 이 특성에 대한 상위 주식을 얻어옴
  ol=[(h[i,j],tickers[j]) for j in range(shape(h)[1])]
  ol.sort()
  sl.reverse()
  for j in range(l2):
    print ol[j]
  print

  # 이 특성에 대한 상위 날짜를 얻어옴
  proder=[(w[d,i],d) for d in range(300)]
  porder.sort()
  porder.reverse()
  print [(p[0],dates[p[1]]) for p in porder[0:3]]
  print
