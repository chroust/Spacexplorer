import pygame

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
BLUE = (0, 100, 200)

class Menu:
    def __init__(self, screen_width, screen_height, title="Menu", options=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.title = title
        self.options = options or ['Start Game', 'Quit']
        self.selected_option = 0
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 36)

    def draw_text(self, screen, text, font, color, x, y):
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (x, y))

    def draw(self, screen):
        screen.fill(BLACK)
        title_width = self.font.size(self.title)[0]
        self.draw_text(screen, self.title, self.font, WHITE,
                      self.screen_width // 2 - title_width // 2, self.screen_height // 4)


        for i, option in enumerate(self.options):
            color = BLUE if i == self.selected_option else WHITE
            option_width = self.small_font.size(option)[0]
            self.draw_text(screen, option, self.small_font, color,
                          self.screen_width // 2 - option_width // 2,
                          self.screen_height // 2 + i * 50)


        instructions = "Use UP/DOWN arrows to navigate, ENTER to select"
        instr_width = self.small_font.size(instructions)[0]
        self.draw_text(screen, instructions, self.small_font, GRAY,
                      self.screen_width // 2 - instr_width // 2, self.screen_height - 100)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.options[self.selected_option]
        return None

    def reset_selection(self):
        self.selected_option = 0