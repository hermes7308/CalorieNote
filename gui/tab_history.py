from PyQt5.QtGui import QCursor, QGuiApplication
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from utils.db_handler import select_gpt_requests
from utils.log_config import get_logger


class HistoryTab(QWidget):
    """
    GPT 요청/응답 이력을 테이블로 보여주는 탭.
    각 요청의 상세 내용은 셀 클릭 또는 마우스 오버로 확인 가능.
    """

    def __init__(self, parent=None):
        """
        HistoryTab 생성자. UI 초기화 및 이력 데이터 로드.
        """
        super().__init__(parent)
        self.logger = get_logger(__name__)
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        # 상단에 Refresh 버튼을 오른쪽 정렬로 배치
        top_layout = QHBoxLayout()
        top_layout.addStretch()  # 왼쪽 공간 확보
        self.refresh_btn = QPushButton("Refresh")
        top_layout.addWidget(self.refresh_btn)
        main_layout.addLayout(top_layout)
        self.refresh_btn.clicked.connect(self.load_gpt_requests)
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(
            ["ID", "Prompt", "Response", "Timestamp"]
        )
        # 컬럼별 width 정책 지정
        self.history_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )  # ID
        self.history_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.Stretch
        )  # Prompt
        self.history_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.Stretch
        )  # Response
        self.history_table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeToContents
        )  # Timestamp
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.history_table)
        self.history_table.cellClicked.connect(
            self.show_cell_content
        )  # 셀 클릭 시 하단에 전체 내용 표시
        self.history_table.cellEntered.connect(
            self.show_tooltip
        )  # 마우스 오버 시 툴팁 표시
        # 하단에 전체 내용 표시용 QTextEdit 추가 (B안)
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        main_layout.addWidget(self.detail_text)
        self.logger.info("[이력탭] UI 초기화 및 이력 데이터 로드 시작")
        self.load_gpt_requests()

    def show_cell_content(self, row, col):
        """
        테이블 셀 클릭 시 해당 셀의 전체 내용을 하단 텍스트박스에 표시하고, 클립보드에 복사.
        """
        item = self.history_table.item(row, col)
        if item:
            self.detail_text.setPlainText(item.text())
            # 클립보드에 복사
            QGuiApplication.clipboard().setText(item.text())
            # 복사 완료 툴팁 표시
            QToolTip.showText(QCursor.pos(), "복사됨", self.history_table)
            self.logger.info(f"[이력탭] 셀 클릭: row={row}, col={col}, 내용 복사 완료")
        else:
            self.logger.warning(f"[이력탭] 셀 클릭: row={row}, col={col}, 내용 없음")

    def show_tooltip(self, row, col):
        """
        테이블 셀에 마우스 오버 시 툴팁으로 전체 내용 표시.
        """
        item = self.history_table.item(row, col)
        if item:
            QToolTip.showText(QCursor.pos(), item.text(), self.history_table)
            self.logger.info(f"[이력탭] 셀 마우스오버: row={row}, col={col}")
        else:
            self.logger.warning(f"[이력탭] 셀 마우스오버: row={row}, col={col}, 내용 없음")

    def load_gpt_requests(self):
        """
        DB에서 GPT 요청/응답 이력 데이터를 불러와 테이블에 표시.
        """
        self.logger.info("[이력탭] 이력 데이터 로드 시도")
        try:
            rows = select_gpt_requests()
            self.logger.info(f"[이력탭] DB 조회 성공: {len(rows)}건")
            self.history_table.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    self.history_table.setItem(row_idx, col_idx, item)
        except Exception as e:
            self.logger.error(f"DB 데이터 불러오기 실패: {e}")
            QMessageBox.warning(self, "DB 오류", f"DB 데이터 불러오기 실패: {e}")
