# IPO 스케줄 관리 프로그램

공모주 정보를 크롤링하여 Google Calendar에 자동으로 스케줄을 추가/업데이트하는 프로그램입니다.

## 주요 기능

- [x] 공모주 목록 크롤링
- [x] 각 공모주의 상세 정보 수집
- [x] Google Calendar API 연동
- [x] Google Calendar에 공모주 스케줄 자동 추가/업데이트
- [x] 웹 브라우저 없이 Google API 인증
- [x] 오래된 CSV 파일 자동 정리 (1주일 이상)

## 사용법

### 1. 환경 설정

#### 필요한 패키지 설치
```bash
pip install pandas schedule google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

#### Google API 설정
1. Google Cloud Console에서 서비스 계정 생성
2. JSON 키 파일 다운로드
3. `google_api.py` 파일에서 서비스 계정 정보 설정

### 2. 프로그램 실행

#### 일회성 실행
```bash
python update_ipo_schedule.py
```

#### 백그라운드 실행 (Linux/Mac)
```bash
nohup python update_ipo_schedule.py > ipo_schedule.log 2>&1 &
```

### 3. 실행 시간 설정

기본적으로 매일 오전 10:30에 실행됩니다. 시간을 변경하려면 `update_ipo_schedule.py` 파일의 다음 부분을 수정하세요:

```python
run_time = datetime.combine(datetime.now(), datetime.strptime("10:30", "%H:%M").time())
```

### 4. 로그 확인

프로그램 실행 시 다음과 같은 로그가 출력됩니다:
- 새로 추가된 공모주 스케줄
- 업데이트된 스케줄
- 삭제된 오래된 CSV 파일
- 오류 메시지

### 5. CSV 파일 관리

- 프로그램은 매일 실행 시 1주일 이상 된 CSV 파일을 자동으로 삭제합니다
- 파일명 패턴: `*yyyy-mm-dd.csv`
- 보관 기간은 `cleanup_old_csv_files()` 함수의 `days_to_keep` 매개변수로 조정 가능

## 파일 구조

```
ipo_schedule/
├── update_ipo_schedule.py    # 메인 프로그램
├── crawl_ipo_list.py         # 공모주 정보 크롤링
├── google_api.py            # Google Calendar API 연동
├── *.csv                    # 크롤링된 데이터 (자동 정리됨)
└── README.md               # 이 파일
```

## 문제 해결

### Google API 인증 오류
- 서비스 계정 JSON 파일이 올바른 위치에 있는지 확인
- Google Calendar API가 활성화되어 있는지 확인

### 크롤링 오류
- 인터넷 연결 상태 확인
- 대상 웹사이트의 구조 변경 여부 확인

### 스케줄 업데이트 실패
- Google Calendar 권한 설정 확인
- 캘린더 ID가 올바른지 확인

## To do
- [x] Crawling IPO list
- [x] Getting the detail information of each IPO
- [x] Connecting to the Google Calendar
- [x] Adding or updating IPO schedule to the Google Calendar
- [x] Getting authority from the Google API without web browser


## 서비스 계정 생성 방법
```
Google Cloud Console 접속:

Google Cloud Console에 접속합니다.
프로젝트 선택 또는 생성:

이미 존재하는 프로젝트를 선택하거나 새 프로젝트를 생성합니다.
서비스 계정 생성:

사이드 메뉴에서 IAM 및 관리자 -> 서비스 계정으로 이동합니다.
서비스 계정 생성을 클릭합니다.
서비스 계정 이름과 ID를 설정한 후, 완료합니다.
키 생성:

방금 생성한 서비스 계정을 클릭한 후, 키 추가 -> 새 키 만들기를 선택합니다.
키 유형은 JSON을 선택하고 만들기를 클릭합니다.
JSON 키 파일이 다운로드됩니다.
서비스 계정으로 API 접근:

다운로드된 JSON 파일을 사용해 서비스 계정 인증을 진행할 수 있습니다.
```

