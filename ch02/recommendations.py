# 영화 비평과 영화 평가 정보를 담는 딕셔너리
critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
 'The Night Listener': 3.0},
'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 3.5},
'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
 'Superman Returns': 3.5, 'The Night Listener': 4.0},
'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
 'The Night Listener': 4.5, 'Superman Returns': 4.0,
 'You, Me and Dupree': 2.5},
'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 2.0},
'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
'Toby': {'Snakes on a Plane': 4.5, 'You, Me and Dupree': 1.0, 'Superman Returns': 4.0}}


from math import sqrt

# person1과 person2의 거리 기반 유사도 점수를 리턴
def sim_distance(prefs,person1,person2):
  # 공통 항목 목록 추출
  si={}
  for item in prefs[person1]:
    if item in prefs[person2]:
      si[item]=1

  # 공통 평가 항목이 없는 경우 0 리턴
  if len(si)==0: return 0

  # 모든 차이 값의 제곱을 더함
  sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2)
                      for item in prefs[person1] if item in prefs[person2]])

  return 1/(1+sum_of_squares)


# p1과 p2에 대한 피어슨 상관계수를 리턴
def sim_pearson(prefs,p1,p2):
  # 같이 평가한 항목들의 목록을 구함
  si={}
  for item in prefs[p1]:
    if item in prefs[p2]: si[item]=1

  # 요소들의 개수를 구함
  n=len(si)

  # 공통 요소가 없으면 0 리턴
  if n==0: return 0

  # 모든 선호드를 합산함
  sum1=sum([prefs[p1][it] for it in si])
  sum2=sum([prefs[p2][it] for it in si])

  # 제곱의 합을 계산
  sum1Sq=sum([pow(prefs[p1][it],2) for it in si])
  sum2Sq=sum([pow(prefs[p2][it],2) for it in si])

  # 곱의 합을 계산
  pSum=sum([prefs[p1][it]*prefs[p2][it] for it in si])

  # 피어슨 점수 계산
  num=pSum-(sum1*sum2/n)
  den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
  if den==0: return 0

  r=num/den

  return r


# 선호도 딕션너리에서 최적의 상대편들을 구함
# 결과 개수와 유사도 함수는 옵션 사항임
def topMatches(prefs,person,n=5,similarity=sim_pearson):
  scores=[(similarity(prefs,person,other),other)
          for other in prefs if other!=person]

  # 최고점이 상단에 오도록 목록을 정렬
  scores.sort()
  scores.reverse()
  return scores[0:n]


# 다른 사람과의 순위의 가중평균값을 이용해서 특정 사람에 추천
def getRecommendations(prefs,person,similarity=sim_pearson):
  totals={}
  simSums={}
  for other in prefs:
    # 나와 나를 비교하지 말 것
    if other==person: continue
    sim=similarity(prefs,person,other)

    # 0 이하 점수는 무시함
    if sim<=0: continue
    for item in prefs[other]:

      # 내가 보지 못한 영화만 대상
      if item not in prefs[person] or prefs[person][item]==0:
        # 유사도 * 점수
        totals.setdefault(item,0)
        totals[item]+=prefs[other][item]*sim
        # 유사도 합계
        simSums.setdefault(item,0)
        simSums[item]+=sim

  # 정규화된 목록 생성
  rankings=[(total/simSums[item],item) for item,total in totals.items()]

  # 정렬된 목록 리턴
  rankings.sort()
  rankings.reverse()
  return rankings



def transformPrefs(prefs):
  result={}
  for person in prefs:
    for item in prefs[person]:
      result.setdefault(item,{})

      # 물건과 사람을 바꿈
      result[item][person]=prefs[person][item]
  return result





# 항목 비교 데이터 세트 생성

def calculateSimilarItems(prefs,n=10):
  # 가장 유사한 항목들을 가진 항목 딕셔너리를 생성
  result={}

  # 선호도 행렬을 뒤집어 항목 중심 행렬로 변환
  itemPrefs=transformPrefs(prefs)
  c=0
  for item in itemPrefs:
    # 큰 데이터 세트를 위해 진척 상태를 갱신
    c+=1
    if c%100==0: print "%d / %d" % (c,len(itemPrefs))
    # 각 항목과 가장 유사한 항목들을 구함
    scores=topMatches(itemPrefs,item,n=n,similarity=sim_distance)
    result[item]=scores
  return result


# 추천 생성

def getRecommendedItems(prefs,itemMatch,user):
  userRatings=prefs[user]
  scores={}
  totalSim={}

  # 이 사용자가 평가한 모든 항목마다 루프를 돔
  for (item,rating) in userRatings.items():

    # 이 항목과 유사한 모든 항목마다 루프를 돔
    for (similarity,item2) in itemMatch[item]:
      
      # 이 사용자가 이 항목을 이미 평가했다면 무시함
      if item2 in userRatings: continue
      
      # 유사도와 평가점수 곱의 가중치 합을 계산
      scores.setdefault(item2,0)
      scores[item2]+=similarity*rating

      # 모든 유사도 합을 계산
      totalSim.setdefault(item2,0)
      totalSim[item2]+=similarity
  
  # 평균값을 얻기 위해 합계를 가중치 합계로 나눔
  rankings=[(score/totalSim[item],item) for item,score in scores.items()]

  # 최고값에서 최저값 순으로 랭킹을 리턴함
  rankings.sort()
  rankings.reverse()
  return rankings



# 08: 무비렌즈 데이터 세트 이용하기

def loadMovieLens(path='data/movielens'):

  # 영화 제목을 얻음
  movies={}
  for line in open(path+'/u.item'):
    (id,title)=line.split('|')[0:2]
    movies[id]=title

  # 데이터를 로드함
  prefs={}
  for line in open(path+'/u.data'):
    (user,movieid,rating,ts)=line.split('\t')
    prefs.setdefault(user,{})
    prefs[user][movies[movieid]]=float(rating)
  return prefs


