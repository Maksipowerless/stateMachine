import json


class Machine:

    def __init__(self, string):
        self.current_condition = 's0'  # текущее состояние автомата
        self.string = string   # строка входных сигналов
        data = dict(json.load(open('description.json')))
        self.conditions = dict((key, data[key]["jump"]) for key in data.keys())  # { состояние :{переходы}, ...}

    def start(self):  # начало движения по автомату
        while self.change_condition(self.current_condition):
            pass
        if self.string:
            return False, self.current_condition
        return True, self.current_condition

    def change_condition(self, condition):  # по входящему сигналу изменяет состояние (если сигнала нет - false)
        for key in self.conditions[condition].keys():
            if self.see(key):
                self.current_condition = self.conditions[condition][key]
                return True
        return False

    def see(self, symbol):  # проверяет, совпадают ли текущий символ с заданным. если да - удаляет его из строки.
        if not self.string:
            return False
        current_symbol = self.string[0]
        is_equal = current_symbol == symbol
        if is_equal:
            self.string = self.string[1:]
        return is_equal
