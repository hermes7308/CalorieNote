from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel

class ClickableLabel(QLabel):
    """
    QLabel을 상속한 커스텀 라벨 위젯.
    마우스 클릭 시 clicked 시그널을 발생시켜, 클릭 이벤트를 외부에서 핸들링할 수 있도록 함.
    """
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        """
        마우스 클릭 이벤트 오버라이드. 클릭 시 clicked 시그널을 발생시킴.
        """
        self.clicked.emit()
        super().mousePressEvent(event) 