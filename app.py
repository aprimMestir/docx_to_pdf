import pygame
import sys
import os
import re
from tkinter import Tk, filedialog
from pygame import mixer
from datetime import datetime
import random

# Инициализация
pygame.init()
mixer.init()

# Настройки интерфейса
WIDTH, HEIGHT = 900, 700
BG_COLOR = (40, 42, 50)
PANEL_COLOR = (55, 57, 65)
ACCENT_COLOR = (0, 150, 255)
TEXT_COLOR = (240, 240, 240)
INPUT_COLOR = (70, 72, 80)
INPUT_ACTIVE_COLOR = (90, 92, 100)
SUCCESS_COLOR = (80, 200, 120)
ERROR_COLOR = (220, 80, 80)
WARNING_COLOR = (220, 180, 60)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('DOCX to PDF Converter Pro')

# Загрузка звуков
try:
    drop_sound = mixer.Sound('sounds/drop.wav')
    click_sound = mixer.Sound('sounds/click.wav')
    success_sound = mixer.Sound('sounds/success.wav')
    error_sound = mixer.Sound('sounds/error.wav')
    process_sound = mixer.Sound('sounds/process.wav')
except:
    print("Звуковые файлы не найдены, работаем без звуков")

# Загрузка шрифтов
try:
    title_font = pygame.font.Font('fonts/Roboto-Bold.ttf', 36)
    header_font = pygame.font.Font('fonts/Roboto-Medium.ttf', 24)
    text_font = pygame.font.Font('fonts/Roboto-Regular.ttf', 20)
    small_font = pygame.font.Font('fonts/Roboto-Light.ttf', 16)
except:
    print("Пользовательские шрифты не найдены, используем системные")
    title_font = pygame.font.Font(None, 36)
    header_font = pygame.font.Font(None, 24)
    text_font = pygame.font.Font(None, 20)
    small_font = pygame.font.Font(None, 16)


class DropArea:
    def __init__(self, x, y, w, h, label, file_type='any'):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.file_type = file_type
        self.image = None
        self.text = ""
        self.active = False
        self.error = False

    def draw(self, surface):
        # Рисуем область с разными состояниями
        if self.error:
            border_color = ERROR_COLOR
            fill_color = (80, 50, 50)
        elif self.active:
            border_color = ACCENT_COLOR
            fill_color = PANEL_COLOR
        else:
            border_color = (80, 80, 80)
            fill_color = PANEL_COLOR

        pygame.draw.rect(surface, fill_color, self.rect, border_radius=12)
        pygame.draw.rect(surface, border_color, self.rect, 2, 12)

        # Отображаем содержимое
        if self.image:
            img_rect = self.image.get_rect(center=self.rect.center)
            surface.blit(self.image, img_rect)
        else:
            self.render_text(surface)

    def render_text(self, surface):
        if not self.text:
            # Текст по умолчанию
            lines = [self.label]
            if self.file_type == 'folder':
                lines.append("(перетащите папку)")
            elif self.file_type == 'image':
                lines.append("(PNG, JPEG)")

            total_h = len(lines) * text_font.get_linesize()
            y = self.rect.centery - total_h // 2

            for i, line in enumerate(lines):
                font = text_font if i == 0 else small_font
                color = TEXT_COLOR if i == 0 else (180, 180, 180)
                text = font.render(line, True, color)
                text_rect = text.get_rect(centerx=self.rect.centerx, y=y)
                surface.blit(text, text_rect)
                y += font.get_linesize()
        else:
            # Пользовательский текст (путь к файлу)
            lines = self.wrap_text(self.text, small_font, self.rect.w - 40)
            total_h = len(lines) * small_font.get_linesize()
            y = self.rect.centery - total_h // 2

            for line in lines:
                text = small_font.render(line, True, TEXT_COLOR)
                text_rect = text.get_rect(centerx=self.rect.centerx, y=y)
                surface.blit(text, text_rect)
                y += small_font.get_linesize()

    @staticmethod
    def wrap_text(text, font, max_width):
        words = text.replace('\\', '/').split('/')
        lines = []
        current_line = []

        for word in words:
            test_line = ('/' if current_line else '') + word
            if font.size(''.join(current_line + [test_line]))[0] <= max_width:
                current_line.append(test_line)
            else:
                if current_line:
                    lines.append(''.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(''.join(current_line))

        return lines[:4]  # Максимум 4 строки


class Button:
    def __init__(self, x, y, w, h, text, color=ACCENT_COLOR):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = (
            min(color[0] + 20, 255),
            min(color[1] + 20, 255),
            min(color[2] + 20, 255)
        )
        self.active = False
        self.disabled = False

    def draw(self, surface):
        color = self.hover_color if self.active and not self.disabled else self.color
        if self.disabled:
            color = (100, 100, 100)

        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (80, 80, 80), self.rect, 2, 8)

        text = header_font.render(self.text, True, TEXT_COLOR)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

    def check_hover(self, pos):
        self.active = self.rect.collidepoint(pos) and not self.disabled
        return self.active


class InputField:
    def __init__(self, x, y, w, h, label, default=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.value = default
        self.active = False

    def draw(self, surface):
        # Рисуем поле ввода
        color = INPUT_ACTIVE_COLOR if self.active else INPUT_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, (80, 80, 80), self.rect, 2, 6)

        # Отображаем текст
        label_surf = text_font.render(self.label, True, TEXT_COLOR)
        surface.blit(label_surf, (self.rect.x - label_surf.get_width() - 10,
                                  self.rect.y + (self.rect.h - label_surf.get_height()) // 2))

        # Значение поля
        value_surf = text_font.render(self.value, True, TEXT_COLOR)
        surface.blit(value_surf, (self.rect.x + 10,
                                  self.rect.y + (self.rect.h - value_surf.get_height()) // 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            if self.active and 'click_sound' in globals():
                click_sound.play()

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]
            elif event.unicode.isdigit() or event.unicode in (',', '.'):
                self.value += event.unicode


# Создание элементов интерфейса
drop_areas = [
    DropArea(50, 100, 400, 200, "Исходные документы", 'folder'),
    DropArea(470, 100, 380, 200, "Изображение штампа", 'image'),
    DropArea(470, 320, 380, 200, "Изображение подписи", 'image')
]

input_fields = [
    InputField(500, 540, 100, 40, "Штамп X:", "100"),
    InputField(630, 540, 100, 40, "Штамп Y:", "100"),
    InputField(500, 590, 100, 40, "Подпись X:", "100"),
    InputField(630, 590, 100, 40, "Подпись Y:", "100")
]

buttons = [
    Button(50, 540, 400, 45, "Выбрать папку для сохранения"),
    Button(50, 600, 400, 60, "ОБРАБОТАТЬ ДОКУМЕНТЫ", SUCCESS_COLOR)
]

# Переменные состояния
output_folder = ""
status_message = ("", TEXT_COLOR)
status_timer = 0
processing = False
progress = 0
processed_files = []


def validate_inputs():
    """Проверяет все необходимые данные перед обработкой"""
    if not drop_areas[0].text:
        drop_areas[0].error = True
        return False, "Не выбрана папка с документами"
    drop_areas[0].error = False

    if not output_folder:
        return False, "Не выбрана папка для сохранения"

    try:
        float(input_fields[0].value)
        float(input_fields[1].value)
        float(input_fields[2].value)
        float(input_fields[3].value)
    except ValueError:
        return False, "Некорректные координаты"

    return True, ""


def process_files():
    """Функция обработки файлов (заглушка с анимацией)"""
    global processing, progress, status_message, status_timer, processed_files

    # Проверка входных данных
    valid, message = validate_inputs()
    if not valid:
        status_message = (message, ERROR_COLOR)
        status_timer = 180
        if 'error_sound' in globals():
            error_sound.play()
        return

    # Начало обработки
    processing = True
    progress = 0
    processed_files = []
    status_message = ("Начата обработка документов...", WARNING_COLOR)

    if 'process_sound' in globals():
        process_sound.play()

    # Симуляция обработки (в реальном коде здесь будет конвертация)
    # Генерируем случайные имена обработанных файлов
    file_count = random.randint(3, 12)
    processed_files = [f"document_{i + 1}.pdf" for i in range(file_count)]


def update_processing():
    """Обновляет прогресс обработки (заглушка)"""
    global processing, progress, status_message, status_timer

    if not processing:
        return

    progress += 0.5
    if progress >= 100:
        processing = False
        status_message = (f"Успешно обработано {len(processed_files)} файлов", SUCCESS_COLOR)
        status_timer = 180
        if 'success_sound' in globals():
            success_sound.play()
    elif progress % 10 == 0:
        status_message = (f"Обработка... {int(progress)}%", WARNING_COLOR)


# Главный цикл
running = True
clock = pygame.time.Clock()

while running:
    dt = clock.tick(60)

    # Обновление статуса
    if status_timer > 0:
        status_timer -= 1
    else:
        status_message = ("", TEXT_COLOR)

    # Обновление прогресса обработки
    update_processing()

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.DROPFILE:
            file_path = event.file
            mouse_pos = pygame.mouse.get_pos()

            for area in drop_areas:
                if area.rect.collidepoint(mouse_pos):
                    try:
                        if area.file_type == 'folder' and os.path.isdir(file_path):
                            area.text = file_path
                            area.error = False
                            if 'drop_sound' in globals():
                                drop_sound.play()

                        elif area.file_type == 'image' and os.path.isfile(file_path):
                            valid_ext = file_path.lower().endswith(('.png', '.jpg', '.jpeg'))
                            if valid_ext:
                                img = pygame.image.load(file_path)
                                aspect = img.get_width() / img.get_height()

                                # Масштабируем с сохранением пропорций
                                if aspect > 1:
                                    new_w = area.rect.w - 40
                                    new_h = new_w / aspect
                                else:
                                    new_h = area.rect.h - 40
                                    new_w = new_h * aspect

                                img = pygame.transform.scale(img, (int(new_w), int(new_h)))
                                area.image = img
                                area.error = False
                                if 'drop_sound' in globals():
                                    drop_sound.play()
                            else:
                                area.error = True
                    except Exception as e:
                        print(f"Ошибка загрузки: {e}")
                        area.error = True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # Проверка кликов по полям ввода
            for field in input_fields:
                field.handle_event(event)

            # Проверка кликов по кнопкам
            for btn in buttons:
                if btn.check_hover(mouse_pos) and event.button == 1:
                    if btn.text == "Выбрать папку для сохранения":
                        root = Tk()
                        root.withdraw()
                        folder = filedialog.askdirectory(title="Выберите папку для сохранения PDF")
                        if folder:
                            output_folder = folder
                            if 'click_sound' in globals():
                                click_sound.play()

                    elif btn.text == "ОБРАБОТАТЬ ДОКУМЕНТЫ" and not processing:
                        process_files()

        elif event.type == pygame.KEYDOWN:
            for field in input_fields:
                if field.active:
                    if event.key == pygame.K_RETURN:
                        field.active = False
                    elif event.key == pygame.K_BACKSPACE:
                        field.value = field.value[:-1]
                    elif event.unicode.isdigit() or event.unicode in (',', '.'):
                        field.value += event.unicode

    # Отрисовка
    screen.fill(BG_COLOR)

    # Заголовок
    title = title_font.render("КОНВЕРТЕР DOCX В PDF", True, TEXT_COLOR)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

    # Текущая дата и время
    time_text = small_font.render(datetime.now().strftime("%d.%m.%Y %H:%M"), True, (150, 150, 150))
    screen.blit(time_text, (WIDTH - time_text.get_width() - 20, 25))

    # Области перетаскивания
    for area in drop_areas:
        area.active = area.rect.collidepoint(pygame.mouse.get_pos())
        area.draw(screen)

    # Поля ввода координат
    for field in input_fields:
        field.draw(screen)

    # Кнопки
    buttons[0].disabled = False
    buttons[1].disabled = processing or not drop_areas[0].text or not output_folder

    for btn in buttons:
        btn.check_hover(pygame.mouse.get_pos())
        btn.draw(screen)

    # Информация о выбранных путях
    if output_folder:
        folder_text = small_font.render(f"Сохранение в: {output_folder}", True, (180, 220, 180))
        screen.blit(folder_text, (50, 670))

    # Статус обработки
    if status_message[0]:
        text, color = status_message
        status_surf = text_font.render(text, True, color)
        screen.blit(status_surf, (WIDTH // 2 - status_surf.get_width() // 2, 670))

    # Прогресс бар (если идет обработка)
    if processing:
        progress_width = 800 * (progress / 100)
        pygame.draw.rect(screen, (80, 80, 80), (50, 640, 800, 10), 0, 5)
        pygame.draw.rect(screen, ACCENT_COLOR, (50, 640, progress_width, 10), 0, 5)

    pygame.display.flip()

pygame.quit()
sys.exit()