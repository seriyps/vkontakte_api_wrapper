#-*- coding: utf8 -*-
'''
Created on 15.04.2011

@author: seriy
'''
import urllib
import urlparse
import json

import vk_api_wrapper

import gettext
from gettext import lgettext as _
gettext.textdomain('vk_api_wrapper')

class VKAuthError(Exception):
    pass

class OAuth:
    permissions={
        "notify": _("Пользователь разрешил отправлять ему уведомления."),
        "friends": _("Доступ к друзьям."),
        "photos": _("Доступ к фотографиям."),
        "audio": _("Доступ к аудиозаписям."),
        "video": _("Доступ к видеозаписям."),
        "notes": _("Доступ заметкам пользователя."),
        "pages": _("Доступ к wiki-страницам."),
        "offers": _("Доступ к предложениям (устаревшие методы)."),
        "questions": _("Доступ к вопросам (устаревшие методы)."),
        "wall": _("Доступ к обычным и расширенным методам работы со стеной."),
        "messages": _("(для Standalone-приложений) Доступ к расширенным методам работы с сообщениями."),
        "offline": _("Доступ к API в любое время со стороннего сервера."),
    }

    auth_url="http://api.vkontakte.ru/oauth/authorize"

    def get_confirm_url(self, permissions, app_id):
        qstring=urllib.urlencode({#call to vkontakte API authorization
          "client_id": app_id,
          "redirect_uri": "http://api.vkontakte.ru/blank.html",
          "response_type": "token",
          "display": "popup",
          "scope": ",".join(permissions)
        })
        return "?".join((self.auth_url, qstring))

    def extract_creds(self, url):
        if "access_token=" in url:
            query_string=url.split("#", 1)[1]
            return dict((k, v.pop()) for k, v in urlparse.parse_qs(query_string).iteritems())
        elif "error=" in url:
            query_string=url.split("?", 1)[1]
            err=urlparse.parse_qs(query_string)
            raise VKAuthError(err["error"][0], err["error_description"][0])
        else:
            raise VKAuthError(None, _("Malformed response url"))

    def setup_by_confirmed_url(self, url):
        self.token=self.extract_creds(url)

    def __getstate__(self):
        return self.token

    def __setstate__(self, state):
        self.token=state

    @property
    def user_id(self):
        return self.token["user_id"]

    @property
    def api_kwargs(self):
        return {"access_token": self.token["access_token"]}

    def get_api_obj(self):
        return vk_api_wrapper.vkApiOAuth(**self.api_kwargs)


class VKAuth:
    permissions={
        1: _("Пользователь разрешил отправлять ему уведомления."),
        2: _("Доступ к друзьям."),
        4: _("Доступ к фотографиям."),
        8: _("Доступ к аудиозаписям."),
        16: _("Доступ к видеозаписям."),
        32: _("Доступ к предложениям."),
        64: _("Доступ к вопросам."),
        128: _("Доступ к wiki-страницам."),
        256: _("Добавление ссылки на приложение в меню слева."),
        512: _("Добавление ссылки на приложение для быстрой публикации на стенах пользователей."),
        1024: _("Доступ к статусам пользователя."),
        2048: _("Доступ заметкам пользователя."),
        4096: _("(для Desktop-приложений) Доступ к расширенным методам работы с сообщениями."),
        8192: _("Доступ к обычным и расширенным методам работы со стеной."),
    }

    auth_url="http://vkontakte.ru/login.php"

    def get_confirm_url(self, permissions, app_id):
        self._app_id=app_id
        qstring=urllib.urlencode({#call to vkontakte API authorization
          "app": app_id,
          "layout": "popup",
          "type": "browser",
          "settings": permissions,
        })
        return "?".join((self.auth_url, qstring))

    def extract_creds(self, url):
        json_string=urllib.unquote(url.split("session=")[1])
        return json.loads(json_string)

    def setup_by_confirmed_url(self, url, app_id=None):
        self.token=self.extract_creds(url)
        self.token["app_id"]=app_id or self._app_id

    def __getstate__(self):
        return self.token

    def __setstate__(self, state):
        self.token=state

    @property
    def user_id(self):
        return self.token["mid"]

    @property
    def api_kwargs(self):
        return {"sid": self.token["sid"],
                "secret": self.token["secret"],
                "mid": self.token["mid"],
                "app_id": self.token["app_id"]}

    def get_api_obj(self):
        return vk_api_wrapper.vkApiOld(**self.api_kwargs)
