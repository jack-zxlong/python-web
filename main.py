import web
import threading
from threading import RLock
from time import ctime, sleep
import urllib2
import json
import hashlib

APPID="wx86f26fb195aecf76"
APPSECRET="b62e5b8d7befbe2438130eaa281aa933"

access_token="accesstoken"
looptime="7200"

urls = (
				'/wx', 'WxHandle',
				'/', 'WebHandle',
				'/api/getUserInfo.do', 'UserInfoHandle'
	   )

class UserInfoHandle(object):
	def __init__(self):
		self.web_token=""
		self.openid=""

	def GET(self):
		data = web.input()
		code = data.code
		print "code======= "+code
		if len(code) == 0:
			print "code is null"
			return "error"
		if len(self.web_token) == 0:
			url="https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code" %(APPID, APPSECRET, code)
			req = urllib2.Request(url)
			res_data = urllib2.urlopen(req)
			res  = res_data.read()
			rjson = json.loads(res)

			print rjson

			try:
				self.web_token=rjson['access_token']
				self.openid=rjson['openid']
			except Exception,e:
				print Exception, ":", e
				return "error,e"


		url_user="https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN" %(self.web_token , self.openid)
		req_user = urllib2.Request(url_user)
		res_data_user = urllib2.urlopen(req_user)
		res_user  = res_data_user.read()
		rjson_user = json.loads(res_user)
		print "userinfo====== "+res_user
		return rjson_user 

class WebHandle(object):
	def GET(self):
		render = web.template.render('templates')
		return render.index()

class WxHandle(object):
	def GET(self):
		data = web.input()
		if len(data) == 0:
			return "hello, this is handle view"
		signature = data.signature
		timestamp = data.timestamp
		nonce = data.nonce
		echostr = data.echostr
		token = "zyebank"

		list = [token, timestamp, nonce]
		list.sort()
		sha1 = hashlib.sha1()
		map(sha1.update, list)
		hashcode = sha1.hexdigest()
		print "handle/GET func: hashcode, signature: ", hashcode, signature
		if hashcode == signature:
			return echostr
		else:
			return ""

def get_access_token():
	global access_token
	global looptime
	url="https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" %(APPID, APPSECRET)
	req = urllib2.Request(url)
	res_data = urllib2.urlopen(req)
	res  = res_data.read()

	rjson = json.loads(res)

	access_token = rjson['access_token']
	looptime =  rjson['expires_in']

def accessTokenProc(arg):
	global looptime
	global access_token
	while True:
		get_access_token()
		print access_token
		sleep(looptime-60)

if __name__ == '__main__':
	accessTokenServer=threading.Thread(target=accessTokenProc, args=(u'kkkkkk',))
	accessTokenServer.setDaemon(True)
	accessTokenServer.start()

	app = web.application(urls, globals())
	app.run()
