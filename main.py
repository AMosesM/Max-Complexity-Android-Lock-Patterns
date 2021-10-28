import sys
import random

from PySide2.QtWidgets import *
from PySide2.QtCore import QFile, Qt, QTimer
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QCloseEvent

from surface import Surface


INF = 999999

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Android Lock Pattern Generator")
        self.cw = QWidget(self)
        self.setCentralWidget(self.cw)

        self.resize(400, 300)
        
        self.vlay = QVBoxLayout()
        self.vlay.setContentsMargins(0,0,0,0)

        self.surface = Surface(self.cw)
        self.vlay.addWidget(self.surface, 1)
        
        self.solutionsCount = 0
        
        self.control_layout = QHBoxLayout()
        
        self.solutionsCombo = QComboBox(self.cw)
        self.solutionsCombo.setMinimumWidth(100)
        self.control_layout.addWidget(self.solutionsCombo)
        self.solutionsCombo.currentIndexChanged.connect(self.choose_solution)

        
        self.control_layout.setContentsMargins(10,0,10,10)
        self.stop_anim_btn = QPushButton(self.style().standardIcon(QStyle.SP_MediaStop), "", self)
        self.stop_anim_btn.clicked.connect(self.stop_animation)
        self.control_layout.addWidget(self.stop_anim_btn)
        
        self.start_anim_btn = QPushButton(self.style().standardIcon(QStyle.SP_MediaPlay), "", self)
        self.start_anim_btn.clicked.connect(self.start_animation)
        self.control_layout.addWidget(self.start_anim_btn)
        
        self.auto_anim_btn = QPushButton("Autoplay")
        self.auto_anim_btn.setCheckable(True)
        self.auto_anim_btn.setChecked(True)
        self.control_layout.addWidget(self.auto_anim_btn)
        
        self.control_layout.addStretch()
        self.vlay.addLayout(self.control_layout)

        # self.vlay.addStretch(1)
        self.cw.setLayout(self.vlay)

        self.slopes = {
              0: [12,23,13,45,56,46,78,89,79],
            INF: [14,47,17,25,58,28,36,69,39],
              1: [42,53,75,73,86],
             -1: [15,59,19,26,48],
              2: [72,83],
             -2: [18,29],
            0.5: [43,76],
           -0.5: [16,49]
        }
        self.slope_constraints = {
            13: [2],
            46: [5],
            79: [8],
            17: [4],
            28: [5],
            39: [6],
            19: [5],
            73: [5]
        }

        self.solutions = []

        self.path = ""

        self.surface.finishedAnim.connect(self.auto_play)

        QTimer.singleShot(100, self.find_solutions)

    def auto_play(self):
        if self.auto_anim_btn.isChecked():
            self.random_solution()

    def random_solution(self):
        n = self.solutionsCombo.count()
        i = random.randint(0, n-1)
        if self.solutionsCombo.itemText(i) == self.surface.path:
            i = n-random.randint(1, n-1)
        QTimer.singleShot(100, lambda: self.solutionsCombo.setCurrentIndex(i))

    def stop_animation(self):
        self.surface.animTimer.stop()
        self.surface.path += self.surface.pathQueue
        self.surface.pathQueue = ""
        self.surface.animDone = True
        QTimer.singleShot(0, self.surface.repaint)

    def start_animation(self):
        if self.auto_anim_btn.isChecked():
            self.random_solution()
        self.surface.animTimer.start()

    def choose_solution(self, index):
        path = self.solutionsCombo.itemText(index)
        self.surface.setPath(path)
        # self.surface.setPath("24")
        # QTimer.singleShot(0, self.surface.repaint)

    def is_solution(self, path: str):
        for key, value in self.slopes.items():
            for s in value:
                if str(s) in path:
                    break
                elif str(s)[::-1] in path:
                    break
            else:
                return False
        return True

    def find_solutions(self):
        for key, value in self.slopes.items():
            for s in value:
                self.path = str(s)
                self.find_solution()
                self.path = str(s)[::-1]
                self.find_solution()
        print("number of max complexity patterns: {}".format(self.solutionsCount))

    def get_slope(self, line):
        result = []
        if len(line) > 1:
            # for key, value in self.slopes.items():
            for key, value in self.slopes.items():
                for slope in value:
                    if str(slope) in line[-2:]:
                        result.append(key)
                    elif str(slope)[::-1] in line[-2:]:
                        result.append(key)
        # print("result: " + str(result))
        return result

    def find_solution(self, _slopes = None):
        # print("start - {}".format(self.path))
        dead = ""
        end = ""
        slopes_used = []
        
        if _slopes:
            slopes_used = _slopes
        slopes_used += self.get_slope(self.path)
        constrains = self.slope_constraints.get(int(self.path[-2:]), []) + self.slope_constraints.get(int(self.path[-2::-1]), [])
        
        if constrains:
            for constraint in constrains:
                if str(constraint) not in self.path:
                    return
        
        while not self.is_solution(self.path):
            options = []
            for key, value in self.slopes.items():
                if key in slopes_used:
                    # print("key: {} in {}".format(key, slopes_used))
                    continue
                can_use = []
                not_used = []
                for slope in value:
                    # print("for slope {} in {}".format(slope, value))
                    if slope in self.slope_constraints.keys():
                        constraint_found = True
                        for constraint in self.slope_constraints.get(slope):
                            if str(constraint) not in self.path:
                                constraint_found = False
                                # print("constraint {} not found in {}".format(constraint, self.path))
                        if not constraint_found:
                            continue

                    if str(slope) in self.path:
                        break
                    elif str(slope)[::-1] in self.path:
                        break
                    else:
                        path_set = set(self.path)
                        slope_set = set(str(slope))
                        result_set = path_set.intersection(slope_set)
                        # print("{} & {} = {}".format(path_set, slope_set, result_set))
                        if len(result_set) == 1:
                            for p in result_set:
                                if p == self.path[-1]:
                                    can_use.append(str(slope))
                                    not_used.append(str(slope))
                        elif len(result_set) == 0:
                            not_used.append(str(slope))
                if len(can_use) == 1 and len(not_used) == 1:
                    self.path += can_use[0].replace(self.path[-1], "")
                    slopes_used += self.get_slope(str(can_use[0]))
                    options = []
                    break
                elif len(can_use) > 0:
                    options += can_use
            if len(options) > 0:
                tmp = self.path
                tmp_slopes = slopes_used.copy()
                for opt in options[1:]:
                    self.path = tmp
                    self.path += opt.replace(self.path[-1], "")
                    slopes_used = tmp_slopes.copy()
                    slopes_used += self.get_slope(str(opt))
                    # print("spliting - %s: %s" % (self.path, slopes_used))
                    self.find_solution(slopes_used)
                self.path = tmp + options[0].replace(tmp[-1], "")
                slopes_used = tmp_slopes.copy()
                slopes_used += self.get_slope(str(options[0]))
                end = dead
                dead = self.path
            elif end == self.path:
                break
            elif end != self.path:
                # print("No options! {}".format(options))
                end = dead
                dead = self.path
        if self.is_solution(self.path):
            if self.path not in self.solutions:
                self.solutionsCombo.addItem(self.path)
                self.solutionsCombo.model().sort(0, Qt.AscendingOrder)
                self.solutions += [self.path]
            self.solutionsCount += 1
            # print("{}".format(self.path))
        else:
            # print("failed - {}".format(self.path))
            pass
        


app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec_()