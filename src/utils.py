import pygame
import os
import random

BASE_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(BASE_DIR, "img")

_image_cache: dict[str, pygame.Surface] = {}

# Audio caches
_sfx_cache: dict[str, pygame.mixer.Sound] = {}


def init_audio(frequency: int = 44100, size: int = -16, channels: int = 2, buffer: int = 512) -> None:
    """Initialize the pygame mixer if not already initialized."""
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=frequency, size=size, channels=channels, buffer=buffer)
    except Exception:
        try:
            pygame.mixer.init()
        except Exception:
            pass


def _sound_path(name: str) -> str:
    return os.path.join(IMG_DIR, "sound", name)


def play_music(filename: str, volume: float = 0.5, loops: int = -1) -> None:
    init_audio()
    try:
        pygame.mixer.music.load(_sound_path(filename))
        pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
        pygame.mixer.music.play(loops)
    except Exception:
        pass


def stop_music() -> None:
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass


def set_music_volume(volume: float) -> None:
    try:
        pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
    except Exception:
        pass


def get_music_volume() -> float:
    try:
        return float(pygame.mixer.music.get_volume())
    except Exception:
        return 0.0


def load_sfx(name: str) -> pygame.mixer.Sound | None:
    init_audio()
    if name in _sfx_cache:
        return _sfx_cache[name]
    path = _sound_path(name)
    if not os.path.exists(path):
        return None
    try:
        snd = pygame.mixer.Sound(path)
        _sfx_cache[name] = snd
        return snd
    except Exception:
        return None


def load_sfx_variant(names: list[str]) -> pygame.mixer.Sound | None:
    for n in names:
        snd = load_sfx(n)
        if snd is not None:
            return snd
    return None


_MUSIC_EXCLUDE_FILES = {
    'engine_loop.ogg', 'engine_loop.wav',
    'thrust.ogg', 'thrust.wav',
    'ship_thrust.ogg', 'ship_thrust.wav'
}


def list_music_files() -> list[str]:
    sound_dir = os.path.join(IMG_DIR, "sound")
    if not os.path.isdir(sound_dir):
        return []
    files = []
    for fn in os.listdir(sound_dir):
        if fn.lower().endswith(('.ogg', '.mp3', '.wav')):
            if fn.lower() in _MUSIC_EXCLUDE_FILES:
                continue
            files.append(fn)
    return files


def play_random_music(volume: float = 0.35, loops: int = -1) -> None:
    music_files = list_music_files()
    if not music_files:
        return
    play_music(random.choice(music_files), volume=volume, loops=loops)


def load_image(name: str) -> pygame.Surface:
    if name not in _image_cache:
        _image_cache[name] = (
            pygame.image.load(os.path.join(IMG_DIR, name)).convert_alpha()
        )
    return _image_cache[name]


def create_mask_from_img(surface: pygame.Surface) -> pygame.mask.Mask:
    return pygame.mask.from_surface(surface)


def load_image_with_mask(name: str) -> tuple[pygame.Surface, pygame.mask.Mask]:
    image = load_image(name)
    mask = create_mask_from_img(image)
    return image, mask


def load_sprite_variant(names: list[str]) -> pygame.Surface | None:
    if not names:
        return None
    chosen = random.choice(names)
    try:
        return load_image(chosen)
    except Exception:
        return None


def load_spritesheet(name: str, frame_width: int, frame_height: int) -> list[pygame.Surface]:
    """Slice a spritesheet into individual frame surfaces (left→right, top→bottom).

    Partial frames at the edge (remainder pixels) are silently ignored.
    """
    sheet = load_image(name)
    cols = sheet.get_width()  // frame_width
    rows = sheet.get_height() // frame_height
    frames: list[pygame.Surface] = []
    for row in range(rows):
        for col in range(cols):
            rect = pygame.Rect(col * frame_width, row * frame_height,
                               frame_width, frame_height)
            frames.append(sheet.subsurface(rect).copy())
    return frames


class AnimationController:
    """Frame-by-frame sprite animation with optional play-range and loop control.

    Parameters
    ----------
    frames          : list of Surfaces extracted from a spritesheet.
    frame_duration  : seconds each frame is shown.
    loop            : whether to repeat after ``end_frame``.
    start_frame     : first frame index to show (and the frame ``reset()`` returns to).
    end_frame       : last frame index to show (inclusive).  Defaults to last frame.
    loop_start_frame: frame index the animation jumps back to when looping.
                      Defaults to ``start_frame``.  Set this higher than
                      ``start_frame`` to skip an intro sequence on every loop
                      (e.g. ship idle frame) while still being able to reset()
                      back to the true first frame.
    """

    def __init__(
        self,
        frames: list[pygame.Surface],
        frame_duration: float = 0.1,
        loop: bool = True,
        start_frame: int = 0,
        end_frame: int | None = None,
        loop_start_frame: int | None = None,
    ) -> None:
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop
        self.start_frame = start_frame
        self.end_frame = (end_frame
                          if end_frame is not None
                          else max(len(frames) - 1, 0))
        self.loop_start_frame = (loop_start_frame
                                 if loop_start_frame is not None
                                 else self.start_frame)
        self.current_frame = self.start_frame
        self.elapsed_time = 0.0
        self.is_playing = False


    def play(self) -> None:
        self.is_playing = True

    def stop(self) -> None:
        self.is_playing = False

    def reset(self) -> None:
        """Return to start_frame.  Does *not* change is_playing."""
        self.current_frame = self.start_frame
        self.elapsed_time = 0.0


    def update(self, delta_time: float) -> None:
        if not self.is_playing or not self.frames:
            return
        self.elapsed_time += delta_time
        if self.elapsed_time >= self.frame_duration:
            self.elapsed_time -= self.frame_duration
            self.current_frame += 1
            if self.current_frame > self.end_frame:
                if self.loop:
                    self.current_frame = self.loop_start_frame
                else:
                    self.current_frame = self.end_frame
                    self.is_playing = False


    def get_current_frame(self) -> pygame.Surface | None:
        if not self.frames:
            return None
        return self.frames[self.current_frame]