import os
import json
import pandas as pd
from datetime import datetime, timedelta
import schedule
import time
import glob

from crawl_ipo_list import get_ipo_list, get_ipo_date
from google_api import get_calendar_id, get_upcoming_events, get_event_details, update_event, delete_event, add_event

KEYWORD_IPO = '공모주'
KEYWORD_PUBLIC = '상장'

IPO_START_TIME = 'T10:00:00+09:00'
IPO_END_TIME = 'T16:00:00+09:00'

PUBLIC_START_TIME = 'T09:00:00+09:00'
PUBLIC_END_TIME = 'T10:00:00+09:00'

def cleanup_old_csv_files(directory='.', days_to_keep=7):
    """
    1주일 이상 된 CSV 파일들을 삭제하는 함수 (파일명의 날짜 기준)
    
    Args:
        directory (str): 검사할 디렉토리 경로 (기본값: 현재 디렉토리)
        days_to_keep (int): 보관할 일수 (기본값: 7일)
    """
    try:
        # 현재 시간
        current_time = datetime.now()
        cutoff_date = current_time - timedelta(days=days_to_keep)
        
        # CSV 파일 패턴으로 모든 파일 찾기
        csv_pattern = os.path.join(directory, '*.csv')
        csv_files = glob.glob(csv_pattern)
        
        deleted_count = 0
        for csv_file in csv_files:
            # 파일명에서 날짜 추출 (yyyy-mm-dd 패턴)
            filename = os.path.basename(csv_file)
            date_pattern = r'(\d{4}-\d{2}-\d{2})'
            import re
            match = re.search(date_pattern, filename)
            
            if match:
                file_date_str = match.group(1)
                try:
                    file_date = datetime.strptime(file_date_str, "%Y-%m-%d")
                    
                    # 파일명의 날짜가 1주일 이상 된 경우 삭제
                    if file_date < cutoff_date:
                        try:
                            os.remove(csv_file)
                            print(f"삭제된 파일: {csv_file} (파일명 날짜: {file_date_str})")
                            deleted_count += 1
                        except Exception as e:
                            print(f"파일 삭제 실패: {csv_file}, 오류: {e}")
                except ValueError:
                    # 날짜 형식이 맞지 않는 파일은 건너뛰기
                    continue
            else:
                # 날짜 패턴이 없는 파일은 건너뛰기
                continue
        
        if deleted_count > 0:
            print(f"총 {deleted_count}개의 오래된 CSV 파일이 삭제되었습니다.")
        else:
            print("삭제할 오래된 CSV 파일이 없습니다.")
            
    except Exception as e:
        print(f"CSV 파일 정리 중 오류 발생: {e}")


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
    ipo_df = get_ipo_list()
    ipo_df['is_new_ipo'] = True
    ipo_df['is_new_public'] = True
    
    today = datetime.today()
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
            ipo_start_date, ipo_end_date = get_ipo_date(row['공모주일정'])
            
            # check if expired
            if ipo_start_date < today:
                ipo_df.at[index, 'is_new_ipo'] = False
                
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

from datetime import datetime, timedelta  
def wait_until(target_time):
    """현재 시간부터 목표 시간까지 대기하는 함수."""
    while True:
        now = datetime.now()
        if now >= target_time:
            break
        time.sleep(1)

        # print(f"현재 시간: {now}, 목표 시간: {target_time}")  # 현재 시간과 목표 시간을 콘솔에 출력
            
if __name__ == '__main__':
    # 프로그램 시작 시 오래된 CSV 파일 정리
    cleanup_old_csv_files()
    
    test()

    run_time = datetime.combine(datetime.now(), datetime.strptime("10:30", "%H:%M").time())
    if run_time < datetime.now():
        # 오늘 10:30가 지나쳤으면 내일로 설정
        run_time += timedelta(days=1)

    while True:
        wait_until(run_time)
        test()
        
        # 매일 실행 시 오래된 CSV 파일 정리
        cleanup_old_csv_files()

        # 다음 날의 같은 시간으로 설정
        run_time += timedelta(days=1)
        print(f"현재 시간: {datetime.now()}, 목표 시간: {run_time}")  # 현재 시간과 목표 시간을 콘솔에 출력