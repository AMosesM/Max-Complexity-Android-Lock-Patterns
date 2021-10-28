from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import QRectF, QRect, QPointF, QEvent, QTimer, QLine, QPoint, QSize, QPropertyAnimation, QObject, Signal
import math

class Surface(QWidget):
    finishedAnim = Signal()
    def __init__(self, parent):
        super().__init__(parent)

        self.vlay = QVBoxLayout()
        self.vlay.setSpacing(0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setLayout(self.vlay)

        self.bg = QBrush(QColor(35, 35, 35))
        self.bg.setStyle(Qt.SolidPattern)

        self.points = []
        for p in range(9):
            point = QPointF(0.0, 0.0)
            self.points.append(point)

        self.path = ""
        self.pathQueue = ""

        self.animPoint = QPointF(0.0, 0.0)
        self.animLineTarget = [QPointF(0.0, 0.0), QPointF(0.0, 0.0)]
        self.animSlope = 0.0
        self.animAngle = 0.0
        self.animP1 = 0
        self.animP2 = 0
        self.animDone = True
        self.animTimer = QTimer()
        self.animTimer.timeout.connect(self.repaint)
        self.calculatedPoints = False
        self.animStep = 0.0

    def getXYs(self, p1, p2):
        x1 = self.points[p1].x()
        y1 = self.points[p1].y()
        x2 = self.points[p2].x()
        y2 = self.points[p2].y()
        return (x1,y1,x2,y2)

    def calculateDistance(self, xs, ys):
        animDist = math.sqrt((xs*xs) + (ys*ys))
        return animDist

    def calculateAnimVars(self):
        if self.animDone:
            return
        self.animP1 = int(self.pathQueue[0]) - 1
        self.animP2 = int(self.pathQueue[1]) - 1

        p1 = self.animP1
        p2 = self.animP2

        x1,y1,x2,y2 = self.getXYs(p1, p2)

        self.animLineTarget[0].setX(x1)
        self.animLineTarget[0].setY(y1)
        self.animLineTarget[1].setX(x2)
        self.animLineTarget[1].setY(y2)

    def setPath(self, path):
        self.path = path[0]
        self.pathQueue = path
        
        self.animDone = False
        self.calculateAnimVars()
        self.animTimer.start(15)

    def processQueue(self):
        if self.pathQueue != "":
            self.animStep = 0.0
            self.path += self.pathQueue[:2]
            self.pathQueue = self.pathQueue[1:]
            if len(self.pathQueue) == 1:
                self.pathQueue = ""
                self.animDone = True
                self.finishedAnim.emit()
            self.calculateAnimVars()
            self.animTimer.start(15)

    def paintEvent(self, event):
        if not self.calculatedPoints:
            self.calculatedPoints = True
            self.calculatePoints()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        bg_path = QPainterPath()
        bg_path.addRect(self.rect())

        painter.setBrush(self.bg)
        bg = 65
        painter.fillPath(bg_path, QBrush(QColor(bg,bg,bg)))

        covered_points = [self.points[int(i)-1] for i in self.path]

        fg = 200
        painter.setPen(QPen(QBrush(QColor(fg,fg,fg)), self.grid_half_size*0.30))
        painter.drawPoints(self.points)
        painter.setPen(QPen(QBrush(QColor(0,fg,0)), self.grid_half_size*0.40))
        painter.drawPoints(covered_points)

        painter.setPen(QPen(QBrush(QColor(fg,fg,fg)), self.grid_half_size*.10, Qt.SolidLine, Qt.RoundCap))
        for i in range(len(self.path) - 1):
            p = [self.points[int(a)-1] for a in str(self.path[i:i+2])]
            painter.drawLine(p[0], p[1])

        if not self.animDone:
            if self.animStep < 1.0:
                self.animPoint = self.animLineTarget[1] - self.animLineTarget[0]
                self.animPoint = self.animLineTarget[0] + self.animStep*self.animPoint
                painter.drawLine(self.animLineTarget[0], self.animPoint)
                self.animStep += 0.05
            else:
                self.animTimer.stop()
                painter.drawLine(self.animLineTarget[0], self.animLineTarget[1])
                self.processQueue()

    def calculatePoints(self):
        self.max_side_len = min([self.width(), self.height()])
        self.grid_margin = self.max_side_len * 0.20
        
        self.grid_half_size = (self.max_side_len - 2.0*self.grid_margin) / 2.0

        center = self.rect().center()

        self.points[0].setX(center.x()-self.grid_half_size)
        self.points[0].setY(center.y()-self.grid_half_size)

        self.points[1].setX(center.x())
        self.points[1].setY(center.y()-self.grid_half_size)

        self.points[2].setX(center.x()+self.grid_half_size)
        self.points[2].setY(center.y()-self.grid_half_size)

        self.points[3].setX(center.x()-self.grid_half_size)
        self.points[3].setY(center.y())

        self.points[4].setX(center.x())
        self.points[4].setY(center.y())

        self.points[5].setX(center.x()+self.grid_half_size)
        self.points[5].setY(center.y())

        self.points[6].setX(center.x()-self.grid_half_size)
        self.points[6].setY(center.y()+self.grid_half_size)

        self.points[7].setX(center.x())
        self.points[7].setY(center.y()+self.grid_half_size)

        self.points[8].setX(center.x()+self.grid_half_size)
        self.points[8].setY(center.y()+self.grid_half_size)

    def resizeEvent(self, event):
        self.animTimer.stop()
        super().resizeEvent(event)
        self.calculatePoints()
        self.calculateAnimVars()
        self.animTimer.start()
