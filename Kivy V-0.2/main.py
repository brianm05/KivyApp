from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty,ListProperty,StringProperty
)
from kivy.vector import Vector
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.config import Config

import random
import json
import os

vivo=False
enemyPos=50
colorPista=0

flag=0

calle=      [[.2,.2,.2,1],      [.5,.5,.5,1],   [.2,.2,.2,1]]
arcoiris=   [[1,0,0,1],         [0,1,0,1],      [0,0,1,1]]
argentina=  [[.4,.6,.9,1],      [1,1,1,1],      [.4,.6,.9,1]]
brasil=     [[0,.5,.2,1],       [.9,.8,0,1],    [0,.1,.4,1]]
river=      [[1,1,1,1],         [.8,0,0,1],     [1,1,1,1]]
bocaca=     [[0,0,.4,1],        [.9,.9,0,1],    [0,0,.4,1]]
chaca=      [[.1,.1,.1,1],      [.8,0,0,1],     [1,1,1,1]]

pistas=[calle,arcoiris,argentina,brasil,river,bocaca,chaca]


def cargarMejorPuntaje(filename="score.json"):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file).get("best_score", 0)
    return 0

def guardarMejorPuntaje(score, filename="score.json"):
    with open(filename, 'w') as file:
        json.dump({"best_score": score}, file)


class Player(Widget):
    score = NumericProperty(0)
    mejor_score = NumericProperty(cargarMejorPuntaje())
    color = ListProperty([1, 1, 1, 1])
    imagen = StringProperty('assets/car1.png')

class Enemy(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    color = ListProperty([1, 1, 1, 1])

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

class Game(Widget):

    aumentarNivel=5
    carril=1

    car = ObjectProperty(None)
    player = ObjectProperty(None)

    start_button = ObjectProperty(None)
    quit_button = ObjectProperty(None)
    color_button = ObjectProperty(None)
    pista_button = ObjectProperty(None)
    
    mejor_puntaje = ObjectProperty(None)
    mejor_puntaje_contorno = ObjectProperty(None)


    color1 = ListProperty(pistas[0][0])
    color2 = ListProperty(pistas[0][1])
    color3 = ListProperty(pistas[0][2])

    crashSound=SoundLoader.load('sounds/crash.mp3')
    crashSound.loop=False
    gameLoopSound=SoundLoader.load('sounds/main_loop.mp3')
    gameLoopSound.loop=True

    whoosh1=SoundLoader.load('sounds/whoosh/whoosh.mp3')
    whoosh2=SoundLoader.load('sounds/whoosh/whoosh2.mp3')
    whoosh3=SoundLoader.load('sounds/whoosh/whoosh3.mp3')

    def cambiarPista(self):
        global colorPista
        colorPista+=1
        if colorPista>=len(pistas):
            colorPista=0

        self.color1=pistas[colorPista][0]
        self.color2=pistas[colorPista][1]
        self.color3=pistas[colorPista][2]

        self.pista_button.text=f"Cambiar pista ({colorPista+1}/{len(pistas)})"

    def reubicarEnemigo(self):
        self.car.y = self.height-self.car.height #reubicar el enemigo en el eje y

        posiciones=(self.width/6-self.car.width/2,
                self.center_x-self.car.width/2,
                self.width/6*5-self.car.width/2)
        eleccion=random.choice(posiciones)
        self.car.x=eleccion #obtener una de las tres posiciones posible para el eje en x
        
        #obtener una lista con 3 numeros aleatorios (de 0 a 1) para el color rgb de auto enemigo
        self.car.color = [random.uniform(0,1)] +[random.uniform(0,1)] +[random.uniform(0,1)] + [1]

    def actualizarScore(self):
        self.player.score += 1 #aumentar el score actual
        #actualizar en best score (en caso de ser necesario)
        if self.player.score>self.player.mejor_score:
            self.player.mejor_score=self.player.score

        #Esto determina la curva de dificultad. Al momento del comentario:
        #Cada 5 puntos conseguidos, el auto enemigo aumenta su velocidad en 2.
        #(esta en negativo porque el enemigo se mueve en direccion contraria)     
        if self.player.score == self.aumentarNivel:
            self.car.velocity_y -= 2
            self.aumentarNivel+=5

    def serve_car(self, vel=(0, -4)):
        self.car.center = self.center
        self.car.velocity = vel
        self.car.velocity_y = -4
        self.reubicarEnemigo()
        global vivo
        vivo=True


    def cambiarAuto(self):
        self.player.color = [random.uniform(0,1)] +[random.uniform(0,1)] +[random.uniform(0,1)] + [1]
        self.player.imagen=random.choice(["assets/car1.png","assets/car.png"])

    def mostrar_menu(self):
        self.start_button.pos = (self.width / 2 - self.start_button.width/2, self.height/2+self.start_button.height)
        self.color_button.pos = (self.width / 2 - self.color_button.width/2, self.height/2)
        self.pista_button.pos = (self.width / 2 - self.pista_button.width/2, self.height/2-self.pista_button.height)
        self.quit_button.pos = (self.width / 2 - self.quit_button.width/2, self.height/2-self.quit_button.height*2)

        #self.mejor_puntaje.pos = (self.width/2-self.mejor_puntaje.width/3, (self.height/2)+self.mejor_puntaje.height)
        self.mejor_puntaje.pos = (self.width/2-self.mejor_puntaje.width/3, self.top-self.mejor_puntaje.height*2)

    def ocultarMenu(self):
        self.start_button.pos = (-500, -500)
        self.quit_button.pos = (-500, -500)
        self.color_button.pos = (-500, -500)
        self.pista_button.pos = (-500, -500)
        self.mejor_puntaje.pos = (-500, -500)

    def iniciar_juego(self):
        global flag
        flag=0                          #Se activa la posibilidad de reproducir el sonido de choque
        self.aumentarNivel=5            #Se establece la varible que controla la dificultad
        self.serve_car()                #El auto enemigo se empieza a mover
        self.gameLoopSound.play()       #Se reproduce la musica del juego
        self.player.score = 0
        self.ocultarMenu()

    def reproducirSonidoChoque(self):
        self.gameLoopSound.stop()
        self.crashSound.play()
        global flag
        flag=1


    def update(self, dt):

        #Llamado a funcion que ejecuta el movimiento del auto enemigo.
        self.car.move()


        #Si la posicion del auto enemigo es tan baja que ya salio de la pantalla:
        if self.car.y < self.y+self.car.height:
            self.reubicarEnemigo()
            self.actualizarScore()

        #Si la posicion en "eje X" del jugador y la posicion en "eje X" del auto enemigo son iguales:
        if (self.car.x == self.player.x):
            if ( 55 < self.car.y <= 235):           #Si el jugador y el auto enemigo colisionan:   
                if flag==0:         #La primera vez que se accede a esta seccion de codigo (flag=0), se reproduce el sonido de choque.
                    self.reproducirSonidoChoque()   #Si no es la primera vez (flag=1), no se reproduce el sonido.
                global vivo
                vivo = False                        #La variable global vivo pasa a Falso.
                guardarMejorPuntaje(self.player.mejor_score)

        if (not vivo):
            self.car.velocity_y = 0                 #Velocidad del auto enemigo = 0.
            self.mostrar_menu()                     #Mostrar menu.
    

    #Movimiento del jugador.
    def on_touch_move(self, touch):
        #Obtenemos la varible global 'vivo' para determinar si el jugador puedo moverse.
        global vivo
        if vivo:
            
            #Si el jugador toca el primer tercio de la pantalla:
            if touch.x < self.width / 3:
                self.player.center_x = self.width/6     #Situamos al jugador en la mitad del primer tercio de la pantalla.
                if self.carril!=0:                      #Si el carril anterior es distinto del carril donde el jugador toco la pantalla,
                    self.whoosh2.play()                 #Hay que ejecutar el sonido de cambio de carril.
                self.carril=0

            #Si el jugador toca el segundo tercio de la pantalla:
            if touch.x > self.width / 3 and touch.x < self.width - self.width / 3:
                self.player.center_x = self.center_x    #Situamos al jugador en la mitad de la pantalla.
                if self.carril!=1:                      #Si el carril anterior es distinto del carril donde el jugador toco la pantalla,
                    self.whoosh1.play()                 #Hay que ejecutar el sonido de cambio de carril.
                self.carril=1

            #Si el jugador toca el tercer tercio de la pantalla:
            if touch.x > self.width - self.width / 3:
                self.player.center_x = self.width/6*5   #Situamos al jugador en la mitad del tercer tercio de la pantalla.
                if self.carril!=2:                      #Si el carril anterior es distinto del carril donde el jugador toco la pantalla,
                    self.whoosh3.play()                 #Hay que ejecutar el sonido de cambio de carril.
                self.carril=2

    #Descargamos los sonidos de la memoria
    def salir(self):
        self.crashSound.unload()
        self.gameLoopSound.unload()
        self.whoosh1.unload()
        self.whoosh2.unload()
        self.whoosh3.unload()
        quit()


class GameApp(App):
    def build(self):
        #Config.set('graphics', 'width', '450')
        #Config.set('graphics', 'height', '800')

        game = Game()

        #A cada objeto, le damos el "id" correspondiente del  archivo kivy (.kv)
        game.start_button = game.ids.start_button       
        game.quit_button = game.ids.quit_button
        game.color_button = game.ids.color_button
        game.pista_button = game.ids.pistaColor_button

        game.mejor_puntaje = game.ids.puntaje_label
        
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game
    
if __name__ == '__main__':
    GameApp().run()
