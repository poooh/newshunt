import urllib,urllib2
from urlparse import *
import sys
import os
from oauth2 import *
from gluon import *
import cgi
import cgitb; cgitb.enable()
import json


def index():
    return dict()

def tw_signin():
    app = Consumer(key= "dJvGhNEaw6ivlQGals8g1mMu9", secret= "n5qBLoWVO77KHLfAUB1Z5wTYtO7ed62XmNbq52bmYjEFYdJNQi")
    client = Client(app)
    response, content = client.request('https://twitter.com/oauth/request_token', "GET")
    if response['status'] != '200':
        raise HTTP(response['status']),str(content)
    request_token = dict(parse_qsl(content))
    session.request_token = request_token
    redirect_location = "%s?oauth_token=%s" % ('https://twitter.com/oauth/authenticate', request_token['oauth_token'])
    redirect(redirect_location)
    return

def permission():
    if not(session.request_token is None):
        consumer = Consumer(key= "dJvGhNEaw6ivlQGals8g1mMu9", secret= "n5qBLoWVO77KHLfAUB1Z5wTYtO7ed62XmNbq52bmYjEFYdJNQi")
        token = None
        try:
            token = Token(session.request_token['oauth_token'],session.request_token['oauth_token_secret'])
        except:
            redirect(URL(r=request,c='default', f='index'))
        token.set_verifier(request.vars['oauth_verifier'])
        client = Client(consumer, token)
        response, content = client.request('https://twitter.com/oauth/access_token', "POST")
        if response['status'] == '401':
            BEAUTIFY("you have denied the request")
            redirect(URL(r=request,c='default', f='index'))
        if response['status'] != '200':
            return response['status'],str(content)
        access_token = dict(parse_qsl(content))
        session.access_token = access_token
        user_id = int(access_token['user_id'])
        name =(access_token['screen_name'])
        tw_status_query = """
            INSERT IGNORE INTO  tw_details(screen_name,user_id,tw_token,tw_token_secret) VALUES ('%s','%s','%s','%s')
    ON DUPLICATE KEY UPDATE tw_token='%s',tw_token_secret='%s';"""%(name,user_id,session.access_token['oauth_token'],session.access_token['oauth_token_secret'],session.access_token['oauth_token'],session.access_token['oauth_token_secret'])
    tw_status = db.executesql(tw_status_query)
    redirect(URL(r=request,c='default', f='tw_trends'))
    return

def tw_trends():
    if not(session.request_token is None):
        consumer = Consumer(key= "dJvGhNEaw6ivlQGals8g1mMu9", secret= "n5qBLoWVO77KHLfAUB1Z5wTYtO7ed62XmNbq52bmYjEFYdJNQi")
        token = Token(session.access_token['oauth_token'],session.access_token['oauth_token_secret'])
        client = Client(consumer, token)
        #response, content = client.request('https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=poojakvj', "GET")
        #response, content = client.request('https://api.twitter.com/1.1/trends/available.json', "GET")
        response, content = client.request('https://api.twitter.com/1.1/trends/place.json?id=23424848', "GET")
        data = json.loads(content)
        #serch_trends = data[0]["trends"][1]['name']
        toptrends = []
        for i in data[0]["trends"]:
        	serch_trends = i
        	Ndata = serch_trends['name']
        	obj = Ndata.split("#")
        	toptrends.append(obj)
        #print toptrends
        return dict(content = toptrends)

def get_extented_token():
    token = request.vars.token
    url1 = "https://graph.facebook.com/"
    url1 += 'me?access_token=%s'%(token)
    details = urllib2.urlopen(url1)
    dict_response = json.loads(details.read())
    name = dict_response['name']
    email_id = dict_response['email']
    fb_id = dict_response['id']
    session.email_id = email_id
    session.fb_id = fb_id
    url = "https://graph.facebook.com/"
    url += "oauth/access_token?client_id="+fbconfig.app_id+"&client_secret="+fbconfig.app_secret
    url += "&grant_type=fb_exchange_token"
    url += "&fb_exchange_token=%s"%(token)

    data = urllib2.urlopen(url)

    interm = data.read().split("=")
    token = interm[1].split("&")
    extended_token = token[0]
    session.extended_token = extended_token
    expires = interm[2]

def fbuser():
    token = request.vars.token
    url1 = "https://graph.facebook.com/"
    url1 += 'me?access_token=%s'%(token)
    details = urllib2.urlopen(url1)
    dict_response = json.loads(details.read())
    name = dict_response['name']
    email_id = ""
    try:
        email_id = dict_response['email']
    except:
        pass
    fb_id = dict_response['id']
    url = "https://graph.facebook.com/"
    url += "oauth/access_token?client_id="+fbconfig.app_id+"&client_secret="+fbconfig.app_secret
    url += "&grant_type=fb_exchange_token"
    url += "&fb_exchange_token=%s"%(token)

    data = urllib2.urlopen(url)
    interm = data.read().split("=")
    token = interm[1].split("&")
    extended_token = token[0]
    session.extended_token = extended_token
    expires = interm[2]
    fb_status = db.executesql("""INSERT IGNORE INTO  fb_details(name,email_id,fb_id,access_token,expiry) VALUES (%s,%s,%s,%s,%s);""",(name,email_id,session.fb_id,extended_token,expires))
    return dict()
