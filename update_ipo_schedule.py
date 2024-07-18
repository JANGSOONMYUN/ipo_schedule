import os
import json
import pandas as pd
from datetime import datetime, timedelta
import schedule
import time
from crawl_ipo_list import get_ipo_list, get_ipo_date
from google_api import get_calendar_id, get_upcoming_events, get_event_details, update_event, delete_event, add_event

KEYWORD_IPO = '공모주'
KEYWORD_PUBLIC = '상장'

IPO_START_TIME = 'T10:00:00+09:00'
IPO_END_TIME = 'T16:00:00+09:00'

PUBLIC_START_TIME = 'T09:00:00+09:00'
PUBLIC_END_TIME = 'T10:00:00+09:00'

ipo_df = get_ipo_list()
ipo_df['is_new_ipo'] = True
ipo_df['is_new_public'] = True



event_detail_format = {
    "summary": "",
    "creator": {
        "email": "jsm890803.3@gmail.com"
    },
    "start": {
        "dateTime": "",
        "timeZone": "Asia/Seoul"
    },
    "end": {
        "dateTime": "",
        "timeZone": "Asia/Seoul"
    }
}

def test():
    ipo_calendar_id = get_calendar_id()
    events = get_upcoming_events(ipo_calendar_id)
    # print(events)
        
    for e in events:
        event_id = e['id']
        detail = get_event_details(ipo_calendar_id, event_id)
        
        # gc = google calendar
        gc_ipo_name = detail['summary']
        gc_start_date = detail['start']['dateTime'].split('T')[0]
        gc_end_date = detail['end']['dateTime'].split('T')[0]
        
        gc_start_date = datetime.strptime(gc_start_date, "%Y-%m-%d")
        gc_end_date = datetime.strptime(gc_end_date, "%Y-%m-%d")
        
        
        detail['end']['dateTime']
        ipo_found = False
        for index, row in ipo_df.iterrows():
            if row['종목명'] in gc_ipo_name:
                ipo_found = True
                print(gc_ipo_name)
                if KEYWORD_IPO in gc_ipo_name:
                    ipo_df.at[index, 'is_new_ipo'] = False
                    ipo_start_date, ipo_end_date = get_ipo_date(row['공모주일정'])
                    # the IPO date has changed
                    if gc_start_date != ipo_start_date:
                        # update the date
                        date_string = ipo_start_date.strftime("%Y-%m-%d")
                        detail['start']['dateTime'] = date_string + IPO_START_TIME
                        detail['end']['dateTime'] = date_string + IPO_END_TIME
                        print('update_event')
                        print(detail)
                        update_event(ipo_calendar_id, event_id, detail)
                elif KEYWORD_PUBLIC in gc_ipo_name:
                    ipo_df.at[index, 'is_new_public'] = False
                    public_date = str(row['상장일']).replace('.', '-')
                    if public_date is None or len(public_date) < 2 or public_date == 'nan':
                        # delete the schedule
                        print('delete_event: public_date has not been decided.')
                        delete_event(ipo_calendar_id, event_id)
                    else:
                        public_date = datetime.strptime(public_date, "%Y-%m-%d")
                        if gc_start_date != public_date:
                            # update the date
                            date_string = public_date.strftime("%Y-%m-%d")
                            detail['start']['dateTime'] = date_string + PUBLIC_START_TIME
                            detail['end']['dateTime'] = date_string + PUBLIC_END_TIME
                            print('update_event')
                            print(detail)
                            update_event(ipo_calendar_id, event_id, detail)
    
        if KEYWORD_PUBLIC in gc_ipo_name: # 상장일은 삭제하지 않는다.
            ipo_found = True
        if ipo_found is False:
            # delete the schedule
            print('delete_event: ipo not found. it may be canceled.')
            delete_event(ipo_calendar_id, event_id)
    
    print(ipo_df)
    for index, row in ipo_df.iterrows():
        if row['is_new_ipo']:
            ipo_start_date, ipo_end_date = get_ipo_date(row['공모주일정'])
            date_string = ipo_start_date.strftime("%Y-%m-%d")
            
            event_details = event_detail_format.copy()
            event_details['summary'] = f'''({KEYWORD_IPO}) {row['종목명']} - {row['주간사']}'''
            event_details['start']['dateTime'] = date_string + IPO_START_TIME
            event_details['end']['dateTime'] = date_string + IPO_END_TIME
            
            print('add_event: new ipo.:', event_details['summary'], event_details['start']['dateTime'], event_details['end']['dateTime'], date_string, type(date_string))
            add_event(ipo_calendar_id, event_details)
            
        
        if row['is_new_public']:
            public_date = str(row['상장일']).replace('.', '-')
            if public_date is None or len(public_date) < 5:
                continue
            event_details = event_detail_format.copy()
            event_details['summary'] = f'''({KEYWORD_PUBLIC}) {row['종목명']} - {row['주간사']}'''
            event_details['start']['dateTime'] = public_date + PUBLIC_START_TIME
            event_details['end']['dateTime'] = public_date + PUBLIC_END_TIME
            
            print('add_event: new public.:', event_details['summary'], event_details['start']['dateTime'], event_details['end']['dateTime'], public_date, type(public_date))
            add_event(ipo_calendar_id, event_details)
            
            
if __name__ == '__main__':
    # Schedule the function to run every day at a specific time
    schedule.every().day.at("10:30").do(test)

    while True:
        schedule.run_pending()
        time.sleep(1)