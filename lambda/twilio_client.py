import os
from twilio.rest import Client

class TwilioClient():
	def __init__(self):
		account_sid = "AC29be577f1d5e9f72cf53284998d77519"
		auth_token = os.environ["TWILIO_AUTH_TOKEN"]
		self.twilio = Client(account_sid, auth_token)

	def send_message(self, message):
		message = self.twilio.messages.create(
			body=message,
			from_="+12059286455",
			to="+16035081158"
		)
		print(message.sid)
