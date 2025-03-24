import pygame
import sys
import os
pygame.init()
width, height = 640, 480
screen = pygame.display.set_mode((width, height))
rect_color = (100, 100, 100)  # Зеленый цвет
text_color = (255, 255, 255)  # Белый цвет
rect_x, rect_y = 10, 10
rect_width, rect_height = 300, 150
text = "Перетащите папку сюда"
font = pygame.font.Font(None, 24)  # None использует системный шрифт, 36 — размер шрифта
text_surface = font.render(text, True, text_color)
text_width, text_height = text_surface.get_size()
text_x = rect_x + (rect_width - text_width) // 2
text_y = rect_y + (rect_height - text_height) // 2
running = True
dragged_file = None  # Переменная для хранения пути к перетащенному файлу/папке
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.DROPFILE:  # Событие перетаскивания файла
            dragged_file = event.file  # Получаем путь к файлу/папке
            print(f"Перетащенный папка: {dragged_file}")
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if (rect_x <= mouse_x <= rect_x + rect_width and
                rect_y <= mouse_y <= rect_y + rect_height):
                if dragged_file:  # Если файл/папка была перетащена
                    print(f"Выбранный путь: {dragged_file}")
                    if os.path.isdir(dragged_file):  # Проверяем, является ли путь папкой
                        print("Это папка!")
                    elif os.path.isfile(dragged_file):  # Проверяем, является ли путь файлом
                        print("Это файл!")
    screen.fill((50, 50, 50))
    pygame.draw.rect(screen, rect_color, (rect_x, rect_y, rect_width, rect_height))
    screen.blit(text_surface, (text_x, text_y))
    pygame.display.flip()
pygame.quit()