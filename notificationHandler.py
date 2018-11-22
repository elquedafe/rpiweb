import tweepy
import telepot
import smtplib
import fileHandler

class NOTIFICATIONHANDLER:
	def __init__(self):
		#twitter
		self._consumer_key = None
		self._consumer_secret = None
		self._access_token = None
		self._access_token_secret = None
		self.readParameters()
		self._auth = tweepy.OAuthHandler(self._consumer_key, self._consumer_secret)
		self._auth.set_access_token(self._access_token, self._access_token_secret)
		self._tweepyapi = tweepy.API(self._auth)

	def readParameters(self):
		fileH = fileHandler.FILEHANDLER()
		self._consumer_key = fileH.readParam('tweeterconsumerkey')
		self._consumer_secret = fileH.readParam('tweeterconsumersecret')
		self._access_token = fileH.readParam('twetteraccesstoken')
		self._access_token_secret = fileH.readParam('tweeteraccesstokensecret')

	def sendNotification(self, msg, bot=None, telGroup=None, persona=None):
		server = smtplib.SMTP('smtp.gmail.com:587')
		server.connect("smtp.gmail.com",587)
		server.ehlo()
		server.starttls()
		server.ehlo()
		fileH = fileHandler.FILEHANDLER()
		server.login(fileH.readParam('emaillogin'), fileH.readParam('emailpasswd'))
		server.sendmail(fileH.readParam('email'), fileH.readParam('email'), msg)
		server.quit()

		if (len(msg)<140):
			self._tweepyapi.update_status(msg)

		if (bot is not None):
			if (persona is None):
				persona = ''
			bot.sendMessage(telGroup, msg+persona)