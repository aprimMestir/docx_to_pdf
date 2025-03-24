import pygame
import sys
import os
import re
from tkinter import Tk, filedialog

pygame.init()

# Настройки интерфейса
WIDTH, HEIGHT = 800, 600
BG_COLOR = (45, 45, 55)
PANEL_COLOR = (60, 60, 70)
ACCENT_COLOR = (0, 150, 255)
TEXT_COLOR = (240, 240, 240)
INPUT_COLOR = (80, 80, 90)
INPUT_ACTIVE_COLOR = (100, 100, 120)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('DOCX to PDF Converter')

# Шрифты
font_large = pygame.font.Font(None, 32)
font_medium = pygame.font.Font(None, 24)
font_small = pygame.font.Font(None, 18)


# Элементы интерфейса
class DropArea:
    def __init__(self, x, y, w, h, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.image = None
        self.text = ""
        self.active = False

    def draw(self, surface):
        # Рисуем область
        color = ACCENT_COLOR if self.active else PANEL_COLOR
        pygame.draw.rect(surface, color, self.rect, 0, 10)
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 2, 10)

        # Если есть изображение - отображаем его
        if self.image:
            img_rect = self.image.get_rect(center=self.rect.center)
            surface.blit(self.image, img_rect)
        else:
            # Отображаем текст (с переносами)
            self.render_text(surface)

    def render_text(self, surface):
        if not self.text:
            text = font_medium.render(self.label, True, TEXT_COLOR)
            text_rect = text.get_rect(center=self.rect.center)
            surface.blit(text, text_rect)
        else:
            # Многострочный текст для пути
            lines = self.wrap_text(self.text, font_small, self.rect.w - 20)
            total_h = len(lines) * font_small.get_linesize()
            y = self.rect.y + (self.rect.h - total_h) // 2

            for line in lines:
                text = font_small.render(line, True, TEXT_COLOR)
                text_rect = text.get_rect(centerx=self.rect.centerx, y=y)
                surface.blit(text, text_rect)
                y += font_small.get_linesize()

    @staticmethod
    def wrap_text(text, font, max_width):
        """Разбивает текст на строки по ширине"""
        words = text.split('\\')
        lines = []
        current_line = []

        for word in words:
            test_line = '\\'.join(current_line + [word]) if current_line else word
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append('\\'.join(current_line))
                current_line = [word]

        if current_line:
            lines.append('\\'.join(current_line))

        return lines[:3]  # Не более 3 строк


# Создаем элементы интерфейса
drop_areas = [
    DropArea(50, 50, 300, 180, "Перетащите папку с DOCX"),
    DropArea(450, 50, 300, 180, "Перетащите штамп"),
    DropArea(450, 280, 300, 180, "Перетащите подпись")
]

# Координатные поля
coord_fields = []
for i in range(2):
    for j in range(2):
        x = 450 + i * 160
        y = 480 + j * 40
        coord_fields.append(pygame.Rect(x, y, 150, 30))

coord_labels = ["Штамп X:", "Штамп Y:", "Подпись X:", "Подпись Y:"]
coord_values = ["100", "100", "100", "100"]
active_field = None

# Кнопка сохранения
save_btn = pygame.Rect(50, 480, 200, 40)
output_folder = ""

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Обработка перетаскивания файлов
        elif event.type == pygame.DROPFILE:
            file_path = event.file
            mouse_pos = pygame.mouse.get_pos()

            for area in drop_areas:
                if area.rect.collidepoint(mouse_pos):
                    try:
                        if area == drop_areas[0] and os.path.isdir(file_path):
                            area.text = file_path
                        elif area != drop_areas[0] and os.path.isfile(file_path):
                            img = pygame.image.load(file_path)
                            img = pygame.transform.scale(img, (area.rect.w - 20, area.rect.h - 20))
                            area.image = img
                    except:
                        pass

        # Обработка кликов
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # Проверка кликов по координатным полям
            active_field = None
            for i, field in enumerate(coord_fields):
                if field.collidepoint(mouse_pos):
                    active_field = i

            # Проверка клика по кнопке сохранения
            if save_btn.collidepoint(mouse_pos):
                root = Tk()
                root.withdraw()
                folder = filedialog.askdirectory(title="Выберите папку для сохранения")
                if folder:
                    output_folder = folder
                    print(f"Выбрана папка для сохранения: {output_folder}")

        # Обработка ввода текста
        elif event.type == pygame.KEYDOWN and active_field is not None:
            if event.key == pygame.K_RETURN:
                active_field = None
            elif event.key == pygame.K_BACKSPACE:
                coord_values[active_field] = coord_values[active_field][:-1]
            elif event.unicode.isdigit() or event.unicode == ',':
                coord_values[active_field] += event.unicode

    # Отрисовка
    screen.fill(BG_COLOR)

    # Заголовок
    title = font_large.render("Конвертер DOCX в PDF", True, TEXT_COLOR)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))

    # Области перетаскивания
    for area in drop_areas:
        area.active = area.rect.collidepoint(pygame.mouse.get_pos())
        area.draw(screen)

    # Координатные поля
    for i, (label, field, value) in enumerate(zip(coord_labels, coord_fields, coord_values)):
        label_surf = font_medium.render(label, True, TEXT_COLOR)
        screen.blit(label_surf, (field.x - 120, field.y + 5))

        color = INPUT_ACTIVE_COLOR if i == active_field else INPUT_COLOR
        pygame.draw.rect(screen, color, field, 0, 5)
        pygame.draw.rect(screen, (100, 100, 100), field, 2, 5)

        value_surf = font_medium.render(value, True, TEXT_COLOR)
        screen.blit(value_surf, (field.x + 10, field.y + 5))

    # Кнопка сохранения
    pygame.draw.rect(screen, ACCENT_COLOR, save_btn, 0, 5)
    pygame.draw.rect(screen, (100, 100, 100), save_btn, 2, 5)

    btn_text = "Выбрать папку" if not output_folder else os.path.basename(output_folder)
    btn_surf = font_medium.render(btn_text, True, TEXT_COLOR)
    screen.blit(btn_surf, (save_btn.centerx - btn_surf.get_width() // 2, save_btn.centery - btn_surf.get_height() // 2))

    # Подпись папки сохранения
    if output_folder:
        folder_text = font_small.render(f"Сохранение в: {output_folder}", True, (200, 200, 200))
        screen.blit(folder_text, (50, 530))

    pygame.display.flip()

pygame.quit()
sys.exit()