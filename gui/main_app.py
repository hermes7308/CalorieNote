from PyQt5.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from gui.tab_analysis import AnalysisTab
from gui.tab_history import HistoryTab
from gui.tab_upload import UploadTab
from utils.db_handler import init_db
from utils.log_config import get_logger


class MainWindow(QMainWindow):
    """
    메인 윈도우 클래스. 탭 위젯을 포함하며, 프로그램의 진입점 역할을 함.
    """

    def __init__(self):
        """
        MainWindow 생성자. UI 초기화 및 DB 초기화 수행.
        """
        super().__init__()
        self.logger = get_logger(__name__)
        self.logger.info("칼로리 분석 프로그램 시작")
        self.setWindowTitle("OpenAI 이미지 설명 프로그램")
        self.setGeometry(100, 100, 1000, 700)
        self.init_ui()
        init_db()

    def init_ui(self):
        """
        메인 UI를 초기화하고, 탭 위젯을 생성하여 각 탭(업로드, 분석, 히스토리)을 추가함.
        """
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        self.tabs = QTabWidget()
        self.upload_tab = UploadTab()
        self.analysis_tab = AnalysisTab()
        self.history_tab = HistoryTab()
        self.tabs.addTab(self.upload_tab, "Upload")
        self.tabs.addTab(self.analysis_tab, "Analysis")
        self.tabs.addTab(self.history_tab, "History")
        main_layout.addWidget(self.tabs)
