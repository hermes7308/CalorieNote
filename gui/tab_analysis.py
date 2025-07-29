import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from utils.db_handler import select_calorie_sum_by_date
from utils.log_config import get_logger

class AnalysisTab(QWidget):
    """
    칼로리 섭취량을 날짜별로 시각화하는 그래프 탭.
    DB에서 날짜별 칼로리 합계를 조회하여 matplotlib 그래프로 표시.
    """
    def __init__(self, parent=None):
        """
        AnalysisTab 생성자. 그래프 및 UI 초기화, 최초 그래프 표시.
        """
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.figure = plt.Figure(figsize=(4, 3))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.plot_calorie_graph)
        self.logger.info("[분석탭] Refresh 버튼 및 UI 초기화 완료")
        top_layout.addStretch()
        top_layout.addWidget(refresh_btn)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.canvas)
        self.setLayout(main_layout)
        self.plot_calorie_graph()

    def get_calorie_data(self):
        """
        DB에서 날짜별 칼로리 합계 데이터를 조회하여 (날짜 리스트, 칼로리 리스트)로 반환.
        예외 발생 시 빈 리스트 반환.
        """
        self.logger.info("[분석탭] 날짜별 칼로리 데이터 조회 시도")
        try:
            dates_str, calories = select_calorie_sum_by_date()
            self.logger.info(f"[분석탭] DB 조회 성공: {len(dates_str)}건")
            dates = [datetime.datetime.strptime(d, "%Y-%m-%d") for d in dates_str]
            return dates, calories
        except Exception as e:
            self.logger.error(f"[분석탭] DB read error: {e}")
            return [], []

    def plot_calorie_graph(self):
        """
        칼로리 데이터를 그래프로 시각화. 데이터가 없으면 안내 메시지 표시.
        """
        self.logger.info("[분석탭] 그래프 새로고침 시도")
        self.ax.clear()
        dates, calories = self.get_calorie_data()
        if not dates:
            self.logger.warning("[분석탭] 시각화할 데이터가 없습니다.")
            self.ax.set_title("Calorie Intake", fontsize=16, weight="bold")
            self.ax.set_ylabel("Calorie Total")
            self.ax.set_xlabel("Date")
            self.ax.text(0.5, 0.5, "No data", ha="center", va="center", fontsize=12)
        else:
            self.logger.info("[분석탭] 그래프 데이터 시각화 진행")
            self.ax.plot_date(dates, calories, color="blue", linestyle="solid")
            self.ax.set_title("Calorie Intake", fontsize=16, weight="bold")
            self.ax.set_ylabel("Calorie Total")
            self.ax.set_xlabel("Date")
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            self.figure.autofmt_xdate()
        self.canvas.draw()
        self.logger.info("[분석탭] 그래프 갱신 완료")
