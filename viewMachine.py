import sys
import math
import json
from PyQt5.QtCore import QPoint, Qt
import Machine
from PyQt5.QtGui import QColor, QFont, QPolygonF, QBrush, QPen
from PyQt5.QtWidgets import QApplication, QWidget, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem,\
     QGraphicsTextItem, QLineEdit


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.line_edit = QLineEdit()
        data = dict(json.load(open('description.json')))
        self.conditions = dict((key, data[key]) for key in data.keys())  # { состояние :{{переходы}, {координаты},
        for key in self.conditions.keys():  # флаг(конечное состояние), объекты на сцене, текст сигналов},...}
            self.conditions[key]["scene_items"] = []
            self.conditions[key]["text"] = {}
        self.signals = {}  # входные сигналы
        self.setGeometry(0, 0, 1000, 650)
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 1000, 570)
        self.view = QGraphicsView(self.scene, self)
        self.view.show()
        self.configure_scene()

    def configure_scene(self):
        self.add_jump()
        self.add_conditions()
        self.add_signals()
        self.line_edit.setGeometry(50, 500, 800, 50)
        self.line_edit.textChanged.connect(self.slot)
        self.scene.addWidget(self.line_edit)

    def slot(self):  # слот при изменения
        machine = Machine.Machine(self.line_edit.text())
        current_condition = machine.start()
        machine = Machine.Machine(self.line_edit.text()[:-1])
        prev_condition = machine.start()
        for key in self.conditions.keys():
            self.change_color_of_circle(key, QColor(192, 192, 192))
            for k in self.conditions[key]["text"]:
                self.conditions[key]["text"][k].setDefaultTextColor(QColor(0, 0, 0))
        if current_condition[0]:
            self.change_color_of_circle(current_condition[1], QColor(50, 205, 50))
            if current_condition[1] in self.conditions[prev_condition[1]]["text"].keys():
                self.conditions[prev_condition[1]]["text"][current_condition[1]].setDefaultTextColor(QColor(50, 205, 50))
        else:
            self.change_color_of_circle(current_condition[1], QColor(255, 50, 50))

    def change_color_of_circle(self, cond, color):
        for item in self.conditions[cond]["scene_items"]:
            item.setBrush(color)

    def add_conditions(self):  # добавляет состояния автомата
        for key in self.conditions.keys():
            x = int(self.conditions[key]["coord"]['x'])
            y = int(self.conditions[key]["coord"]['y'])
            r = int(self.conditions[key]["coord"]['r'])
            self.paint_circle(x, y, r, key)
        for item in self.conditions['s0']["scene_items"]:  # закрашиваем начальное состояние
            item.setBrush(QColor(50, 205, 50))

    def paint_circle(self, x, y, r, name):  # добавляет круг на сцену
        ell = QGraphicsEllipseItem(x - r // 2, y - r // 2, r, r)  # поправка смещения(в qt x,y - правый левый угол)
        ell.setBrush(QColor(192, 192, 192))
        self.scene.addItem(ell)
        self.conditions[name]["scene_items"].append(ell)
        if self.conditions[name]["is_final"] == 'yes':
            ell = QGraphicsEllipseItem(x - r // 2 + r//10, y - r // 2 + r//10, r - r//5, r - r//5)
            ell.setBrush(QColor(192, 192, 192))
            self.scene.addItem(ell)
            self.conditions[name]["scene_items"].append(ell)
        text_item = QGraphicsTextItem(name)
        text_item.moveBy(x - 11, y - 12)
        self.scene.addItem(text_item)

    def add_jump(self):  # добавляет переходы
        for key in self.conditions.keys():  # цикл по всем состояниям
            exist_jumps = []
            r1 = int(self.conditions[key]["coord"]['r'])
            x1 = int(self.conditions[key]["coord"]['x'])
            y1 = int(self.conditions[key]["coord"]['y'])
            for state in self.conditions[key]["jump"].values():  # цикл по всем переходам из текущего состояния
                r2 = int(self.conditions[state]["coord"]['r'])
                x2 = int(self.conditions[state]["coord"]['x'])
                y2 = int(self.conditions[state]["coord"]['y'])
                if key == state and state not in exist_jumps:
                    self.add_arc(x1, y1, r1)
                    exist_jumps.append(state)
                elif state not in exist_jumps:
                    self.add_arrow(x1, y1, x2, y2, r2)
                    exist_jumps.append(state)
            if self.conditions[key]["is_final"] == 'start':  # начальное состояние
                self.add_arrow(x1, y1 - 1.5*r1, x1, y1, r1)


    def add_arrow(self, x1, y1, x2, y2, r):  # добавляет стрелки [(x1,y1) ---> (x2,y2)
        polygon = QPolygonF()
        polygon.append(QPoint(x1, y1))
        arrow_length = 30 + r // 2  # длина стрелки
        ostr = 0.1  # острота стрелки
        x = x2 - x1
        y = y2 - y1
        angle = math.atan2(y, x)
        new__x2 = x2 - r / 2 * math.cos(angle)  # координаты с учетом радиуса
        new__y2 = y2 - r / 2 * math.sin(angle)
        polygon.append(QPoint(new__x2, new__y2))
        arrow__x = x2 - arrow_length * math.cos(angle - ostr)
        arrow__y = y2 - arrow_length * math.sin(angle - ostr)
        polygon.append(QPoint(arrow__x, arrow__y))
        arrow__x = x2 - arrow_length * math.cos(angle + ostr)
        arrow__y = y2 - arrow_length * math.sin(angle + ostr)
        polygon.append(QPoint(arrow__x, arrow__y))
        polygon.append(QPoint(new__x2, new__y2))
        self.scene.addPolygon(polygon, QPen(), QBrush(Qt.black))

    def add_triangle(self, x, y, l):
        polygon = QPolygonF()
        polygon.append(QPoint(x, y))
        polygon.append(QPoint(x + l//2, y - l))
        polygon.append(QPoint(x - l//2, y - l))
        polygon.append(QPoint(x, y))
        self.scene.addPolygon(polygon, QPen(), QBrush(Qt.black))

    def add_arc(self, x, y, r):  # x,y - центр окружности, к которой строится дуга
        ell = QGraphicsEllipseItem(x - r // 4, y - r / 1.1, r - r // 2, r + r // 2)
        ell.setStartAngle(0)
        ell.setSpanAngle(2900)
        self.scene.addItem(ell)
        self.add_triangle(x - r // 4.4, y - r//2.28, r//4)

    def add_signals(self):  # добавление сигналов для перехода в другое состояние
        for cond in self.conditions.keys():
            text = {}
            for key in self.conditions[cond]["jump"].keys():
                if self.conditions[cond]["jump"][key] not in text.keys():  # если нет ключа - добавляем запись
                    text[self.conditions[cond]["jump"][key]] = key + ','
                else:  # если ключ есть - перезаписываем строку
                    text[self.conditions[cond]["jump"][key]] += key + ','
            for k in text.keys():
                if k == cond:  # переход в это же состояние
                    x = int(self.conditions[cond]["coord"]["x"])
                    y = int(self.conditions[cond]["coord"]["y"])
                    r = int(self.conditions[cond]["coord"]["r"])
                    self.add_text(cond, k, text[k][:-1], x+r//5, y - r)
                else:
                    x1 = int(self.conditions[cond]["coord"]["x"])
                    y1 = int(self.conditions[cond]["coord"]["y"])
                    x2 = int(self.conditions[k]["coord"]["x"])
                    y2 = int(self.conditions[k]["coord"]["y"])
                    self.add_text(cond, k, text[k][:-1], (x1+x2)//2, (y1+y2)//2 -30)

    # добавляет текст на сцену и в conditions сохраняет объекты этого текста
    def add_text(self, key, cond, text, x, y):  # key - к какому состоянию привязать текст не сцене
        text_item = QGraphicsTextItem(text)  # cond куда произойдет переход
        text_item.moveBy(x, y)
        f = QFont("Times", 15)
        text_item.setFont(f)
        self.scene.addItem(text_item)
        self.conditions[key]["text"][cond] = text_item


if __name__ == '__main__':
    application = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(application.exec_())