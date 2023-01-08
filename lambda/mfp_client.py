from webdriver_auth import SeleniumAuth
import myfitnesspal

auth = SeleniumAuth(
    username='stephenchambers515@gmail.com',
    password='515aug06SC*',
    creds_filepath='creds.json',
    use_stored_credentials=False)


class MFPClient():
    def __init__(self):
        if auth.login(max_wait_time=60):
            #print('auth cookie jar')
            #print(auth.cookiejar)
            #print(auth.cookies)
            #print('attempting to load cookie jar')
            
            auth.load_cookie_jar()
            
            #print('auth cookie jar')
            #print(auth.cookiejar)
            self.mfp = myfitnesspal.Client(
                cookiejar=auth.cookiejar)

    def get_mfp_data_by_day(self, year, month, day):
        nutrition_data = {}
        mfpCurrentDayData = self.mfp.get_date(2023,1,7)
        
        nutrition_data['entries'] = mfpCurrentDayData.entries
        nutrition_data['water'] = mfpCurrentDayData.water
        nutrition_data['meals'] = mfpCurrentDayData.meals
    
        nutrition_data['totals'] = mfpCurrentDayData.totals
        nutrition_data['retrieval'] = 'mfp'

        return nutrition_data