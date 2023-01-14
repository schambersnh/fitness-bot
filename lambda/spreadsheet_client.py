import httplib2
import os

from apiclient import discovery

discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                'version=v4')
service = discovery.build(
    'sheets',
    'v4',
    http=httplib2.Http(),
    discoveryServiceUrl=discoveryUrl,
    developerKey=os.environ["SPREADSHEET_API_KEY"])


class SpreadsheetNutritionClient():
    def get_spreadsheet_nutrition_data(self):
        nutrition_data = {}
        nutrition_data['totals'] = {}
        spreadsheetId = '1-XYteIgeAccDfDRnl4ZsOV-HUONsrbu_8LdNdB_V2qc'
        rangeName = 'sheet1!A1:E2'
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheetId, range=rangeName).execute()
        values = result.get('values', [])

        date = values[1][4]
        print(date)


        nutrition_data['totals']['calories'] = float(values[1][0])
        nutrition_data['totals']['carbohydrates'] = float(values[1][1])
        nutrition_data['totals']['fat'] = float(values[1][2])
        nutrition_data['totals']['protein'] = float(values[1][3])

        nutrition_data['retrieval'] = 'spreadsheet'

        print('retrieved nutrition_data from spreadsheet')
        print(nutrition_data)

        return nutrition_data

if __name__ == "__main__":
    nutrition_data = SpreadsheetNutritionClient().get_spreadsheet_nutrition_data()