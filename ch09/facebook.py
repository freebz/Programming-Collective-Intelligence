#-*- coding: utf-8 -*-

# 07: 지지벡터머신

# 08: LIBSVM 사용

# 09: 페이스북 매칭

# 개발자 키 얻기

import urllib,md5,webbrowser,time
from xml.dom.minidom import parseString

apikey="Your API Key"
secret="Your Secret Key"
FacebookURL = "https://api.facebook.com/restserver.php"


def getsinglevalue(node,tag):
  nl=node.getElementsByTagName(tag)
  if len(nl)>0:
    tagNode=nl[0]
    if tagNode.hasChildNodes():
      return tagNode.firstChild.nodeValue
  return ''

def callid():
  return str(int(time.time()*10))



# 세션 생성하기

class fbsession:
  def __init__(self):
    self.session_secret=None
    self.session_key=None
    #self.token=self.createtoken()
    self.createtoken()
    webbrowser.open(self.getlogin())
    print "Press enter after logging in:",
    raw_input()
    self.getsession()

  def sendrequest(self,args):
    args['api_key'] = apikey
    args['sig'] = self.makehash(args)
    post_data = urllib.urlencode(args)
    url = FacebookURL + "?" + post_data
    data=urllib.urlopen(url).read()
    return parseString(data)

  def makehash(self,args):
    hasher = md5.new(''.join([x + '=' + args[x] for x in sorted(args.keys())]))
    if self.session_secret: hasher.update(self.session_secret)
    else: hasher.update(secret)
    return hasher.hexdigest()

  def createtoken(self):
    res = self.sendrequest({'method':"facebook.auth.createToken"})
    self.token = getsinglevalue(res,'token')

  def getlogin(self):
    return "http://api.facebook.com/login.php?api_key="+apikey+\
           "&auth_token=" + self.token

  def getsession(self):
    doc=self.sendrequest({'method':'facebook.auth.getSession',
                          'auth_token':self.token})
    self.session_key=getsinglevalue(doc,'session_key')
    self.session_secret=getsinglevalue(doc,'secret')



# 친구 데이터 다운로드하기

  def getfriends(self):
    doc=self.sendrequest({'method':'facebook.friends.get',
                          'session_key':self.session_key,'call_id':callid()})
    results=[]
    for n in doc.getElementsByTagName('result_elt'):
      results.append(n.firstChild.nodeValue)
    return results

  def getinfo(self,users):
    ulist=','.join(users)

    fields='gender,current_location,relationship_status,'+\
           'affiliations,hometown_location'

    doc=self.sendrequest({'method':'facebook.users.getInfo',
                          'session_key':self.session_key,'call_id':callid(),
                          'users':ulist,'fields':fields})
    
    results={}
    for n,id in zip(doc.getElementsByTagName('result_elt'),users):
      # 위치를 얻음
      locnode=n.getElementsByTagName('hometown_location')[0]
      loc=getsinglevalue(locnode,'city')+', '+getsinglevalue(locnode,'state')

      # 학교를 얻음
      college=''
      gradyear='0'
      affiliations=n.getElementsByTagName('affiliations_elt')
      for aff in affiliations:
        # 유형 1은 대학임
        if getsinglevalue(aff,'type')=='1':
          college=getsinglevalue(aff,'name')
          gradyear=getsinglevalue(aff,'year')

      results[id]={'gender':getsinglevalue(n,'gender'),
                   'status':getsinglevalue(n,'relationship_status'),
                   'location':loc,'college':college,'year':gradyear}
    return results




# 중매 데이터 세트 만들기

  def arefriends(self,idlist1,idlist2):
    id1=','.join(idlist1)
    id2=','.join(idlist2)
    doc=self.sendrequest({'method':'facebook.friends.areFriends',
                          'session_key':self.session_key,'call_id':callid(),
                          'id1':id1,'id2':id2})
    results=[]
    for n in doc.getElementsByTagName('result_elt'):
      results.append(n.fristChild.nodeValue)
    return results


  def makedataset(self):
    from advancedclassify import milesdistance
    # 내 친구의 정보를 얻음
    friends=self.getfriends()
    info=self.getinfo(friends)
    ids1,ids2=[],[]
    rows=[]

    # 모든 친구 쌍을 살펴볼 이중 루프를 돔
    for i in range(len(friends)):
      f1=friends[i]
      data1=info[f1]
      
      # i+1에서 시작해서 이중 검사를 피함
      for j in range(i+1,len(friends)):
        f2=friends[j]
        data2=info[f2]
        ids1.append(f1)
        ids2.append(f2)

        # 데이터에서 몇 가지 숫자를 생성함
        if data1['college']==data2['college']: sameschool=1
        else: sameschool=0
        mail1=(data1['gender']=='Male') and 1 or 0
        mail2=(data2['gender']=='Male') and 1 or 0

        row=[male1,int(data1['year']),male2,int(data2['year']),sameschool]
        rows.append(row)
    # 모든 사람 쌍마다 블록 단위로 arefriends를 호출함
    arefriends=[]
    for i in range(0,len(ids1),30):
      j=min(i+20,len(ids1))
      pa=self.arefriends(ids1[i:j],ids2[i:j])
      arefriends+=pa
    return arefriends,rows



# SVM 모델 생성하기
