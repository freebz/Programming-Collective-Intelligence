from pydelicious import get_popular,get_userposts,get_urlposts

def initializeUserDict(tag,count=5):
  user_dict={}
  # count개의 인기 게시물을 얻음
  for p1 in get_popular(tag=tag)[0:count]:
    # 이 게시물을 올린 모든 사용자를 얻음
    for p2 in get_urlposts(p1['href']):
      user=p2['user']
      user_dict[user]={}
  return user_dict
  
def fillItems(user_dict):
  all_items={}
  # 모든 사용자가 올린 링크를 수집
  for user in user_dict:
    for i in range(3):
      try:
        posts=get_userposts(user)
        break
      except:
        print "Failed user "+user+", retrying"
        time.sleep(4)
    for post in posts:
      url=post['href']
      user_dict[user][url]=1.0
      all_items[url]=1
    
  # 평가점수가 없는 경우 0으로 채움
  for ratings in user_dict.values():
    for item in all_items:
      if item not in ratings:
        ratings[item]=0.0
