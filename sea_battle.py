from random import randint
import time

""""Игра 'Морской бой', написана как практическая работа
по разделу ООП на платформе SkillFactory. Играют пользователь
и компьютер на поле 6х6, на котором располагаются 3-х, 2*2-х
 и 4*1-палубных кораблей. Пользователь вводит координаты в виде
 2-х цифр. При попадании (ранении) ход сохраняется, при уничтожении
 корабля ход перходит к противнику. Компьютер ходит по случайным
 координатам, но при попадании в многопалубный корабль пытается
 "добить" его на следующих ходах. Выигрывает первый уничтоживший
 все корабли противника. Разработка и тестирование в PyCharm 2022.2.3"""



class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class Board:
    def __init__(self, hid=True, size=6):
        self.size = size
        self.hid = hid

        self.count = 0
        self.field = [["0"] * size for _ in range(size)]
        self.busy = []
        self.ships = []
        self.ship_died = False


    def out(self, dot):#True если вышли за пределы поля
        return not ((0 <= dot.x < self.size) and (0 <= dot.y < self.size))

    def contour(self, ship, verb = False):
        near = [
            (-1, -1), (-1, 0) , (-1, 1),
            (0, -1), (0, 0) , (0 , 1),
            (1, -1), (1, 0) , (1, 1)
        ]
        for dot in ship.dots():
            for dx, dy in near:
                cur = Dot(dot.x + dx, dot.y + dy)
                # если не вылеззли за поле и точка не занята
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for dot in ship.dots():
            if self.out(dot) or dot in self.busy:
                raise BoardWrongShipException()
        for dot in ship.dots():
            self.field[dot.x][dot.y] = "■"
            self.busy.append(dot)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException()

        if dot in self.busy:
            raise BoardUsedException()

        self.busy.append(dot)

        for ship in self.ships:
            if ship.shooten(dot):
                ship.lives -= 1
                self.field[dot.x][dot.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    self.ship_died = True
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[dot.x][dot.y] = "Т"
        print("Мимо!")
        return False


    def begin(self):
        self.busy = []

class Ship:
    def __init__(self, bow, flat, pos):
        self.bow = bow
        self.flat = flat
        self.pos = pos
        self.lives = flat


# Построение корабля
    def dots(self):
        ship_dots = []
        for i in range(self.flat):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.pos == 0:
                cur_x += i

            elif self.pos == 1:
                cur_y += i
            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooten(self, shot):
        return shot in self.dots()

# Для ИИ пытаемся выдать следующую цель после ранения
class Target():
    def __init__(self):
        self.next_target = []
        self.size = 6

#По пораженной точке берем точки вокруг нее
    def next_dot(self, dot):
        near = [(-1, 0), (0, -1), (0, 1),  (1, 0)]
        for dx, dy in near:
            cur = (dot.x + dx, dot.y + dy)
            if ((0 <= cur[0] < self.size) and (0 <= cur[1] < self.size)):
                self.next_target.append(cur)

    def next_random(self):
        d = self.next_target[randint(0, len(self.next_target)-1)]
        return Dot(d[0], d[1])


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
        self.nt = Target()

    def ask(self):
        raise NotImplementedError()



    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                if repeat:
                    self.enemy.ship_died = False
                    self.nt.next_dot(target)
                # если корабль уничтожен обнулим список след.координат
                if self.enemy.ship_died:
                    self.nt.next_target = []
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):

    def ask(self):
        while True:
            if self.nt.next_target:# Если есть координаты в списке после ранения
                dot = self.nt.next_random()# выбираем из него
            else:
                dot = Dot(randint(0,5), randint(0, 5))
            if dot not in self.enemy.busy:
                break
        print("Компьютер думает. .", end = '')
        for _ in range(4):
            time.sleep(1)#имитируем задержку при мозговой деятельности
            print(" . .", end = "")
        print(f" Ход компьютера: {dot.x+1}{dot.y+1}")

        return dot



class User(Player):
    def ask(self):

        while True:
            try:
                cords = int(input("Введите координаты: "))
            except ValueError as e:
                print('Необходимо вводить только цифры')
                continue
            if not (1 <= cords // 10 <= 6 and 1 <= cords % 10 <= 6 and 11 <= cords <= 66):
                raise BoardOutException()
                continue

            x, y = cords // 10, cords % 10
            return Dot(x - 1, y - 1)

#Отображение игрового поля
class View:
    def out_view(self, hid=True):
        self.hid = hid
        out = ""
        temp = self.ai.board.field.copy()
        if self.hid:#скроем корабли компьютера
            for i in range(len(temp)):
                for j in range(6):
                    if temp[i][j] == '■':
                        temp[i][j] ='0'
        out += "         Ваше поле                     Поле противника   \n"
        out += "  | 1 | 2 | 3 | 4 | 5 | 6 |\t\t"   * 2
        for i, row in enumerate(self.us.board.field): # Построчно выводим игровые поля
            out += f"\n{i + 1} | " + " | ".join(row) + " |"
            out += f"\t\t{i + 1} | " + " | ".join(temp[i]) + " |"

        return out

class Game:
    def __init__(self, size=6):
        self.lens = [3, 2, 2, 1, 1, 1, 1]
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = False

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        board = Board(size = self.size)
        attempts = 0
        for len in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), len, randint(0,1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print("-------------------------------------------------------")
        print("|           Добро пожаловать в игру МОРСКОЙ БОЙ!      |")
        print("-------------------------------------------------------")
        print("  Чтобы сделать ход, введите координаты в формате двух ")
        print("      цифр от 1 до 6 без пробела (строка-столбец).\n")

    def loop(self):
        num = 0
        while True:
            print(View.out_view(self))
            if num % 2 == 0:
                print("Ваш ход!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 24)
                print("ПОЗДРАВЛЯЮ! Вы выиграли!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()
