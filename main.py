from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextProperties, TextPropertiesManager
from panda3d.core import Vec4, Texture
from direct.gui.DirectGui import DirectButton, DirectFrame
from direct.gui import DirectGuiGlobals as DGG
from direct.interval.IntervalGlobal import LerpScaleInterval
from direct.gui.OnscreenImage import OnscreenImage
import json
from panda3d.core import loadPrcFileData

from menus import OptionsMenu
from achievements import AchievementsMenu   

try:
    with open('sources/options.json', 'r') as file:
        data = json.load(file)
except:
    data = {
        "video": {"vsync": True},
        "resolution": {"width": 1920, "height": 1080},
        "audio": {"master_volume": 70, "game_music": 70, "sound_effects": 50},
        "auto_fullscreen": False
    }

vsync_state = data.get("video", {}).get("vsync", True)
loadPrcFileData("", f"sync-video {'true' if vsync_state else 'false'}")


class MyApp(ShowBase):
    def __init__(self):
        super().__init__()

        self.game_config = data
        self.apply_startup_settings()
        self.setFrameRateMeter(True)

        # Create Background but keep it HIDDEN until intro finishes
        self.background = OnscreenImage(
            image='sources/textures/menu_background_1024x768.png',
            parent=render2dp
        )
        self.background.hide()

        base.cam2dp.node().getDisplayRegion(0).setSort(-20)

        self.normal_scale = 0.10
        self.hover_scale = 0.12
        self.duration = 0.2
        self.active_animations = {}

        props = WindowProperties()
        props.setSize(1024, 768)
        props.setTitle("Abyss of Darkness")
        self.win.requestProperties(props)

        gold_prop = TextProperties()
        gold_prop.setTextColor(Vec4(1, 0.85, 0, 1))
        TextPropertiesManager.getGlobalPtr().setProperties("gold", gold_prop)

        self.silkscreen = loader.loadFont("fonts/Silkscreen-Regular.ttf")
        if self.silkscreen:
            self.silkscreen.set_pixels_per_unit(200)
            self.silkscreen.setMinfilter(Texture.FTLinear)

        # MAIN MENU FRAME (Created Hidden)
        self.main_menu_frame = DirectFrame(relief=None)
        self.main_menu_frame.hide()

        # MENUS
        self.options_menu = OptionsMenu(self)
        self.achievements_menu = AchievementsMenu(self)   

        # TITLE
        OnscreenText(
            text="Abyss of \1gold\1Darkness\2",
            pos=(0, 0.7),
            scale=0.20,
            fg=(1, 1, 1, 1),
            font=self.silkscreen,
            parent=self.main_menu_frame
        )

        # BUTTONS
        self.start_button = DirectButton(
            text="Start Game",
            scale=self.normal_scale,
            pos=(0, 0, 0),
            command=self.start_game,
            text_font=self.silkscreen,
            pad=(0.5, 0.3),
            relief=None,
            text_fg=(1, 1, 1, 1),
            parent=self.main_menu_frame
        )

        self.achievement_btn = DirectButton(
            text="Achievements",
            scale=self.normal_scale,
            pos=(0, 0, -0.2),
            command=self.open_achievements,   
            text_font=self.silkscreen,
            pad=(0.5, 0.3),
            relief=None,
            text_fg=(1, 1, 1, 1),
            parent=self.main_menu_frame
        )

        self.fullscreen_btn = DirectButton(
            text="Fullscreen",
            scale=self.normal_scale,
            pos=(0, 0, -0.4),
            command=self.toggle_fullscreen,
            text_font=self.silkscreen,
            pad=(0.5, 0.3),
            relief=None,
            text_fg=(1, 1, 1, 1),
            parent=self.main_menu_frame
        )

        self.settings_button = DirectButton(
            text="Options",
            scale=self.normal_scale,
            pos=(0, 0, -0.6),
            command=self.open_settings,
            text_font=self.silkscreen,
            pad=(0.5, 0.3),
            relief=None,
            text_fg=(1, 1, 1, 1),
            parent=self.main_menu_frame
        )

        # HOVER EFFECTS
        self.setup_button_hover(self.start_button)
        self.setup_button_hover(self.fullscreen_btn)
        self.setup_button_hover(self.achievement_btn)
        self.setup_button_hover(self.settings_button)

    # ---------------- REVEAL MAIN MENU SEQUENCE ----------------

    def show_main_menu(self):
        # Clear out anything left behind by the intro environment rendering
        self.camera.setPos(0, -22, 2)
        self.camera.lookAt(0, 0, 0)
        self.setBackgroundColor(0, 0, 0) # Fallback window background color
        
        # Unhide menu layout and background asset seamlessly
        self.background.show()
        self.main_menu_frame.show()

    # ---------------- SETTINGS ----------------

    def apply_startup_settings(self):
        if self.game_config.get("auto_fullscreen", False):
            self.apply_startup_fullscreen()

    def apply_startup_fullscreen(self):
        res = self.game_config.get("resolution", {})
        width = res.get("width", 1920)
        height = res.get("height", 1080)

        self.user_w = width
        self.user_h = height

        self.taskMgr.doMethodLater(0, self._restart_window_fullscreen, "restartFS")

    def _restart_window_fullscreen(self, task):
        wp = WindowProperties()
        wp.setSize(self.user_w, self.user_h)
        wp.setFullscreen(True)

        self.win.requestProperties(wp)
        return task.done

    def toggle_fullscreen(self):
        current = self.win.getProperties()

        res = self.game_config.get("resolution", {})
        width = res.get("width", 1920)
        height = res.get("height", 1080)

        wp = WindowProperties()

        if current.getFullscreen():
            wp.setFullscreen(False)
            wp.setSize(1024, 768)
            self.game_config["auto_fullscreen"] = False
        else:
            wp.setFullscreen(True)
            wp.setSize(width, height)
            self.game_config["auto_fullscreen"] = True

        with open('sources/options.json', 'w') as file:
            json.dump(self.game_config, file, indent=4)

        self.win.requestProperties(wp)

    # ---------------- BUTTON EFFECTS ----------------

    def setup_button_hover(self, button):
        button.bind(DGG.WITHIN, self.on_hover_enter, extraArgs=[button])
        button.bind(DGG.WITHOUT, self.on_hover_exit, extraArgs=[button])
        self.active_animations[button] = None

    def on_hover_enter(self, button, status):
        if self.active_animations[button]:
            self.active_animations[button].finish()

        self.active_animations[button] = LerpScaleInterval(
            button,
            self.duration,
            self.hover_scale,
            blendType='easeInOut'
        )
        self.active_animations[button].start()

    def on_hover_exit(self, button, status):
        if self.active_animations[button]:
            self.active_animations[button].finish()

        self.active_animations[button] = LerpScaleInterval(
            button,
            self.duration,
            self.normal_scale,
            blendType='easeInOut'
        )
        self.active_animations[button].start()

    # ---------------- MENU NAVIGATION ----------------

    def start_game(self):
        print("start the game")

    def open_settings(self):
        self.main_menu_frame.hide()
        self.options_menu.show()

    def open_achievements(self):
        self.main_menu_frame.hide()                
        self.achievements_menu.show()              
