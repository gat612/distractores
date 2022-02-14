import pygame, sys, random
import pygame_widgets
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
from pygame_widgets.button import Button as buton
import sqlite3

# import gpiozero as gpioz #///libreria de los pines del Raspberry

class Button():
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        if position[0] in range(self.rect.left - 300, self.rect.right + 300) and position[1] in range(self.rect.top,
                                                                                                      self.rect.bottom):
            return True
        return False

    def checkInput(self, position):
        if position[0] in range(self.rect.left - 20, self.rect.right + 20) and position[1] in range(self.rect.top,
                                                                                                      self.rect.bottom):
            return True
        return False

    def changeColor(self, position):
        if position[0] in range(self.rect.left - 300, self.rect.right + 300) and position[1] in range(self.rect.top,
                                                                                                      self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)

    def changeHoverColor(self, position):
        if position[0] in range(self.rect.left - 20, self.rect.right + 20) and position[1] in range(self.rect.top,
                                                                                                      self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)

class OptionBox():
    def __init__(self, x, y, w, h, color, highlight_color, font, option_list, selected=0):
        self.color = color
        self.highlight_color = highlight_color
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.option_list = option_list
        self.selected = selected
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1

    def draw(self, surf):
        pygame.draw.rect(surf, self.highlight_color if self.menu_active else self.color, self.rect)
        pygame.draw.rect(surf, (0, 0, 0), self.rect, 2)
        msg = self.font.render(self.option_list[self.selected], 1, (0, 0, 0))
        surf.blit(msg, msg.get_rect(center=self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.option_list):
                rect = self.rect.copy()
                rect.y += (i + 1) * self.rect.height
                pygame.draw.rect(surf, self.highlight_color if i == self.active_option else self.color, rect)
                msg = self.font.render(text, 1, (0, 0, 0))
                surf.blit(msg, msg.get_rect(center=rect.center))
            outer_rect = (
            self.rect.x, self.rect.y + self.rect.height, self.rect.width, self.rect.height * len(self.option_list))
            pygame.draw.rect(surf, (0, 0, 0), outer_rect, 2)

    def update(self, event_list):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)

        self.active_option = -1
        for i in range(len(self.option_list)):
            rect = self.rect.copy()
            rect.y += (i + 1) * self.rect.height
            if rect.collidepoint(mpos):
                self.active_option = i
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or (event.type == pygame.FINGERDOWN):
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.selected = self.active_option
                    self.draw_menu = False
                    return self.active_option
        return -1

class RadioButton(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, font, text):
        super().__init__()
        text_surf = font.render(text, True, (0, 0, 0))
        self.button_image = pygame.Surface((w, h))
        self.button_image.fill('thistle2')
        self.button_image.blit(text_surf, text_surf.get_rect(center=(w // 2, h // 2)))
        self.hover_image = pygame.Surface((w, h))
        self.hover_image.fill('thistle2')
        self.hover_image.blit(text_surf, text_surf.get_rect(center=(w // 2, h // 2)))
        pygame.draw.rect(self.hover_image, ('#ee4e34'), self.hover_image.get_rect(), 3)
        self.clicked_image = pygame.Surface((w, h))
        self.clicked_image.fill('#ee4e34')
        self.clicked_image.blit(text_surf, text_surf.get_rect(center=(w // 2, h // 2)))
        self.image = self.button_image
        self.rect = pygame.Rect(x, y, w, h)
        self.clicked = False
        self.buttons = None

    def setRadioButtons(self, buttons):
        self.buttons = buttons

    def update(self, event_list):
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        for event in event_list:
            if (event.type == pygame.MOUSEBUTTONDOWN) or (event.type == pygame.FINGERDOWN):
                if hover:
                    for rb in self.buttons:
                        rb.clicked = False
                    self.clicked = True

        self.image = self.button_image
        if self.clicked:
            self.image = self.clicked_image
        elif hover:
            self.image = self.hover_image

class FrameState():

    def __init__(self):
        self.estado = 1
        self.accion = False
        self.timer_boton = 0
        self.timer_tuto = 0
        self.tm = True
        self.user_text = ''
        self.estudios_login = 0
        self.game_active = False

        # ////login buttons/////
        self.radioButtons = [
            RadioButton(80, 230, 80, 35, short_font, "Masculino"),
            RadioButton(80, 280, 80, 35, short_font, "Femenino")
        ]
        self.radioButtonsAccept = [
            RadioButton(350, 280, 80, 35, short_font, "Acepto"),
            RadioButton(450, 280, 80, 35, short_font, "No Acepto")
        ]
        for rb in self.radioButtons:
            rb.setRadioButtons(self.radioButtons)
        self.radioButtons[0].clicked = True
        for rb in self.radioButtonsAccept:
            rb.setRadioButtons(self.radioButtonsAccept)
        self.radioButtonsAccept[1].clicked = True
        self.gender = pygame.sprite.Group(self.radioButtons)
        self.disclaimer = pygame.sprite.Group(self.radioButtonsAccept)

        self.studies = OptionBox(
            60, 165, 140, 25, '#ee4e34', 'thistle2', pygame.font.SysFont('Quicksand', 16),
            ['Primarios', 'Secundarios', 'Universitarios', 'Postgrado', 'Diplomado', 'Maestría'])

        self.slider = Slider(screen, 140, 105, 200, 15, min=16, max=85, step=1, initial=30, handleRadius = 18, handleColour = (238,78,52))
        self.output = TextBox(screen, 60, 95, 45, 40, fontSize=30, font=pygame.font.SysFont('Quicksand',22))
        self.output.disable()
        # /////////////////////

    def waithere(self):
        if self.tm == False:
            # time.sleep(3)
            print('waiting..')
            pygame.time.wait(random.randint(2,5)*1000)
            self.tm = True

    def presiona_boton(self, imagen, rectangulo):
        global indice_tuto
        if self.accion:
            self.transparent = (0, 0, 0, 0)
            imagen.fill(self.transparent)
            screen.blit(imagen, rectangulo)
            if indice_tuto == 2:
                indice_tuto = 0
            else:
                indice_tuto += 1
            self.tm = False
            self.accion = False
        else:
            screen.blit(imagen, rectangulo)
       
    def login_datos(self):
        self.edad_login = self.slider.getValue()
        if self.radioButtons[0].clicked == True:
            self.genero_login = 'M'
        else:
            self.genero_login = 'F'
        if self.estudios == 0:
            self.estudios_login = 'Primarios'
        elif self.estudios == 1:
            self.estudios_login = 'Secundarios'
        elif self.estudios == 2:
            self.estudios_login = 'Universitarios'
        elif self.estudios == 3:
            self.estudios_login = 'Postgrado'
        elif self.estudios == 4:
            self.estudios_login = 'Diplomado'
        elif self.estudios == 5:
            self.estudios_login = 'Maestría'
        # cursor.execute("INSERT INTO usuarios VALUES "\
        #                '(self.edad_login, self.estudios_login, self.genero_login,0,0)')
        # conexion.commit()
        # conexion.close()
        print(self.edad_login)
        print(self.estudios_login)
        print(self.genero_login)
        self.estado = 4

    def cancel_datos(self):
        self.estado = 1
        self.radioButtonsAccept[0].clicked = False
        self.radioButtonsAccept[1].clicked = True

    def main_menu(self):  # Frame principal (1)
        screen.fill("thistle2")
        principal_surface = pygame.image.load('images/logo640x350.png').convert()
        screen.blit(principal_surface, (-15, 0))

        menu_mouse_pos = pygame.mouse.get_pos()

        btn_menu = Button(image=None, pos=(300, 380), text_input="SIMULADOR", font=main_font, base_color="black",
                               hovering_color="thistle4")

        for button in [btn_menu]:  # [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]
            button.changeColor(menu_mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                if btn_menu.checkForInput(menu_mouse_pos):
                    self.estado = 2
        pygame.display.flip()

    def rules(self):  # Frame reglas (2)
        rules_mouse_pos = pygame.mouse.get_pos()
        screen.fill("thistle2")
        fondo_surface = pygame.image.load('images/via.png').convert()
        instrucciones_surface = pygame.image.load('images/Instruccionesss.PNG').convert_alpha()
        screen.blit(fondo_surface, (0, 0))
        screen.blit(instrucciones_surface, (-10, 50))

        btn_rules = Button(image=None, pos=(300, 380), text_input="CONTINUAR", font=main_font,
                             base_color="black", hovering_color="thistle4")

        for button in [btn_rules]:  # [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]
            button.changeColor(rules_mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                if btn_rules.checkForInput(rules_mouse_pos):
                    self.estado = 3

        pygame.display.flip()

    def login(self): #Frame de login-inicio (3)
        screen.fill("#0a3057")
        login_mouse_pos = pygame.mouse.get_pos()
        login_text = main_font.render("Ingrese los datos para continuar", True, "#ee4e34")
        login_rect = login_text.get_rect(midleft=(25, 40))
        estudios_text = short_font.render("Pulse para seleccionar sus estudios:", True, "white")
        estudios_rect = estudios_text.get_rect(midleft=(55, 150))
        edad_text = short_font.render("Deslice la barra para ingresar su edad:", True, "white")
        edad_rect = edad_text.get_rect(midleft=(55, 80))
        genero_text = short_font.render("Seleccione su género:", True, "white")
        genero_rect = genero_text.get_rect(midleft=(55, 210))
        logo_surface = pygame.image.load('images/logoAzul100x100.png').convert_alpha()
        disclaimer_surf = pygame.image.load('images/disclaimer.png').convert_alpha()
        pygame.draw.rect(screen, 'thistle2', (0, 360, 600, 40))
        pygame.draw.rect(screen, 'black', (1, 361, 598, 38), 2)
        pygame.draw.line(screen, 'black', (400, 360), (400, 600),2)
        screen.blit(logo_surface, (500, 10))
        screen.blit(disclaimer_surf, (310, 150))
        screen.blit(login_text, login_rect)
        screen.blit(estudios_text, estudios_rect)
        screen.blit(edad_text, edad_rect)
        screen.blit(genero_text, genero_rect)


        btn_acepta = Button(image=None, pos=(190, 380), text_input="Acepte los términos para Continuar", font=main_font,
                           base_color="black", hovering_color="thistle4")
        btn_no_acepta = Button(image=None, pos=(500, 380), text_input="Salir", font=main_font,
                            base_color="black", hovering_color="thistle4")

        for button in [btn_no_acepta]:  # [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]
            button.changeHoverColor(login_mouse_pos)
            button.update(screen)

        self.event_list = pygame.event.get()
        for event in self.event_list:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.FINGERDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                if btn_acepta.checkInput(login_mouse_pos):
                    self.login_datos()
                elif btn_no_acepta.checkInput(login_mouse_pos):
                    self.estado = 1



        self.selected_option = self.studies.update(self.event_list)
        if self.selected_option >= 0:
            self.estudios = self.selected_option
            

        if self.radioButtonsAccept[0].clicked == True:
            for button in [btn_acepta]:  # [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]
                button.changeHoverColor(login_mouse_pos)
                button.update(screen)

        self.output.setText(self.slider.getValue())
        # print(slider.getValue())
        pygame_widgets.update(self.event_list)
        self.gender.update(self.event_list)
        self.disclaimer.update(self.event_list)
        self.gender.draw(screen)
        self.disclaimer.draw(screen)
        self.studies.draw(screen)
        pygame.display.flip()

    def tutorial(self): #Frame tutorial pedales y botones (4)
        global indice_tuto
        self.orden_tuto = ['amarillo', 'azul', 'blanco']
        screen.fill("thistle2")
        tutorial_surface = pygame.image.load('images/via.png').convert()
        tutorial_surface = pygame.transform.scale(tutorial_surface, (620, 410))
        screen.blit(tutorial_surface, (-10, 0))
        semaforo_surf = pygame.image.load('images/Green.png').convert_alpha()
        screen.blit(semaforo_surf, (490, 35))
        self.amarillo_tuto = pygame.image.load('images/estimulos/Amarillo_M.png').convert_alpha()
        self.amarillo_tuto_rect = self.amarillo_tuto.get_rect(center=(300, 180))
        self.blanco_tuto = pygame.image.load('images/estimulos/Blanco_M.png').convert_alpha()
        self.blanco_tuto_rect = self.blanco_tuto.get_rect(center=(300, 180))
        self.azul_tuto = pygame.image.load('images/estimulos/Azul_M.png').convert_alpha()
        self.azul_tuto_rect = self.azul_tuto.get_rect(center=(300, 180))
        self.morado_tuto = pygame.image.load('images/estimulos/Morado_M.png').convert_alpha()
        self.morado_tuto_rect = self.morado_tuto.get_rect(center=(300, 180))
        self.rojo_tuto = pygame.image.load('images/estimulos/Rojo_M.png').convert_alpha()
        self.rojo_tuto_rect = self.rojo_tuto.get_rect(center=(300, 180))
        self.vino_tuto = pygame.image.load('images/estimulos/Vino_M.png').convert_alpha()
        self.vino_tuto_rect = self.vino_tuto.get_rect(center=(300, 180))
        self.pare_tuto = pygame.image.load('images/estimulos/PareM.png').convert_alpha()
        self.pare_tuto_rect = self.pare_tuto.get_rect(center=(300, 180))
        self.estimulos = self.orden_tuto[indice_tuto]

        if self.estimulos == 'amarillo':
            FrameState.waithere(self)
            FrameState.presiona_boton(self, self.amarillo_tuto, self.amarillo_tuto_rect)
        elif self.estimulos == 'blanco':
            FrameState.waithere(self)
            FrameState.presiona_boton(self, self.blanco_tuto, self.blanco_tuto_rect)
        elif self.estimulos == 'azul':
            FrameState.waithere(self)
            FrameState.presiona_boton(self, self.azul_tuto, self.azul_tuto_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    # self.timer_boton = pygame.time.get_ticks()
                    self.accion = True
                    print('presionó a')
                if event.key == pygame.K_m:
                    self.estado = 5

        self.timer_tuto = pygame.time.get_ticks()

        pygame.display.flip()

    def level_selector(self): # Seleccion de nivel (5)
        screen.fill("#0a3057")
        level_text = main_font.render("Seleccione la dificultad", True, "#ee4e34")
        level_rect = level_text.get_rect(center=(300,60))
        logo_surface = pygame.image.load('images/logoAzul100x100.png').convert_alpha()
        screen.blit(logo_surface, (500, 10))
        screen.blit(level_text, level_rect)
        pygame.draw.rect(screen, 'darkgreen', (220, 130, 160, 40))
        pygame.draw.rect(screen, 'yellow', (220, 210, 160, 40))
        pygame.draw.rect(screen, 'red', (220, 290, 160, 40))

        level_mouse_pos = pygame.mouse.get_pos()

        btn_level_easy = Button(image=None, pos=(300, 150), text_input="FÁCIL", font=main_font, base_color="white",
                               hovering_color="thistle3")
        btn_level_normal = Button(image=None, pos=(300, 230), text_input="NORMAL", font=main_font, base_color="black",
                                hovering_color="thistle3")
        btn_level_hard = Button(image=None, pos=(300, 310), text_input="DIFÍCIL", font=main_font, base_color="white",
                                hovering_color="thistle3")

        for button in [btn_level_easy, btn_level_normal, btn_level_hard]:  # [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]
            button.changeHoverColor(level_mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                if btn_level_easy.checkInput(level_mouse_pos):
                    print('Inicia Modo Facil')
                    self.estado = 6
                elif btn_level_normal.checkInput(level_mouse_pos):
                    print('Inicia Modo Normal')
                    self.estado = 7
                elif btn_level_hard.checkInput(level_mouse_pos):
                    print('Inicia Modo Dificil')
                    self.estado = 8

        pygame.display.flip()

    def easy_mode(self): #Frame nivel facil (6)
        screen.fill("thistle2")
        tutorial_surface = pygame.image.load('images/viaEasy.PNG').convert()
        screen.blit(tutorial_surface, (-15, 0))
        semaforo_surf = pygame.image.load('images/Green.png').convert_alpha()
        screen.blit(semaforo_surf, (490, 35))
        '''
            //////
            Aqui poner codigo para el nivel facil
            //////
        '''

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    self.estado = 5
                elif event.key == pygame.K_m:
                    self.estado = 9

        pygame.display.flip()

    def normal_mode(self): #Frame nivel normal (7)
        screen.fill("thistle2")
        tutorial_surface = pygame.image.load('images/viaMed.png').convert()
        screen.blit(tutorial_surface, (-15, -5))
        semaforo_surf = pygame.image.load('images/Green.png').convert_alpha()
        screen.blit(semaforo_surf, (490, 35))
        '''
            //////
            Aqui poner codigo para el nivel normal
            //////
        '''

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    print('pedal pressed!!')
                    self.game_active = True
                elif event.key == pygame.K_n:
                    self.estado = 5
                elif event.key == pygame.K_m:
                    self.estado = 9
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    print('pedal released!!')
                    self.game_active = False
        
        if self.game_active:
            print('game active')
        else:
            print('----------')

        pygame.display.flip()

    def hard_mode(self): #Frame nivel dificil (8)
        screen.fill("thistle2")
        tutorial_surface = pygame.image.load('images/viaPro.PNG').convert()
        screen.blit(tutorial_surface, (-25, 5))
        semaforo_surf = pygame.image.load('images/Green.png').convert_alpha()
        screen.blit(semaforo_surf, (490, 35))
        '''
            //////
            Aqui poner codigo para el nivel dificil
            //////
        '''

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    self.estado = 5
                elif event.key == pygame.K_m:
                    self.estado = 9

        pygame.display.flip()

    def end_scores(self):  # Seleccion de nivel (9)
        self.correctos = 20
        screen.fill("#0a3057")
        title_text = main_font.render("Simulación Finalizada", True, "#ee4e34")
        title_rect = title_text.get_rect(center=(300, 60))
        prueba_text = big_font.render("Prueba", True, "white")
        prueba_rect = prueba_text.get_rect(midleft=(150, 150))
        superada_text = big_font.render("Superada", True, "white")
        superada_rect = superada_text.get_rect(midleft=(290, 150))
        no_superada_text = big_font.render("NO Superada", True, "white")
        no_superada_rect = no_superada_text.get_rect(midleft=(280, 150))
        posibles_text = main_font.render("aciertos de 30 posibles", True, "white")
        posibles_rect = posibles_text.get_rect(midleft=(200, 250))
        aciertos_text = big_font.render(str(self.correctos), True, "#ee4e34")
        aciertos_rect = aciertos_text.get_rect(midright=(190, 250))
        logo_surface = pygame.image.load('images/logoAzul100x100.png').convert_alpha()
        pygame.draw.rect(screen, 'thistle2', (0, 360, 600, 40))
        pygame.draw.rect(screen, 'black', (1, 361, 200, 38),2)
        pygame.draw.rect(screen, 'black', (204, 361, 200, 38),2)
        pygame.draw.rect(screen, 'black', (407, 361, 192, 38),2)
        screen.blit(logo_surface, (500, 10))
        screen.blit(title_text, title_rect)
        screen.blit(prueba_text, prueba_rect)
        screen.blit(posibles_text, posibles_rect)
        screen.blit(aciertos_text, aciertos_rect)
        if self.correctos >= 23:
            screen.blit(superada_text, superada_rect)
        else:
            screen.blit(no_superada_text, no_superada_rect)

        end_mouse_pos = pygame.mouse.get_pos()

        btn_detail_results = Button(image=None, pos=(100, 380), text_input="DETALLE DE RESULTADOS", font=short_font, base_color="black",
                                hovering_color="thistle4")
        btn_change_level = Button(image=None, pos=(305, 380), text_input="CAMBIAR DIFICULTAD", font=short_font, base_color="black",
                                  hovering_color="thistle4")
        btn_end_test = Button(image=None, pos=(500, 380), text_input="FINALIZAR PRUEBA", font=short_font, base_color="black",
                                hovering_color="thistle4")

        for button in [btn_detail_results, btn_change_level, btn_end_test]:  # [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]
            button.changeHoverColor(end_mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                if btn_detail_results.checkInput(end_mouse_pos):
                    print('Muestro resultados')
                    self.estado = 10
                elif btn_change_level.checkInput(end_mouse_pos):
                    print('Cambio de dificultad')
                    self.estado = 5
                elif btn_end_test.checkInput(end_mouse_pos):
                    print('Fin Prueba, pantalla inicial')
                    self.estado = 1

        pygame.display.flip()

    def show_result(self):
        screen.fill("#0a3057")
        login_text = main_font.render("Resultados", True, "#ee4e34")
        login_rect = login_text.get_rect(midleft=(25, 20))
        logo_surface = pygame.image.load('images/logoAzul100x100.png').convert_alpha()
        screen.blit(logo_surface, (500, 10))
        screen.blit(login_text, login_rect)
        pygame.draw.rect(screen, 'thistle2', (0, 360, 600, 40))
        pygame.draw.rect(screen, 'black', (1, 361, 598, 38),2)
        input_rect = pygame.Rect(5, 40, 490, 310)

        login_mouse_pos = pygame.mouse.get_pos()

        btn_goback = Button(image=None, pos=(300, 380), text_input="REGRESAR", font=main_font, base_color="Black",
                           hovering_color="thistle4")

        for button in [btn_goback]:
            button.changeColor(login_mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                if btn_goback.checkForInput(login_mouse_pos):
                    self.estado = 9

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.user_text = self.user_text[:-1]
                else:
                    self.user_text += event.unicode

        pygame.draw.rect(screen, 'white', input_rect)
        text_surface = short_font.render(self.user_text, True, (0, 0, 0))
        screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
        input_rect.w = max(100, text_surface.get_width() + 10)
        pygame.display.flip()

    def frame_manager(self):
        # print('frame_manager')
        if self.estado == 1:
            self.radioButtonsAccept[0].clicked = False
            self.radioButtonsAccept[1].clicked = True
            self.radioButtons[0].clicked = True
            self.radioButtons[1].clicked = False
            self.slider.setValue(30)
            self.studies.selected = 0
            self.main_menu()
        elif self.estado == 2:
            self.rules()
        elif self.estado == 3:
            self.login()
        elif self.estado == 4:
            self.tutorial()
        elif self.estado == 5:
            self.level_selector()
        elif self.estado == 6:
            self.easy_mode()
        elif self.estado == 7:
            self.normal_mode()
        elif self.estado == 8:
            self.hard_mode()
        elif self.estado == 9:
            self.end_scores()
        elif self.estado == 10:
            self.show_result()



# General Setup
pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption('Simulador')
clock = pygame.time.Clock()
main_font = pygame.font.SysFont("Quicksand", 26)  #//Color naranja Aneta '#ee4e34' --- Color azul Aneta '#0a3057'
big_font = pygame.font.SysFont("Quicksand", 36)
short_font = pygame.font.SysFont("Quicksand", 14)
frame_state = FrameState()
conexion = sqlite3.connect('Datos.db')
cursor = conexion.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS usuarios"\
              "(edad INTEGER, estudios TEXT, genero TEXT, correctos INTEGER, prom_tiempo FLOAT)")

conexion.commit()

indice_tuto = 0

# #// Pulsadores en pines del Raspberry
# pulAzul = gpioz.Button('GPIO22')
# pulBlanco = gpioz.Button('GPIO27')
# pulAmarillo = gpioz.Button('GPIO17')

# Mainloop
while True:
    frame_state.frame_manager()
    clock.tick(30)
