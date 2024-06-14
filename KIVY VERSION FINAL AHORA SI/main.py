from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty,ListProperty,StringProperty
)
from kivy.vector import Vector
from kivy.core.audio import SoundLoader
from kivy.clock import Clock

import random

vivo=False
colorPista=0
flag=0

calle=      [[.2,.2,.2,1],      [.5,.5,.5,1],   [.2,.2,.2,1]]
argentina=  [[.4,.6,.9,1],      [1,1,1,1],      [.4,.6,.9,1]]
brasil=     [[0,.5,.2,1],       [.9,.9,0,1],    [0,.5,.2,1]]
river=      [[1,1,1,1],         [.8,0,0,1],     [1,1,1,1]]
bocaca=     [[0,0,.4,1],        [.9,.9,0,1],    [0,0,.4,1]]
chaca=      [[.1,.1,.1,1],      [.8,0,0,1],     [1,1,1,1]]
primarios=  [[0,0,1,1],         [1,0,0,1],      [1,1,0,1]]
secundarios=[[1,.5,0,1],        [1,0,1,1],      [0,1,0,1]]


pistas=[calle,argentina,brasil,river,bocaca,chaca,primarios,secundarios]


class Player(Widget):
    score = NumericProperty(0)
    color = ListProperty([1, 1, 1, 1])
    imagen = StringProperty('car1.png')

class Enemy(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    color = ListProperty([1, 1, 1, 1])
    imagen = StringProperty('car1.png')

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

class Game(Widget):

    aumentarNivel=1
    carril=1

    car = ObjectProperty(None)
    player = ObjectProperty(None)

    start_button = ObjectProperty(None)
    quit_button = ObjectProperty(None)
    color_button = ObjectProperty(None)
    pista_button = ObjectProperty(None)

    puntajeLabel = ObjectProperty(None)
    
    color1 = ListProperty(pistas[0][0])
    color2 = ListProperty(pistas[0][1])
    color3 = ListProperty(pistas[0][2])

    crashSound=SoundLoader.load('crash.mp3')
    gameLoopSound=SoundLoader.load('main_loop.mp3')
    gameLoopSound.loop=True

    whoosh1=SoundLoader.load('whoosh.mp3')
    whoosh2=SoundLoader.load('whoosh2.mp3')
    whoosh3=SoundLoader.load('whoosh3.mp3')
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

        #obtener modelo del auto enemigo
        self.car.imagen=random.choice(["car1.png","car2.png","car3.png"])

    def actualizarScore(self):
        self.player.score += 1 #aumentar el score actual

        #Esto determina la curva de dificultad. Al momento del comentario:
        #Cada 5 puntos conseguidos, el auto enemigo aumenta su velocidad en 2.
        #(esta en negativo porque el enemigo se mueve en direccion contraria)     
        if self.player.score == self.aumentarNivel:
            self.car.velocity_y -= .5
            self.aumentarNivel+=1

    def serve_car(self, vel=(0, -6)):
        self.car.center = self.center
        self.car.velocity = vel
        self.car.velocity_y = -6
        self.reubicarEnemigo()
        global vivo
        vivo=True


    def cambiarAuto(self):
        self.player.color = [random.uniform(0,1)] +[random.uniform(0,1)] +[random.uniform(0,1)] + [1]
        self.player.imagen=random.choice(["car1.png","car2.png","car3.png"])

    def mostrar_menu(self):
    

        self.start_button.pos = (self.width / 2 - self.start_button.width/2, self.height/2+self.start_button.height)
        self.color_button.pos = (self.width / 2 - self.color_button.width/2, self.height/2)
        self.pista_button.pos = (self.width / 2 - self.pista_button.width/2, self.height/2-self.pista_button.height)
        self.quit_button.pos = (self.width / 2 - self.quit_button.width/2, self.height/2-self.quit_button.height*2)
        
        self.puntajeLabel.pos = (self.width / 2 - self.puntajeLabel.width/2, self.top-self.puntajeLabel.height)

    def ocultarMenu(self):
        self.start_button.pos = (-500, -500)
        self.quit_button.pos = (-500, -500)
        self.color_button.pos = (-500, -500)
        self.pista_button.pos = (-500, -500)

    def iniciar_juego(self):
        global flag
        flag=0
        self.aumentarNivel=1            #Se establece la varible que controla la dificultad
        self.serve_car()                #El auto enemigo se empieza a mover
        self.gameLoopSound.play()
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
        game.color_button = game.ids.color_button
        game.pista_button = game.ids.pistaColor_button
        game.quit_button = game.ids.quit_button
        
        game.puntajeLabel = game.ids.labelPuntaje

        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game
    
if __name__ == '__main__':
    GameApp().run()
