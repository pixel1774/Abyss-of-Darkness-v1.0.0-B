from direct.gui.DirectGui import DirectFrame, DirectButton
from direct.gui.OnscreenText import OnscreenText
from direct.gui import DirectGuiGlobals as DGG
from panda3d.core import TextNode
import json


class AchievementsMenu:
    def __init__(self, app):
        self.app = app
        self.frame = DirectFrame(relief=None)
        self.frame.hide()

        self.scroll_offset = 0
        self.visible_items = 5   # slightly less = cleaner spacing
        self.item_spacing = 0.14

        self.achievements = {}
        self.items = []

        self.build_ui()

    def build_ui(self):
        OnscreenText(
            text="ACHIEVEMENTS",
            pos=(0, 0.7),
            scale=0.14,
            fg=(1, 1, 1, 1),
            font=self.app.silkscreen,
            parent=self.frame
        )

        self.list_frame = DirectFrame(
            frameColor=(0, 0, 0, 0.3),
            frameSize=(-0.85, 0.85, -0.45, 0.5),
            pos=(0, 0, 0),
            parent=self.frame
        )

        # Scroll buttons
        self.up_btn = DirectButton(
            text="▲",
            scale=0.05,
            pos=(0.8, 0, 0.4),
            command=self.scroll_up,
            relief=DGG.FLAT,
            frameColor=(0.2, 0.2, 0.2, 0.8),
            parent=self.frame
        )

        self.down_btn = DirectButton(
            text="▼",
            scale=0.05,
            pos=(0.8, 0, -0.4),
            command=self.scroll_down,
            relief=DGG.FLAT,
            frameColor=(0.2, 0.2, 0.2, 0.8),
            parent=self.frame
        )

        # Back button
        self.back_button = DirectButton(
            text="BACK",
            scale=self.app.normal_scale,
            pos=(0, 0, -0.75),
            command=self.go_back,
            text_font=self.app.silkscreen,
            text_fg=(1, 1, 1, 1),
            relief=DGG.FLAT,
            frameColor=(0.2, 0.2, 0.2, 0.8),
            parent=self.frame
        )

        self.app.setup_button_hover(self.back_button)

        # Mouse scroll
        self.app.accept("wheel_up", self.scroll_up)
        self.app.accept("wheel_down", self.scroll_down)

    def load_achievements(self):
        try:
            with open("sources/achievements.json", "r") as f:
                self.achievements = json.load(f)
        except:
            self.achievements = {}

    def rebuild_list(self):
        # Clear old items
        for item in self.items:
            item.destroy()
        self.items.clear()

        keys = list(self.achievements.keys())

        start = self.scroll_offset
        end = min(start + self.visible_items, len(keys))

        for i, key in enumerate(keys[start:end]):
            value = self.achievements[key]

            y = 0.35 - i * self.item_spacing

            status_text = "Complete" if value else "Incomplete"
            status_color = (0.1, 0.8, 0.1, 1) if value else (0.8, 0.1, 0.1, 1)

            # --- Achievement Name (WRAPPED TEXT) ---
            name = OnscreenText(
                text=key,
                pos=(-0.78, y),
                scale=0.05,
                fg=(1, 1, 1, 1),
                font=self.app.silkscreen,
                align=TextNode.ALeft,
                wordwrap=18,   # 👈 FIXES TEXT OVERFLOW
                parent=self.list_frame
            )

            # --- Status ---
            status = OnscreenText(
                text=status_text,
                pos=(0.7, y),
                scale=0.05,
                fg=status_color,
                font=self.app.silkscreen,
                align=TextNode.ARight,
                parent=self.list_frame
            )

            self.items.append(name)
            self.items.append(status)

    def scroll_up(self):
        if self.scroll_offset > 0:
            self.scroll_offset -= 1
            self.rebuild_list()

    def scroll_down(self):
        if self.scroll_offset + self.visible_items < len(self.achievements):
            self.scroll_offset += 1
            self.rebuild_list()

    def show(self):
        self.load_achievements()
        self.scroll_offset = 0
        self.rebuild_list()
        self.frame.show()

    def hide(self):
        self.frame.hide()

    def go_back(self):
        self.hide()
        self.app.main_menu_frame.show()