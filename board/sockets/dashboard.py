from socketio.namespace import BaseNamespace
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.conf import settings
import Cookie
from django.utils import timezone


def getUserFromSession(sid):
	""" Find the session if not expired and return the corresponding user
		or None if none can be found
	"""
	try:
		s = Session.objects.get(pk=sid, expire_date__gte=timezone.now())
		# print "Session", s.get_decoded()
		uid = s.get_decoded()['_auth_user_id']
		# print "UID:", uid
		user = User.objects.get(pk=uid)
		return user
	except Session.DoesNotExist, User.DoesNotExist:
		return None


def getUserFromEnviron(environ):
	cookies = Cookie.SimpleCookie()
	cookies.load(environ['HTTP_COOKIE'])
	sid = cookies[settings.SESSION_COOKIE_NAME].value
	print sid
	user = getUserFromSession(sid)
	return user


class MessageBoardNamespace(BaseNamespace):
	""" This is a sort of controller for the messageboard """
	_registry = {}
	_users = {}

	def initialize(self):
		# print "CONNECTED, sending status"
		user = getUserFromEnviron(self.environ)
		print "Connected:", user
		if user:
			self._users[id(self)] = user
			self._registry[id(self)] = self
			self.emit('connectStatus', user.username)    # tell the client we are connected
		else:
			self.emit('error', "Credenziali di accesso errate.")


	def disconnect(self, *args, **kwargs):
		ids = id(self)
		if ids in self._registry: del (self._registry[ids])
		if ids in self._users: del (self._users[ids])
		super(MessageBoardNamespace, self).disconnect(*args, **kwargs)

	def on_message(self, message):
		print "MESSAGE: %s" % message
		ids = id(self)
		if not ids in self._users:
			self.emit('error', "Devi essere autenticato per mandare messaggi.")
			return
		user = self._users[ids]
		print "broadcasting '%s' from %s" % (message, user)
		self._broadcast('message', dict(u=user.username, m=message))

	def _broadcast(self, event, message):
		for s in self._registry.values():
			s.emit(event, message)
