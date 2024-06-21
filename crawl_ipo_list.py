import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

def get_ipo_info():
    # 38커뮤니케이션 공모주 페이지 URL
    url = 'https://www.38.co.kr/html/fund/?o=k'

    # 페이지 요청
    response = requests.get(url)
    response.encoding = 'euc-kr'  # 인코딩 설정

    # BeautifulSoup 객체 생성
    soup = BeautifulSoup(response.text, 'html.parser', from_encoding='euc-kr')

    # 테이블 찾기
    table = soup.find('table', {'summary': '공모주 청약일정'})

    # 테이블이 제대로 선택되었는지 확인
    if table is None:
        raise ValueError("Table with summary '공모주 청약일정' not found.")

    # 테이블 헤더 추출
    headers = [header.text.strip() for header in table.find_all('th')]

    # '종목명' 헤더에 링크 추가를 위해 새로운 헤더 구성
    headers.insert(headers.index('종목명') + 1, '링크')

    print(headers)

    # 데이터 추출
    rows = []
    for row in table.find_all('tr')[1:]:
        do_pass = False
        cols = row.find_all('td')
        cols_data = []
        for i, col in enumerate(cols):
            # '종목명' 컬럼에서 링크 추출
            if i == 0: 
                link = ''
                if col.find('a'):
                    link = col.find('a')['href']
                if col.text is None or len(col.text) == 0 or '스팩' in col.text:
                    do_pass = True
                    break
                cols_data.append(col.text.strip())
                cols_data.append(link)
            else:
                cols_data.append(col.text.strip())
        if not do_pass:
            rows.append(cols_data)

    # print(rows)
    # 데이터프레임 생성
    df = pd.DataFrame(rows, columns=headers)
    return df


# 날짜 범위를 처리하는 함수
def is_within_two_weeks(date_range):
    # 오늘 날짜와 2주 전 날짜 계산
    today = datetime.today()
    two_weeks_ago = today - timedelta(weeks=2)
    
    start_date_str, end_date_str = date_range.split('~')
    start_date = datetime.strptime(start_date_str.strip(), '%Y.%m.%d')
    
    current_year = start_date.year
    end_date_str = end_date_str.strip()
    date_format_size = len(end_date_str.split('.'))
    if date_format_size == 2:
        end_date_str = f'{current_year}.{end_date_str}'
    end_date = datetime.strptime(end_date_str, '%Y.%m.%d')
    
    return (start_date >= two_weeks_ago) or (end_date >= two_weeks_ago)


# 특정 페이지에서 상장일을 가져오는 함수
def get_public_date(page_url):
    response = requests.get(page_url)
    response.encoding = 'euc-kr'
    soup = BeautifulSoup(response.text, 'html.parser')
    # soup = BeautifulSoup(response.text, 'html.parser', from_encoding='euc-kr')
    # 예시: 상장일 정보가 <td> 태그 내에 "상장일"이라는 텍스트가 있는 경우
    public_date_td = soup.find('td', string='상장일')
    if public_date_td:
        return public_date_td.find_next_sibling('td').text.strip()
    return None


df = get_ipo_info()
# '청약일'이 날짜 범위인 데이터를 필터링
df_filtered = df[df['공모주일정'].apply(is_within_two_weeks)]

# 상장일 받아오기
public_date = get_public_date('https://www.38.co.kr/html/fund/?o=v&no=2053&l=&page=1')
print(public_date)


# 데이터프레임 출력
print(df_filtered)
# 필요한 경우 CSV 파일로 저장
df.to_csv('ipo_schedule_with_links.csv', index=False, encoding='utf-8-sig')
