import datetime
import json

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QDateEdit,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from api.openai_api import get_image_description
from gui.clickable_label import ClickableLabel
from utils.db_handler import insert_calorie, insert_gpt_request, select_calories
from utils.file_handler import get_image_file
from utils.log_config import get_logger


class UploadTab(QWidget):
    """
    이미지 업로드, GPT 분석, 칼로리 정보 입력/저장 기능을 제공하는 탭 위젯.
    """

    def __init__(self, parent=None):
        """
        UploadTab 생성자. UI 초기화 및 기존 칼로리 데이터 로드.
        """
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.image_path = None
        self.calorie_entries = []
        self.init_ui()
        self.logger.info("[업로드탭] UI 초기화 완료")
        self.load_calories()

    def init_ui(self):
        """
        UI 구성 요소를 초기화하고 배치함. 좌측: 이미지, 분석, 결과/입력, 저장. 우측: 칼로리 테이블.
        """
        layout = QHBoxLayout()
        self.setLayout(layout)
        # 좌측 패널
        left_panel = QVBoxLayout()
        layout.addLayout(left_panel, 1)
        self.image_label = ClickableLabel()
        self.image_label.clicked.connect(self.load_image)

        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.image_label.setFixedSize(250, 150)
        self.image_label.setStyleSheet("border: 1px solid #ccc; background: #fafafa;")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setPixmap(
            QPixmap("gui/image_placeholder.png").scaled(80, 80, Qt.KeepAspectRatio)
        )
        self.image_label.setText("(＋) 이미지를 불러와 주세요.")
        left_panel.addWidget(self.image_label)
        self.analysis_btn = QPushButton("GPT 분석")
        self.analysis_btn.clicked.connect(self.generate_description)
        left_panel.addWidget(self.analysis_btn)
        result_groupbox = QGroupBox("결과")
        result_layout = QVBoxLayout()
        result_groupbox.setLayout(result_layout)
        left_panel.addWidget(result_groupbox)
        date_layout = QHBoxLayout()
        date_label = QLabel("Date:")
        date_layout.addWidget(date_label)
        self.date_edit = QDateEdit()
        self.date_edit.setDate(datetime.date.today())
        self.date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.date_edit, 1)
        result_layout.addLayout(date_layout)
        cal_label = QLabel("Calories:")
        result_layout.addWidget(cal_label)
        self.calorie_entries_layout = QVBoxLayout()
        result_layout.addLayout(self.calorie_entries_layout)
        self.add_calorie_btn = QPushButton("음식 추가")
        self.add_calorie_btn.clicked.connect(lambda: self.add_calorie_entry())
        result_layout.addWidget(self.add_calorie_btn)
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_calorie_entries)
        left_panel.addWidget(self.save_btn)
        result_layout.addStretch()
        # 우측 패널
        right_panel = QVBoxLayout()
        layout.addLayout(right_panel, 2)
        # Refresh 버튼을 우측 상단에 추가
        refresh_layout = QHBoxLayout()
        refresh_layout.addStretch()  # 우측 정렬
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_calories)
        refresh_layout.addWidget(refresh_btn)
        right_panel.addLayout(refresh_layout)
        self.calories_table = QTableWidget()
        self.calories_table.setColumnCount(5)
        self.calories_table.setHorizontalHeaderLabels(
            ["ID", "FOOD NAME", "CALORIES", "DATE", ""]
        )
        self.calories_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.Stretch
        )
        self.calories_table.verticalHeader().setVisible(False)
        self.calories_table.setEditTriggers(QTableWidget.NoEditTriggers)
        right_panel.addWidget(self.calories_table)

    def load_image(self):
        """
        이미지 파일을 선택하여 라벨에 표시. 실패 시 경고 메시지 출력.
        """
        self.logger.info("[업로드탭] 이미지 불러오기 시도")
        try:
            path = get_image_file()
            if path:
                pixmap = QPixmap(path).scaled(
                    self.image_label.width(),
                    self.image_label.height(),
                    Qt.KeepAspectRatio,
                )
                if pixmap.isNull():
                    raise ValueError("이미지를 불러올 수 없습니다.")
                self.image_label.setPixmap(pixmap)
                self.image_path = path
                self.logger.info(f"[업로드탭] 이미지 불러오기 성공: {path}")
            else:
                self.logger.warning("[업로드탭] 이미지 경로 없음")
        except Exception as e:
            self.logger.error(f"[업로드탭] 이미지 불러오기 실패: {e}")
            QMessageBox.warning(self, "오류", f"이미지 불러오기 실패: {e}")

    def generate_description(self):
        """
        선택한 이미지를 GPT API로 분석하여 음식명/칼로리 정보를 추출, 결과를 입력 폼에 자동 추가.
        """
        if not self.image_path:
            self.logger.error("이미지를 먼저 불러와 주세요.")
            QMessageBox.warning(self, "오류", "이미지를 먼저 불러와 주세요.")
            return
        prompt = (
            "너는 음식 분석 전문가입니다.\n"
            "이미지를 보고 음식의 이름과 칼로리를 분석해줘.\n"
            "- 결과는 JSON 형식의 문자열로만 반환해줘.\n"
            "- 여러 음식이 한 사진에 있을 경우, 각 음식의 이름과 칼로리를 분석해줘.\n"
            "- [주의사항] 예시:\n"
            "{\n"
            '\t"output": [\n'
            "\t\t{\n"
            '\t\t\t"food_name": "치킨",\n'
            '\t\t\t"calories": "100"\n'
            "\t\t},\n"
            "\t\t{\n"
            '\t\t\t"food_name": "피자",\n'
            '\t\t\t"calories": "200"\n'
            "\t\t}\n"
            "\t]\n"
            "}\n"
            "- 만약, 음식 사진이 아닌경우, 결과는 빈 배열로 반환해줘.\n"
            "- [주의사항] 예시:\n"
            "{\n"
            '\t"output": []\n'
            "}"
        )
        try:
            self.logger.info(f"[업로드탭] GPT 분석 요청 시작: {self.image_path}")
            result = get_image_description(self.image_path, prompt)
            if result is not None:
                result = result.replace("```json", "").replace("```", "").strip()
            self.logger.info(f"[업로드탭] GPT API 응답: {result}")
            with open(self.image_path, "rb") as f:
                image_blob = f.read()
            insert_gpt_request(image_blob, prompt, result)
            if result is None:
                self.logger.warning("[업로드탭] 음식 분석 결과 없음")
                QMessageBox.warning(self, "경고", "음식 분석 결과가 없습니다.")
                return
            json_result = json.loads(result)
            if hasattr(self, "calorie_entries_layout"):
                while self.calorie_entries_layout.count():
                    item = self.calorie_entries_layout.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
            foods = json_result["output"]
            self.logger.info(f"[업로드탭] 분석된 음식 개수: {len(foods)}")
            for food in foods:
                self.logger.info(f"[업로드탭] 음식명: {food['food_name']}, 칼로리: {food['calories']}")
                self.add_calorie_entry(food["food_name"], food["calories"])
        except json.JSONDecodeError as e:
            self.logger.error(f"[업로드탭] JSON 파싱 오류 발생: {e}")
            QMessageBox.warning(self, "오류", f"JSON 파싱 오류 발생: {e}")
        except Exception as e:
            self.logger.error(f"[업로드탭] 응답 오류 발생: {e}")
            QMessageBox.warning(self, "오류", f"응답 오류 발생: {e}")

    def load_calories(self):
        """
        DB에서 칼로리 정보를 불러와 테이블에 표시.
        """
        self.logger.info("[업로드탭] 칼로리 테이블 로드 시도")
        try:
            rows = select_calories()
            rows = [list(row[:-1]) for row in rows]
            self.logger.info(f"[업로드탭] 칼로리 DB 조회 성공: {len(rows)}건")
            self.calories_table.setColumnCount(5)
            self.calories_table.setHorizontalHeaderLabels(
                ["ID", "FOOD NAME", "CALORIES", "DATE", ""]
            )
            self.calories_table.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    self.calories_table.setItem(row_idx, col_idx, item)
                # 삭제 버튼 추가 (late binding 문제 해결)
                delete_btn = QPushButton("삭제")
                calorie_id = row[0]  # ID는 첫 번째 컬럼
                delete_btn.clicked.connect(
                    lambda checked, cid=calorie_id: self.delete_calorie(cid)
                )
                self.calories_table.setCellWidget(row_idx, len(row), delete_btn)
        except Exception as e:
            self.logger.error(f"[업로드탭] DB 데이터 불러오기 실패: {e}")
            QMessageBox.warning(self, "DB 오류", f"DB 데이터 불러오기 실패: {e}")

    def delete_calorie(self, calorie_id):
        """
        주어진 ID의 칼로리 레코드를 DB에서 삭제하고 테이블을 갱신.
        """
        from utils.db_handler import delete_calorie_by_id

        self.logger.info(f"[업로드탭] 칼로리 삭제 시도: id={calorie_id}")
        try:
            delete_calorie_by_id(calorie_id)
            self.logger.info(f"[업로드탭] 칼로리 삭제 성공: id={calorie_id}")
            self.load_calories()
            QMessageBox.information(self, "삭제 완료", "칼로리 정보가 삭제되었습니다.")
        except Exception as e:
            self.logger.error(f"[업로드탭] 칼로리 삭제 실패: {e}")
            QMessageBox.warning(self, "DB 오류", f"칼로리 삭제 실패: {e}")

    def add_calorie_entry(self, food_text="", kcal_text=""):
        """
        음식명/칼로리 입력 행을 동적으로 추가. food_text, kcal_text로 초기값 지정 가능.
        """
        self.logger.info(f"[업로드탭] 음식 입력 행 추가: food={food_text}, kcal={kcal_text}")
        row_widget = QWidget()
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        food_edit = QLineEdit()
        food_edit.setPlaceholderText("음식 이름")
        food_edit.setText(food_text)
        kcal_edit = QLineEdit()
        kcal_edit.setPlaceholderText("칼로리(kcal)")
        kcal_edit.setText(kcal_text)
        kcal_edit.setFixedWidth(60)
        remove_btn = QPushButton("삭제")

        def remove():
            self.remove_calorie_entry(row_widget)

        remove_btn.clicked.connect(remove)
        row_layout.addWidget(food_edit)
        row_layout.addWidget(kcal_edit)
        row_layout.addWidget(remove_btn)
        row_widget.setLayout(row_layout)
        self.calorie_entries_layout.addWidget(row_widget)
        self.calorie_entries.append((food_edit, kcal_edit, row_widget))

    def remove_calorie_entry(self, row_widget):
        """
        음식 입력 행을 삭제.
        """
        for i, (food_edit, kcal_edit, widget) in enumerate(self.calorie_entries):
            if widget == row_widget:
                self.calorie_entries_layout.removeWidget(widget)
                widget.deleteLater()
                del self.calorie_entries[i]
                self.logger.info(f"[업로드탭] 음식 입력 행 삭제: index={i}")
                break

    def save_calorie_entries(self):
        """
        입력된 음식명/칼로리 정보를 DB에 저장. 저장 후 테이블 갱신 및 알림.
        """
        self.logger.info("[업로드탭] 칼로리 저장 시도")
        try:
            date_str = self.date_edit.date().toString("yyyy-MM-dd")
            for food_edit, kcal_edit, _ in list(self.calorie_entries):  # 복사본 사용
                # 위젯이 이미 삭제된 경우 건너뜀
                if food_edit is None or kcal_edit is None:
                    continue
                if not food_edit.isVisible() or not kcal_edit.isVisible():
                    continue
                food_name = food_edit.text().strip()
                calories = kcal_edit.text().strip()
                if not food_name or not calories:
                    self.logger.warning("[업로드탭] 음식명 또는 칼로리 미입력 행 건너뜀")
                    continue
                insert_calorie(food_name, int(calories), date_str)
                self.logger.info(f"[업로드탭] 칼로리 저장: {food_name}, {calories}, {date_str}")
            # 저장 후 입력 폼 및 리스트 초기화
            while self.calorie_entries_layout.count():
                item = self.calorie_entries_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
            self.calorie_entries.clear()
            self.load_calories()
            QMessageBox.information(self, "저장 완료", "칼로리 정보가 저장되었습니다.")
        except Exception as e:
            self.logger.error(f"[업로드탭] 칼로리 저장 실패: {e}")
            QMessageBox.warning(self, "DB 오류", f"칼로리 저장 실패: {e}")
