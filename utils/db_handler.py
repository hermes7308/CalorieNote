import sqlite3
from typing import Any, List, Tuple

from utils.config import DB_PATH
from utils.log_config import get_logger
logger = get_logger(__name__)


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """DB 연결 객체 반환"""
    try:
        conn = sqlite3.connect(db_path)
        logger.info(f"DB 연결 성공: {db_path}")
        return conn
    except Exception as e:
        logger.error(f"DB 연결 실패: {db_path}, 에러: {e}")
        raise


# 1. DB 초기화 함수
def init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gpt_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image BLOB,
                prompt TEXT,
                response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                food_name TEXT,
                calories INTEGER,
                date DATE,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        logger.info("DB 초기화 완료 (gpt_requests, calories 테이블 생성)")
    except Exception as e:
        logger.error(f"DB 초기화 실패: {e}")
        raise
    finally:
        conn.close()


# 2. gpt_requests 관련 함수
def insert_gpt_request(image_blob: bytes, prompt: str, response: str) -> None:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO gpt_requests (image, prompt, response) VALUES (?, ?, ?)",
            (image_blob, prompt, response),
        )
        conn.commit()
        logger.info(f"gpt_requests 삽입 성공 | prompt: {prompt[:30]}... | response: {response[:30]}...")
    except Exception as e:
        logger.error(f"gpt_requests 삽입 실패: {e}")
        raise
    finally:
        conn.close()


def select_gpt_requests() -> List[Tuple[Any, ...]]:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, prompt, response, timestamp FROM gpt_requests ORDER BY id DESC"
        )
        rows = cursor.fetchall()
        logger.info(f"gpt_requests 조회 성공 | {len(rows)}건")
        return rows
    except Exception as e:
        logger.error(f"gpt_requests 조회 실패: {e}")
        raise
    finally:
        conn.close()


# 3. calories 관련 함수
def insert_calorie(food_name: str, calories: int, date: str) -> None:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO calories (food_name, calories, date) VALUES (?, ?, ?)",
            (food_name, calories, date),
        )
        conn.commit()
        logger.info(f"calories 삽입 성공 | food_name: {food_name}, calories: {calories}, date: {date}")
    except Exception as e:
        logger.error(f"calories 삽입 실패: {e}")
        raise
    finally:
        conn.close()


def select_calories() -> List[Tuple[Any, ...]]:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, food_name, calories, date, timestamp FROM calories ORDER BY id DESC"
        )
        rows = cursor.fetchall()
        logger.info(f"calories 조회 성공 | {len(rows)}건")
        return rows
    except Exception as e:
        logger.error(f"calories 조회 실패: {e}")
        raise
    finally:
        conn.close()


def delete_calorie_by_id(calorie_id: int) -> None:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM calories WHERE id=?",
            (calorie_id,)
        )
        conn.commit()
        logger.info(f"calories 삭제 성공 | id: {calorie_id}")
    except Exception as e:
        logger.error(f"calories 삭제 실패 | id: {calorie_id}, 에러: {e}")
        raise
    finally:
        conn.close()


def select_calorie_sum_by_date() -> Tuple[List[str], List[int]]:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT date, SUM(calories) FROM calories GROUP BY date ORDER BY date;"
        )
        rows = cursor.fetchall()
        dates = [row[0] for row in rows]
        calories = [row[1] for row in rows]
        logger.info(f"calories 일자별 합계 조회 성공 | {len(dates)}일")
        return dates, calories
    except Exception as e:
        logger.error(f"calories 일자별 합계 조회 실패: {e}")
        raise
    finally:
        conn.close()
