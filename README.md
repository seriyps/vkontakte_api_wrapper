Тонкая обертка над vkontakte.ru API
===================================

Библиотека не содержит в себе кода методов VKontakte API. Все функции генерируются
во время выполнения.
Библиотека использует JSON версию API.
Изначально библиотека была написана во время разработки [плагина VKontakte для Gwibber](https://code.launchpad.net/~seriy-pr/gwibber/vkontakte-ru-plugin).

Примеры использования
---------------------

### Инициализация

	import vk_api_wrapper
	api=vk_api_wrapper.vkApi(sid="41b...22550",
							mid=53...7,
							secret="97......85",
							app_id=20....5)

Параметры "sid", "secret", "mid" можно получить запросос к http://vkontakte.ru/login.php
"app_id" - ID приложения из административной панели приложения.
Подробнее см на [Desktop+Application+Authorization](http://vk.com/developers.php?o=-17680044&p=Desktop+Application+Authorization).

### Выполнение простых запросов

(не имеют точек в имени (пространств имен), вроде "getProfiles", "isAppUser"):

	api.isAppUser()
	>>> {u'response': u'1'}
	
	api.getProfiles(uids=(1,535397),
					fields=("uid", "first_name", "photo"))
	>>> {u'response': [{u'first_name': u'\u041f\u0430\u0432\u0435\u043b',
		                u'photo': u'http://cs1495.vkontakte.ru/u00001/e_257ab0fd.jpg',
		                u'uid': 1},
		               {u'first_name': u'\u0421\u0435\u0440\u0433\u0435\u0439',
		                u'photo': u'http://cs9419.vkontakte.ru/u535397/e_07a24e4a.jpg',
		                u'uid': 535397}]}

### Выполнение запросов к методам в пространствах имен.

(имеют точку в имени, вроде "wall.post", "newsfeed.get"):

	api.wall.get(count=1)
	>>> {u'response': [563,
		               {u'comments': {u'can_post': 1, u'count': 0},
		                u'date': 1302122508,
		                u'from_id': 535397,
		                u'id': 715,
		                u'likes': {u'can_like': 1,
		                           u'can_publish': 0,
		                           u'count': 3,
		                           u'user_likes': 0},
		                u'online': 1,
		                u'post_source': {u'type': u'api'},
		                u'reply_count': 0,
		                u'text': u'\u0412\u044b\u0448\u0435\u043b Gnome 3. ... #gnome3',
		                u'to_id': 535397}]}


Vkontakte.ru (vk.com) API wrapper
=================================

### Initialization:

	api=vkApi(session, secret, mid, app_id)

"session", "secret", "mid" can be retrieved from call to http://vkontakte.ru/login.php
"app_id" is an application id from application administrative panel
See [Desktop+Application+Authorization](http://vk.com/developers.php?o=-17680044&p=Desktop+Application+Authorization) for details

### Make calls to simple methods.

(has no dots in name, like "getProfiles", "isAppUser"):

	res=api.method(arg_name1=arg1, arg_name2=arg2)

eg `res=api.getProfiles(uids="535397,1", fields="uid,first_name,last_name")`
    
### Make calls to namespaced methods.

(has dots in name, like "wall.post", "newsfeed.get"):

	res=api.namespace.method(arg_name1=arg1, arg_name2=arg2)

eg `res=api.wall.post(message="New wall post from API")`

### Alternative call syntax.

(better performance):

	res=api._load('namespace.method', arg_name1=arg1, arg_name2=arg2)

eg `res=api._load('wall.post', message="New wall post from API")`
