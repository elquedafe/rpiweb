import tweepy
import telepot
import smtplib

class NOTIFICATIONHANDLER:
	def __init__(self):
		#twitter
		self._consumer_key="hq4wypbIiQFPH13QOmKB8t9ss"
		self._consumer_secret="TQi9r79BET0jimOz1jClQ7z6fLBxGrJoEaUdAexeBzhitb26Ky"
		self._access_token="1064175532877729792-xMjH9Vx3Ia8Mz4k3teIV1U8c0b7K2a"
		self._access_token_secret="2WIP9cbOefnW7r8AK6IbclMko05yWlyb0K26PBWIpkCu2"

		self._auth = tweepy.OAuthHandler(self._consumer_key, self._consumer_secret)
		self._auth.set_access_token(self._access_token, self._access_token_secret)
		self._tweepyapi = tweepy.API(self._auth)

	def sendNotification(self, msg, bot=None, telGroup=None, persona=None):
		server = smtplib.SMTP('smtp.gmail.com:587')
		server.connect("smtp.gmail.com",587)
		server.ehlo()
		server.starttls()
		server.ehlo()
		server.login('mayordomobot', "caputloqueseve")
		server.sendmail('mayordomobot@gmail.com', 'mayordomobot@gmail.com', msg)
		server.quit()

		if (len(msg)<140):
			self._tweepyapi.update_status(msg)

		if (bot is not None):
			if (persona is None):
				persona = ''
			bot.sendMessage(telGroup, msg+persona)