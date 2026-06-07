import pygame
from . import utils

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
BLUE = (0, 100, 200)

UPGRADES = [
    {
        "id": "fuel_tank",
        "name": "Fuel Tank",
        "description": "+200 max fuel capacity",
        "cost": 50,
        "max_level": 5,
        "stat": "fuel_max",
        "amount": 200,
    },
    {
        "id": "efficiency",
        "name": "Engine Efficiency",
        "description": "-4 fuel consumed per second",
        "cost": 75,
        "max_level": 5,
        "stat": "fuel_consumption",
        "amount": -4,
    },
    {
        "id": "thruster",
        "name": "Thruster Power",
        "description": "+0.05 thrust acceleration",
        "cost": 60,
        "max_level": 5,
        "stat": "thrust",
        "amount": 0.05,
    },
    {
        "id": "gyroscope",
        "name": "Gyroscope",
        "description": "+1 rotation speed",
        "cost": 40,
        "max_level": 3,
        "stat": "rotation_speed",
        "amount": 1,
    },
    {
        "id": "mining_laser",
        "name": "Mining Laser",
        "description": "+50 % mining speed",   # handling v update_game
        "cost": 100,
        "max_level": 3,
        "stat": None,
        "amount": 0,
    },
]

class Menu:
    def __init__(self, screen_width, screen_height, title="Menu", options=None, background_image_name=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.title = title
        self.options = options or ['Start Game', 'Quit']
        self.selected_option = 0
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 36)
        self.background_image = None
        if background_image_name:
            try:
                image = utils.load_image(background_image_name)
                self.background_image = pygame.transform.scale(image, (screen_width, screen_height))
            except Exception:
                self.background_image = None

    def draw_text(self, screen, text, font, color, x, y):
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (x, y))

    def draw(self, screen):
        if self.background_image is not None:
            screen.blit(self.background_image, (0, 0))
        else:
            screen.fill(BLACK)
        title_width = self.font.size(self.title)[0]
        self.draw_text(screen, self.title, self.font, WHITE, self.screen_width // 2 - title_width // 2, self.screen_height // 4)


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


class PauseMenu(Menu):
    def __init__(self, screen_width, screen_height, title="Paused", options=None, initial_volume: float = 0.35):
        # expected options list should include a 'Volume' entry where the slider appears
        super().__init__(screen_width, screen_height, title, options)
        self.volume = max(0.0, min(1.0, initial_volume))

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.options and self.options[self.selected_option].lower().startswith('volume'):
                if event.key == pygame.K_LEFT:
                    self.volume = max(0.0, self.volume - 0.05)
                    utils.set_music_volume(self.volume)
                    return None
                elif event.key == pygame.K_RIGHT:
                    self.volume = min(1.0, self.volume + 0.05)
                    utils.set_music_volume(self.volume)
                    return None
                elif event.key == pygame.K_RETURN:
                    return None
        return super().handle_input(event)

    def draw(self, screen):
        display_options = []
        for opt in self.options:
            if opt.lower().startswith('volume'):
                display_options.append(f"Volume: {int(self.volume * 100)}%")
            else:
                display_options.append(opt)

        old_options = self.options
        self.options = display_options
        super().draw(screen)
        self.options = old_options

class UpgradeMenu:
    def __init__(self, screen_width, screen_height):
        self.screen_width  = screen_width
        self.screen_height = screen_height
        self.selected   = 0
        self.upgrades   = UPGRADES
        self.title_font = pygame.font.Font(None, 48)
        self.font       = pygame.font.Font(None, 34)
        self.small_font = pygame.font.Font(None, 26)
        self.feedback_msg   = ""
        self.feedback_timer = 0.0
        self.feedback_ok    = True

    def handle_input(self, event, player):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.upgrades)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.upgrades)
            elif event.key == pygame.K_RETURN:
                self._try_purchase(player)
            elif event.key in (pygame.K_ESCAPE, pygame.K_TAB):
                return "close"
        return None

    def _try_purchase(self, player):
        upg   = self.upgrades[self.selected]
        level = player.upgrade_levels.get(upg["id"], 0)

        if level >= upg["max_level"]:
            self._feedback("Already at max level!", ok=False)
            return
        
        if player.credits < upg["cost"]:
            self._feedback("Not enough credits!", ok=False)
            return

        player.credits -= upg["cost"]
        player.upgrade_levels[upg["id"]] = level + 1

        if upg["stat"] is not None:
            current = getattr(player, upg["stat"])
            setattr(player, upg["stat"], current + upg["amount"])
            if upg["stat"] == "fuel_max":
                player.fuel = min(player.fuel + upg["amount"], player.fuel_max)     #kdyz koupi pridat rovnou tech 200

        self._feedback(f"{upg['name']} - Lv {level + 1}", ok=True)

    def _feedback(self, msg, ok=True):
        self.feedback_msg   = msg
        self.feedback_timer = 2.5
        self.feedback_ok    = ok

    def update(self, delta_time):
        if self.feedback_timer > 0:
            self.feedback_timer -= delta_time

    def draw(self, screen, player):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))

        panel_w, panel_h = 640, 120 + len(self.upgrades) * 80 + 80
        panel_x = self.screen_width  // 2 - panel_w // 2
        panel_y = self.screen_height // 2 - panel_h // 2

        pygame.draw.rect(screen, (10, 12, 30), (panel_x, panel_y, panel_w, panel_h))
        pygame.draw.rect(screen, (0, 150, 255), (panel_x, panel_y, panel_w, panel_h), 2)

        title_surf = self.title_font.render("UPGRADE SHOP", True, (0, 210, 255))
        screen.blit(title_surf, (self.screen_width // 2 - title_surf.get_width() // 2, panel_y + 14))

        cred_surf = self.font.render(f"Credits: {int(player.credits)}", True, (255, 215, 0))
        screen.blit(cred_surf, (panel_x + 20, panel_y + 65))

        for i, upg in enumerate(self.upgrades):
            level  = player.upgrade_levels.get(upg["id"], 0)
            maxed  = level >= upg["max_level"]
            row_y  = panel_y + 120 + i * 80
            can_buy = (not maxed) and (player.credits >= upg["cost"])

            if i == self.selected:
                pygame.draw.rect(screen, (0, 55, 110),
                                 (panel_x + 8, row_y - 4, panel_w - 16, 72))
                pygame.draw.rect(screen, (0, 140, 255),
                                 (panel_x + 8, row_y - 4, panel_w - 16, 72), 1)
                arrow = ">"
            else:
                arrow = "  "

            name_color = (160, 160, 160) if maxed else WHITE
            name_surf  = self.font.render(arrow + upg["name"], True, name_color)
            screen.blit(name_surf, (panel_x + 18, row_y))

            lv_text  = "MAX" if maxed else f"Lv {level} / {upg['max_level']}"
            lv_color = (0, 255, 140) if maxed else (150, 200, 255)
            lv_surf  = self.small_font.render(lv_text, True, lv_color)
            screen.blit(lv_surf, (panel_x + panel_w - lv_surf.get_width() - 18, row_y + 4))

            desc_surf = self.small_font.render(upg["description"], True, (140, 140, 165))
            screen.blit(desc_surf, (panel_x + 36, row_y + 36))

            if maxed:
                cost_text  = "MAXED"
                cost_color = (80, 200, 80)
            elif can_buy:
                cost_text  = f"{upg['cost']} credits"
                cost_color = (255, 215, 0)
            else:
                cost_text  = f"{upg['cost']} credits"
                cost_color = (220, 60, 60)
            cost_surf = self.small_font.render(cost_text, True, cost_color)
            screen.blit(cost_surf, (panel_x + panel_w - cost_surf.get_width() - 18, row_y + 36))

        if self.feedback_timer > 0:
            fb_color = (0, 255, 140) if self.feedback_ok else (255, 80, 80)
            fb_surf  = self.font.render(self.feedback_msg, True, fb_color)
            screen.blit(fb_surf, (self.screen_width // 2 - fb_surf.get_width() // 2,
                                  panel_y + panel_h - 65))

        instr_surf = self.small_font.render(
            "UP/DOWN arrows  Navigate      ENTER  Buy      TAB / ESC  Close", True, (90, 90, 120))
        screen.blit(instr_surf, (self.screen_width // 2 - instr_surf.get_width() // 2,
                                 panel_y + panel_h - 30))  