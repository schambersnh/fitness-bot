from mfp_client import MFPClient
from spreadsheet_client import SpreadsheetNutritionClient
from twilio_client import TwilioClient
from fitness_message_builder import FitnessMessageBuilder
from datetime import date


def get_day_totals(year, month, day):
	nutrition_data = None
	try:
		return get_nutrition_data_from_mfp(year, month, day)
	except Exception as e:
		print('could not log into myfitness pal:')
		print(e)
		return get_totals_from_spreadsheet()


def get_nutrition_data_from_mfp(year, month, day):
	mfpClient = MFPClient()
	return mfpClient.get_mfp_data_by_day(year, month, day)   

def get_totals_from_spreadsheet():
	print('falling back to spreadsheet....')
	spreadsheetNutritionClient = SpreadsheetNutritionClient()
	return spreadsheetNutritionClient.get_spreadsheet_nutrition_data()

def create_and_send_fitness_message():
	today = date.today()
	fitnessMessageBuilder = FitnessMessageBuilder()

	#get summary header
	message = fitnessMessageBuilder.serialize_header(today)

	#get nutritional information
	nutrition_data = get_day_totals(today.year, today.month, today.day)
	message += fitnessMessageBuilder.serialize_nutrition_data(nutrition_data)

	print(message)
	TwilioClient().send_message(message)


def handler(event, context):
	create_and_send_fitness_message() 	

if __name__ == "__main__":
    create_and_send_fitness_message()


