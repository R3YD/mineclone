from direct.showbase.DirectObject import DirectObject
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import BitMask32
from panda3d.core import LPoint3f
from mapmanager import MapManager


# Класс редактора блоков
class Editor(DirectObject):
    # Конструктор
    def __init__(self, map_manager):
        # сохраняем ссылку на объект менеджера карты
        self.map_manager = map_manager

        # создание обходчика столкновений
        self.traverser = CollisionTraverser()
        # очередь обработки столкновений
        self.collisQueue = CollisionHandlerQueue()
        # узел для луча столкновений
        collisionNode = CollisionNode('CenterRay')
        # установите на узел collisionNode маску проверки столкновений ОТ
        # такую же, как и у блока Block
        collisionNode.setFromCollideMask(BitMask32.bit(1))
        # создаём луч
        self.collisRay = CollisionRay()
        # и прикрепляем к созданному ранее узлу
        collisionNode.addSolid(self.collisRay)
        # закрепляем узел на камере
        collisCamNode = base.camera.attachNewNode(collisionNode)
        # уведомляем обходчик о новом «объекте ОТ»
        self.traverser.addCollider(collisCamNode, self.collisQueue)
        # визуализируем столкновения (раскомментировать/закоментировать)
        #self.traverser.showCollisions(base.render)
        # позиция для добавления нового блока
        self.new_position = None
        # ключ выделенного блока
        self.selected_key = None
        # узел выделенного блока
        self.selected_node = None

        # запускаем задачу проверки выделения блоков
        taskMgr.doMethodLater(0.02, self.testBlocksSelection,
                              "test_block-task")

        # регистрируем на нажатие левой кнопки мыши
        # событие добавления блока
        self.accept('mouse1', self.addBlock)
        # регистрируем на нажатие правой кнопки мыши
        # событие удаления блока
        self.accept('mouse3', self.delBlock)

    # Метод сброса свойств выделенного блока
    def resetSelectedBlock(self):
        self.new_position = None
        self.selected_key = None
        self.selected_node = None

    # Метод добавления блока
    def addBlock(self):
        # если есть позиция для нового блока
        if self.new_position:
            # добавьте новый блок в эту позицию
            # вызвав соответствующий метод у менеджера карты self.map_manager
            self.map_manager.addBlock(self.new_position)
            # сбрасываем выделение
            self.resetSelectedBlock()

    # Метод удаления блока
    def delBlock(self):
        # удалите выделенный блок
        # вызвав соответствующий метод у менеджера карты self.map_manager
        self.map_manager.deleteSelectedBlock()
        # сбрасываем выделение
        self.resetSelectedBlock()

    # Метод проверки проверки выделения блоков
    def testBlocksSelection(self, task):
        # устанавливаем позицию луча столкновений в центр экрана
        self.collisRay.setFromLens(base.camNode, 0, 0)
        # запускаем обходчик на проверку
        self.traverser.traverse(base.render)

        # если обходчик обнаружил какие-то столкновения
        if self.collisQueue.getNumEntries() > 0:
            # сортируем их, чтобы получить ближайшее
            self.collisQueue.sortEntries()
            # получаем описание ближайшего столкновения
            collisionEntry = self.collisQueue.getEntry(0)
            # получаем узел с «объектом ДО»
            intoNode = collisionEntry.getIntoNodePath()
            # получите из узла intoNode по тому же тегу 'key', что и в Block
            # ключ выделенного блока и занесите в переменную key
            key = intoNode.getTag('key')
        

            # если найден новый блок
            if key != self.selected_key:
                # обновляем ключ выделенного блока
                self.selected_key = key
                # выделите новый блок
                # и сохраните узел этого блока в свойстве self.selected_node
                # соответствующий метод у менеджера карты
                # возвращает узел выделенного блока
                self.selected_node = self.map_manager.selectBlock(key)


            # если есть выделенный блок
            if self.selected_node:
                # координаты выделенного блока
                selected_position = self.selected_node.getPos()
                # вектор нормали к поверхности на выделенном блоке
                normal = collisionEntry.getSurfaceNormal(self.selected_node)
                # позиция для добавления нового блока
                self.new_position = selected_position + normal
        else:
            # снимите выделение со всех блоков
            # вызвав соответствующий метод у менеджера карты
            self.map_manager.deselectAllBlocks()
            # сбрасываем выделение
            self.resetSelectedBlock()

        # сообщаем о необходимости повторного запуска задачи
        return task.again
