from direct.showbase.ShowBase import ShowBase
from panda3d.core import LPoint3f
from random import randint, random
import pickle
from block import Block

# Функция получения случайного цвета
def getRandomColor():
    return (random()*0.3+0.7,
            random()*0.3+0.7,
            random()*0.3+0.7, 1)


# Класс менеджера карты
class MapManager():
    # Конструктор
    def __init__(self):
        # список с блоками
        self.blocks = list()

    # Метод добавления нового блока цвета color в позицию position
    def addBlock(self, position, color=None):
        # если цвет не задан
        if color is None:
            # генерируем случайный цвет
            color = getRandomColor()

        # создаём блок
        block = Block(position, color)
        # добавляем его в список
        self.blocks.append(block)

    # Метод создания базовой карты - квадрата
    def basicMap(self):
        # удаляем все блоки
        self.clearAll()

        for i in range(-7,8):
            for j in range(-7,8):
                pos = (i, j, -2)
                self.addBlock(pos, (1,1,1,1))

    # Метод генерации новой случайной карты
    def generateRandomMap(self):
        # удаляем все блоки
        self.clearAll()

        # Блоки в нижней части карты
        for i in range(-8,9):
            for j in range(-8,9):
                pos = (i, j, randint(-4,-2))
                self.addBlock(pos)

        # Блоки по краям карты
        for i in range(-8,9):
            for j in range(-8,9):
                if -5 < i < 5 and -5 < j < 5:
                    continue
                pos = (i, j, randint(-1,6))
                self.addBlock(pos)

    # Метод создания карты, аргументы
    # colors - словарь цветов,
    #   ключ - символ цвета,
    #   значение - цвет
    # matrix - трёхмерный вложенный список цветов
    #   значения - символы цвета
    # shift - сдвиг всех координат
    def createMap(self, colors, matrix, shift):
        # удаляем все блоки
        self.clearAll()

        # проходимся по всем трём координатам
        for z in range(len(matrix)):
            for y in range(len(matrix[z])):
                for x in range(len(matrix[z][y])):
                    # Получаем цвет блока
                    key = matrix[z][y][x]
                    # если такой цвет есть в словаре цветов
                    if key in colors and colors[key]:
                        # Рассчитываем позицию
                        # Координата Y инвертируется !!!
                        pos = (x + shift[0],
                               - y - shift[1],
                               z + shift[2])
                        # добавляем новый блок
                        self.addBlock(pos, colors[key])

    # Метод очистки карты - удаления всех блоков
    def clearAll(self):
        # удаляем блоки из Panda3D
        for block in self.blocks:
            block.remove()

        # удаляем блоки из памяти
        self.blocks.clear()

    # Метод сохранения карты в файл
    # filename - имя файла
    def saveMap(self, filename):
        # если нет блоков
        if not self.blocks:
            return

        # откройте бинарный файл filename на запись
        nfile = open(filename, 'wb')

        # сохраните в начало файла количество блоков
        pickle.dump(len(self.blocks), nfile)

        # обойдите в цикле все блоки
        for i in self.blocks:
            # в теле цикла

            # получите из блока его позицию,
            # используя соответствующий метод класса Block
            pos_b = i.getPos()
            # сохраните её в файл
            pickle.dump(pos_b, nfile)
            # повторите это всё для цвета блока
            col_b = i.getColor()
            pickle.dump(col_b, nfile)

        # закройте файл
        nfile.close()

        print("save map to", filename)


    # Метод загрузки карты из файла
    # filename - имя файла
    def loadMap(self, filename):
        # удаляем все блоки
        self.clearAll()

        # откройте бинарный файл filename на чтение
        nfile = open(filename, 'rb')

        # прочитайте из файла количество блоков
        q_blocks = pickle.load(nfile)

        # запустите цикл по количеству блоков
        for i in range(q_blocks):
            # прочитайте позицию блока
            pos_b = pickle.load(nfile)
            # прочитайте цвет блока
            col_b = pickle.load(nfile)

            # по этой информации добавьте новый блок
            # вызвав соответствующий метод класса MapManager
            self.addBlock(pos_b, col_b)

        # закройте файл
        nfile.close()

        print("load map from", filename)


if __name__ == '__main__':
    # отладка модуля
    from direct.showbase.ShowBase import ShowBase
    from controller import Controller

    class MyApp(ShowBase):

        def __init__(self):
            ShowBase.__init__(self)

            self.controller = Controller()

            self.map_manager = MapManager()

            self.accept('f1', self.map_manager.basicMap)
            self.accept('f2', self.map_manager.generateRandomMap)
            self.accept('f3', self.map_manager.saveMap, ["testmap.dat"])
            self.accept('f4', self.map_manager.loadMap, ["testmap.dat"])
            self.accept('f5', self.createMap)

            print("'f1' - создать базовую карту")
            print("'f2' - создать случайную карту")
            print("'f3' - сохранить карту")
            print("'f4' - загрузить карту")
            print("'f5' - создать карту по вложенному списку")

            self.map_manager.generateRandomMap()

        def createMap(self):
            # словарь цветовых обозначений блоков
            colors = {'R':(1.0, 0, 0, 1),
                      'G':(0, 1.0, 0, 0.5),
                      'B':(0, 0, 1.0, 0.5),
                      'Y':(1.0, 1.0, 0, 1),
                      'O':(1.0, 0.5, 0.0, 1),
                      'W':(1.0, 1.0, 1.0, 1),
                      '-':None}

            # вложенный список блоков
            blocks = [
                [['G','O','O','O','G'],
                 ['O','-','-','-','O'],
                 ['O','-','W','-','O'],
                 ['O','-','-','-','O'],
                 ['G','O','O','O','G']],

                [['G','-','-','-','G'],
                 ['-','-','-','-','-'],
                 ['-','-','W','-','-'],
                 ['-','-','-','-','-'],
                 ['G','-','-','-','G']],

                [['G','-','R','-','G'],
                 ['-','-','R','-','-'],
                 ['R','R','W','R','R'],
                 ['-','-','R','-','-'],
                 ['G','-','R','-','G']],

                [['G','-','-','-','G'],
                 ['-','-','-','-','-'],
                 ['-','-','W','-','-'],
                 ['-','-','-','-','-'],
                 ['G','-','-','-','G']],

                [['G','Y','Y','Y','G'],
                 ['Y','-','-','-','Y'],
                 ['Y','-','W','-','Y'],
                 ['Y','-','-','-','Y'],
                 ['G','Y','Y','Y','G']],
                ]

            self.map_manager.createMap(colors, blocks, (-2,-10,-2))


    app = MyApp()
    app.run()
