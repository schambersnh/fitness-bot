class FitnessMessageBuilder():
	def serialize_header(self, today):
		serialized_day = str(today.month) + "/" + str(today.day) + "/" + str(today.year)
		header_message = "Hi there, it's fitbot! Here's Stephen's fitness summary for " + serialized_day
		header_message += "\n\nGoal Nutrition: " + "1940/194/65/146"
		return header_message

	def convert_water(self, water):
		water = water * 0.033814
		return str(round(water)) + ' oz'

	def slash_nutrition(self, calories, carbs, fat, protein):
		return "" + str(round(calories)) + "/" + str(round(carbs)) + "/" + str(round(fat)) + "/" + str(round(protein))

	def serialize_nutrition_data(self, nutrition_data):
		nutritional_message = ""

		if nutrition_data['retrieval'] == 'spreadsheet' and "message" in nutrition_data:
			return nutrition_data['message']

		calories = nutrition_data['totals']['calories']
		carbs = nutrition_data['totals']['carbohydrates'] 
		fat = nutrition_data['totals']['fat']
		protein = nutrition_data['totals']['protein']

		nutritional_message += "\n\nNutritional Totals: " + self.slash_nutrition(calories, carbs, fat, protein)

		if nutrition_data['retrieval'] != 'mfp':
			nutritional_message += "\n\nWeight: " + nutrition_data['weight'] + ' lbs'
			nutritional_message += "\nWater: " + nutrition_data['water'] + ' oz'

		if nutrition_data['retrieval'] == 'mfp':
			nutritional_message += "\n\nWater: " + self.convert_water(nutrition_data['water'])

			for meal in nutrition_data['meals']:
				if meal.entries:
					nutritional_message += "\n\n" + meal.name + ":"
					for entry in meal.entries:
						entry_calories = entry['calories']
						entry_carbs = entry['carbohydrates']
						entry_fat = entry['fat']
						entry_protein = entry['protein']
						nutritional_message += "\n" + entry.name + ": " + self.slash_nutrition(entry_calories, entry_carbs, entry_fat, entry_protein)
		return nutritional_message
