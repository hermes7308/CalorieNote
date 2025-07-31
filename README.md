# 칼로리노트

## 📌 주제 및 선정배경

현대인은 건강관리를 위해 섭취 칼로리 기록이 중요합니다.  
음식 사진, 날짜, 칼로리 정보를 쉽고 빠르게 기록·관리할 수 있는 시스템이 필요합니다.

## 🎯 목표

사용자가 음식 사진을 업로드하고, 날짜와 칼로리를 입력하여 저장할 수 있습니다.  
저장된 칼로리 기록을 히스토리(리스트)와 그래프로 시각화 기능도 제공합니다.

## 🧩 사용 기술

- Python, PyQt5
- SQLite3
- OpenAI API
- matplotlib (그래프)
- dotenv (.env 환경변수)

## 🔁 전체 흐름

1. 음식 이미지 업로드
2. GPT 로 칼로리 계산
3. 날짜 입력
4. 저장 버튼 클릭 → DB 저장
5. GPT 히스토리(리스트) 및 칼로리 그래프 출력

## 🔧 시스템 구성도 (Architecture)

```
[ 사용자 ]
   ↓
[ PyQt5 GUI / Web UI ]
   ↓                ↘
[ 이미지 ]        [ 검색 질의 ]
   ↓                  ↓
[ GPT API 호출 ]
   ↓              ↘   ↓
[ 날짜 + 칼로리 ]    [ SQLite DB ]
   ↓
[ SQLite DB ]
   ↓
[ 히스토리/그래프 출력 ]
```

## 📁 디렉토리 구조 (예시)

```
project/
│
├───api
│   └───openai_api.py
│
├───gui
│   │───clickable_label.py
│   │───main_app.py
│   │───spinner.gif
│   │───tab_analysis.py
│   │───tab_history.py
│   └───tab_upload.py
│
├───utils
│   │───config.py
│   │───db_handler.py
│   │───file_handler.py
│   └───log_config.py
│───.env
│───app.db
│───main.py
│───README.md
└───requirements.txt
```

## 📝 사용 방법

1. `.env` 파일에 본인의 OPENAI_API_KEY를 입력하세요.
   ```
   OPENAI_API_KEY={YOUR_OPENAI_API_KEY}
   DB_PATH=app.db
   ```
2. 아래 명령어로 필요한 패키지를 설치하세요.
   ```
   pip install -r requirements.txt
   ```
3. 아래 명령어로 프로그램을 실행하세요.
   ```
   # Python 3.11
   python main.py
   ```

> ⚠️ 참고:
>
> - `.env` 파일이 없으면 OpenAI API를 사용할 수 없습니다.
> - Windows PowerShell/명령 프롬프트에서는 각 명령어를 한 줄씩 개별적으로 실행하세요.

## 📷 예시 시나리오

- 점심 식사 사진을 업로드하고, 날짜와 칼로리를 입력 후 저장
- 지난 일주일간의 칼로리 섭취량을 그래프로 확인

## 🚀 확장 아이디어(선택)

- 일/주/월별 통계 대시보드
- CSV/Excel로 데이터 내보내기
- 달력으로 보여주기
- 탭 이동시 자동 Refresh
- 멀티쓰레드