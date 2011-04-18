# -*- coding: utf-8 -*-
'''
Created on 07.12.2010

@author: Sergey Prokhorov <me@seriyps.ru>
'''
import hashlib
import urllib
import json

__all__=['vkException',
         'vkApiOAuth',
         'vkApiOld']

class vkException(Exception):

    def __init__(self, code, msg, url, response):
        self.code=code
        self.msg=msg
        self.response=response
        self.url=url
        Exception.__init__(self, code, msg, url, response)


def Download(url, params):
    qstring=urllib.urlencode(params)
    return urllib.urlopen("?".join((url, qstring))).read()


class _vkApiBase(object):

    def __init__(self):
        self._prefix=[]

    """Support for api.namespace.method(**kwargs) calls below"""
    def __getattr__(self, name):
        if ("(" in name) or (name in self._prefix):
            return self#protection from ipython introspection calls
        self._prefix.append(name)
        return self

    def __call__(self, **kwargs):
        if self._prefix:
            method=".".join(self._prefix)
            self._prefix=[]
        else:
            method=kwargs.pop("method")
        return self._load(method, **kwargs)


class vkApiOAuth(_vkApiBase):
    """Vkontakte.ru (vk.com) API wrapper for Gwibber
    == Usage ==
    Initialization:
        api=vk_api(access_token)
        "access_token" can be retrieved from call to http://api.vkontakte.ru/oauth/authorize
        (see http://vkontakte.ru/developers.php?o=-1&p=%C0%E2%F2%EE%F0%E8%E7%E0%F6%E8%FF%20%EA%EB%E8%E5%ED%F2%F1%EA%E8%F5%20%EF%F0%E8%EB%EE%E6%E5%ED%E8%E9)
    Make calls to simple methods (has no dots in name, like "getProfiles", "isAppUser"):
        res=api.method(arg_name1=arg1, arg_name2=arg2)
        eg res=api.getProfiles(uids="535397,1", fields="uid,first_name,last_name")
    Make calls to namespaced methods (has dots in name, like "wall.post", "newsfeed.get"):
        res=api.namespace.method(arg_name1=arg1, arg_name2=arg2)
        eg res=api.wall.post(message="New wall post from API")
    Alternative call syntax (better performance):
        res=api._load('namespace.method', arg_name1=arg1, arg_name2=arg2)
        eg res=api._get('wall.post', message="New wall post from API")
    """

    api_url='https://api.vkontakte.ru/method/%s'

    def __init__(self, access_token, downloader=None):
        self._access_token=access_token
        self._prefix=[]
        self._downloader=downloader or Download
        super(vkApiOAuth, self).__init__()

    def _load(self, method, **params):
        """Make call by method name and arguments"""
        params["access_token"]=self._access_token
        url=self.api_url%method
        res=json.loads(self._downloader(url, params))

        if res.has_key("error"):
            raise vkException(res["error"]["error_code"],
                              res["error"]["error_msg"],
                              "%s?%s"%(url, urllib.urlencode(params)),
                              res)
        return res


class vkApiOld(_vkApiBase):
    """Vkontakte.ru (vk.com) API wrapper
    == Usage ==
    Initialization:
        api=vkApi(session, secret, mid, app_id)
        "session", "secret", "mid" can be retrieved from call to http://vkontakte.ru/login.php
        "app_id" is an application id from application administrative panel
        (see http://vk.com/developers.php?o=-17680044&p=Desktop+Application+Authorization)
    Make calls to simple methods (has no dots in name, like "getProfiles", "isAppUser"):
        res=api.method(arg_name1=arg1, arg_name2=arg2)
        eg res=api.getProfiles(uids="535397,1", fields="uid,first_name,last_name")
    Make calls to namespaced methods (has dots in name, like "wall.post", "newsfeed.get"):
        res=api.namespace.method(arg_name1=arg1, arg_name2=arg2)
        eg res=api.wall.post(message="New wall post from API")
    Alternative call syntax (better performance):
        res=api._load('namespace.method', arg_name1=arg1, arg_name2=arg2)
        eg res=api._load('wall.post', message="New wall post from API")
    """

    api_url='http://api.vkontakte.ru/api.php'
    version='3.0'

    def __init__(self, sid, secret, mid, app_id,
				downloader=None):
        self._session=sid
        self._secret=secret
        self._mid=mid
        self._app_id=app_id
        self._prefix=[]
        self._downloader=downloader or Download
        super(vkApiOld, self).__init__()

    def _make_sig(self, params):
        """Create request signature"""
        params="".join("%s=%s"%(k, v) for k, v in sorted(params.items()))
        sig_str=unicode(self._mid)+unicode(params)+unicode(self._secret)
        return hashlib.md5(sig_str).hexdigest()

    def _load(self, method, **kwargs):
        """Make call by method name and arguments"""
        for k, v in kwargs.items():#convert lists/tuples to comma-separated string
            if isinstance(v, (tuple, list)):
                kwargs[k]=",".join(str(e) for e in v)#convert each element to str and join by comma

        params=dict(kwargs, **{'api_id': str(self._app_id),
                               'method': method,
                               'v': self.version,
                               'format': 'JSON'})
        params["sig"]=self._make_sig(params)
        params["sid"]=self._session

        res=json.loads(self._downloader(self.api_url, params))

        if res.has_key("error"):
            raise vkException(res["error"]["error_code"],
                              res["error"]["error_msg"],
                              "%s?%s"%(self.api_url, urllib.urlencode(params)),
                              res)
        return res
