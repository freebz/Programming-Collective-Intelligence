#-*- coding: utf-8 -*-

# 10: 네트워크 시각화

# 배치 문제

import math
from PIL import Image,ImageDraw


people=['Charlie', 'Augustus', 'Veruca', 'Violet', 'Mike', 'Joe', 'Willy', 'Miranda']

links=[('Augustus', 'Willy'),
       ('Mike', 'Joe'),
       ('Miranda', 'Mike'),
       ('Violet', 'Augustus'),
       ('Miranda', 'Willy'),
       ('Charlie', 'Mike'),
       ('Veruca', 'Joe'),
       ('Miranda', 'Augustus'),
       ('Willy', 'Augustus'),
       ('Joe', 'Charlie'),
       ('Veruca', 'Augustus'),
       ('Miranda', 'Joe')]


# 교차선 세기

def crosscount(v):
  # 번호 목록을 사람: (x,y) 에 대한 딕셔너리로 변경함
  loc=dict([(people[i],(v[i*2],v[i*2+1])) for i in range(0,len(people))])
  total=0

  # 모든 links 쌍마다 루프를 돔
  for i in range(len(links)):
    for j in range(i+1,len(links)):
      
      # 위치 좌표를 얻음
      (x1,y1),(x2,y2)=loc[links[i][0]],loc[links[i][1]]
      (x3,y3),(x4,y4)=loc[links[j][0]],loc[links[j][1]]

      den=(y4-y3)*(x2-x1)-(x4-x3)*(y2-y1)

      # 평생선이면 den==0
      if den==0: continue
      
      # 그렇지 않으면 ua와 ub는 교차점에 대한 선의 비율임
      ua=((x4-x3)*(y1-y3)-(y4-y3)*(x1-x3))/den
      ub=((x2-x1)*(y1-y3)-(y2-y1)*(x1-x3))/den

      # 비율이 두 선 모두 0과 1 사이 값이면 서로 교차함
      if ua>0 and ua<1 and ub>0 and ub<1:
        total+=1

  for i in range(len(people)):
    for j in range(i+1,len(people)):
      # 두 노드의 위치를 구함
      (x1,y1),(x2,y2)=loc[people[i]],loc[people[j]]
      
      # 두 노드 간의 거리를 계산함
      dist=math.sqrt(math.pow(x1-x2,2)+math.pow(y1-y2,2))
      # 50픽셀보다 가까우면 벌점을 줌
      if dist<50:
        total+=(1.0-(dist/50.0))

  return total



domain=[(10,370)]*(len(people)*2)



# 네트워크 그리기

def drawnetwork(sol):
  # 이미지를 생성함
  img=Image.new('RGB',(400,400),(255,255,255))
  draw=ImageDraw.Draw(img)

  # 위치 딕셔너리를 생성함
  pos=dict([(people[i],(sol[i*2],sol[i*2+1])) for i in range(0,len(people))])

  # 연결들을 그림
  for (a,b) in links:
    draw.line((pos[a],pos[b]),fill=(255,0,0))

  # 사람들을 그림
  for n,p in pos.items():
    draw.text(p,n,(0,0,0))

  img.show()
