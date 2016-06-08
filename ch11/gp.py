#-*- coding: utf-8 -*-

# 01: 유전자 프로그래밍이란?

# 유전자 프로그래밍과 유전자 알고리즘

# 02: 프로그램을 트리로 표현하기

# 파이썬에서 트리 표현하기

from random import random,randint,choice
from copy import deepcopy
from math import log


class fwrapper:
  def __init__(self,function,childcount,name):
    self.function=function
    self.childcount=childcount
    self.name=name

class node:
  def __init__(self,fw,children):
    self.function=fw.function
    self.name=fw.name
    self.children=children

  def evaluate(self,inp):
    results=[n.evaluate(inp) for n in self.children]
    return self.function(results)

  def display(self,indent=0):
    print (' '*indent)+self.name
    for c in self.children:
      c.display(indent+1)



class paramnode:
  def __init__(self,idx):
    self.idx=idx

  def evaluate(self,inp):
    return inp[self.idx]

  def display(self,indent=0):
    print '%sp%d' % (' '*indent,self.idx)

class constnode:
  def __init__(self,v):
    self.v=v

  def evaluate(self,inp):
    return self.v

  def display(self,indent=0):
    print '%s%d' % (' '*indent,self.v)



addw=fwrapper(lambda l:l[0]+l[1],2,'add')
subw=fwrapper(lambda l:l[0]-l[1],2,'subtract')
mulw=fwrapper(lambda l:l[0]*l[1],2,'multiply')

def iffunc(l):
  if l[0]>0: return l[1]
  else: return l[2]
ifw=fwrapper(iffunc,3,'if')

def isgreater(l):
  if l[0]>l[1]: return 1
  else: return 0
gtw=fwrapper(isgreater,2,'isgreater')

flist=[addw,mulw,ifw,gtw,subw]




# 트리 제작 및 평가하기

def exampletree():
  return node(ifw,[
    node(gtw,[paramnode(0),constnode(3)]),
    node(addw,[paramnode(1),constnode(5)]),
    node(subw,[paramnode(1),constnode(2)]),
    ]
  )


# 프로그램 표시하기



# 03: 초기 개체군 만들기

def makerandomtree(pc,maxdepth=4,fpr=0.5,ppr=0.6):
  if random()<fpr and maxdepth>0:
    f=choice(flist)
    children=[makerandomtree(pc,maxdepth-1,fpr,ppr)
              for i in range(f.childcount)]
    return node(f,children)
  elif random()<ppr:
    return paramnode(randint(0,pc-1))
  else:
    return constnode(randint(0,10))




# 04: 해담 검증하기

# 단순한 수식으로 검증하기

def hiddenfunction(x,y):
  return x**2+2*y+3*x+5


def buildhiddenset():
  rows=[]
  for i in range(200):
    x=randint(0,40)
    y=randint(0,40)
    rows.append([x,y,hiddenfunction(x,y)])
  return rows



# 성공여부 측정하기

def scorefunction(tree,s):
  dif=0
  for data in s:
    v=tree.evaluate([data[0],data[1]])
    dif+=abs(v-data[2])
  return dif




# 05: 프로그램 돌연변이시키기

def mutate(t,pc,probchange=0.1):
  if random()<probchange:
    return makerandomtree(pc)
  else:
    result=deepcopy(t)
    if isinstance(t,node):
      result.children=[mutate(c,pc,probchange) for c in t.children]
    return result



# 06: 교배하기

def crossover(t1,t2,probswap=0.7,top=1):
  if random()<probswap and not top:
    return deepcopy(t2)
  else:
    result=deepcopy(t1)
    if isinstance(t1,node) and isinstance(t2,node):
      result.children=[crossover(c,choice(t2.children),probswap,0)
                       for c in t1.children]
    return result



# 07: 환경 구축하기

def evolve(pc,popsize,rankfunction,maxgen=500,
           mutationrate=0.1,breedingrate=0.4,pexp=0.7,pnew=0.05):
  # 낮은 숫자를 선호하도록 무작위 숫자를 리턴함
  # 분모인 pexp가 작을수록 낮은 숫자를 얻을 가능성이 높음
  def selectindex():
    return int(log(random())/log(pexp))

  # 무작위로 초기 개체군을 생성함
  population=[makerandomtree(pc) for i in range(popsize)]
  for i in range(maxgen):
    scores=rankfunction(population)
    print scores[0][0]
    if scores[0][0]==0: break

    # 두 개의 최고를 선택함
    newpop=[scores[0][1],scores[1][1]]

    # 다음세대를 만듦
    while len(newpop)<popsize:
      if random()>pnew:
        newpop.append(mutate(
          crossover(scores[selectindex()][1],
                    scores[selectindex()][1],
                    probswap=breedingrate),
          pc,probchange=mutationrate))
      else:
      # 무작위 노드를 섞어 넣음
        newpop.append(makerandomtree(pc))

    population=newpop
  scores[0][1].display()
  return scores[0][1]



def getrankfunction(dataset):
  def rankfunction(population):
    scores=[(scorefunction(t,dataset),t) for t in population]
    scores.sort()
    return scores
  return rankfunction




# 08: 간단한 게임

def gridgame(p):
  # 보드 크기
  max=(3,3)

  # 각 선수의 마지막 이동을 기억함
  lastmove=[-1,-1]

  # 선수의 위치를 기억함
  location=[[randint(0,max[0]),randint(0,max[1])]]

  # 두 번째 선수를 첫 선수와 충분히 멀리 떨어뜨림
  location.append([(location[0][0]+2)%4,(location[0][1]+2)%4])
  # 무승부 전에 최대 50만큼만 이동함
  for o in range(50):

    # 각 선수에 대해
    for i in range(2):
      locs=location[i][:]+location[1-i][:]
      locs.append(lastmove[i])
      move=p[i].evaluate(locs)%4

      # 가로줄에서 동일한 방향으로 두 번 이동하면 짐
      if lastmove[i]==move: return 1-i
      lastmove[i]=move
      if move==0:
        location[i][0]-=1
        # 보드 경계에 도달했는가?
        if location[i][0]<0: location[i][0]=0
      if move==1:
        location[i][0]+=1
        if location[i][0]>max[0]: location[i][0]=max[0]
      if move==2:
        location[i][1]-=1
        if location[i][1]<0: location[i][1]=0
      if move==3:
        location[i][1]+=1
        if location[i][1]>max[1]: location[i][1]=max[1]

      # 다른 선수를 잡으면 이기게 됨
      if location[i]==location[1-i]: return i
  return -1




# 승자전

def tournament(pl):
  # 패배 횟수
  losses=[0 for p in pl]

  # 모든 선수가 각자 겨룸
  for i in range(len(pl)):
    for j in range(len(pl)):
      if i==j: continue

      # 누가 승자인지 판단함
      winner=gridgame([pl[i],pl[j]])

      # 패배면 2점을, 무승부면 1점을 기록함
      if winner==0:
        losses[j]+=2
      elif winner==1:
        losses[i]+=2
      elif winner==-1:
        losses[i]+=1
        losses[j]+=1
        pass

  # 정렬해서 결과를 리턴함
  z=zip(losses,pl)
  z.sort()
  return z




# 실제 사람과 경기하기

class humanplayer:
  def evaluate(self,board):
    
    # 다른 선수의 위치와 내 위치를 얻음
    me=tuple(board[0:2])
    others=[tuple(board[x:x+2]) for x in range(2,len(board)-1,2)]

    # 보드를 출력함
    for i in range(4):
      for j in range(4):
        if (i,j)==me:
          print 'O',
        elif (i,j) in others:
          print 'X',
        else:
          print '.',
      print

    # 참조를 위해 이동결과를 보여줌
    print 'Your last move was %d' % board[len(board)-1]
    print ' 0'
    print '2 3'
    print ' 1'
    print 'Enter move: ',
    
    # 사용자가 입력한 것을 리턴함
    move=int(raw_input())
    return move
