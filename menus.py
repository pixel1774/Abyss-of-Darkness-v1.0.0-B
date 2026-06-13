from direct.gui.DirectGui import DirectButton, DirectFrame, DirectSlider, DirectOptionMenu
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import WindowProperties, loadPrcFileData
import json
import sys
import os


class OptionsMenu:
    def __init__(self, main_app):
        self.app = main_app
        self.frame = DirectFrame(relief=None)
        self.frame.hide()
        self.ignore_changes = False
        self.initial_vsync_on_open = True
        self.build_ui()

    def build_ui(self):
        OnscreenText(
            text="OPTIONS",
            pos=(0, 0.70),
            scale=0.14,
            fg=(1, 1, 1, 1),
            font=self.app.silkscreen,
            parent=self.frame
        )

        self.app.game_config.setdefault("audio", {})
        self.app.game_config.setdefault("video", {})
        self.app.game_config.setdefault("resolution", {})

        audio = self.app.game_config["audio"]
        video = self.app.game_config["video"]
        res = self.app.game_config["resolution"]

        self.vol_label = OnscreenText(text="MASTER VOLUME", pos=(-0.5, 0.45), scale=0.045, fg=(0.7, 0.7, 0.7, 1), font=self.app.silkscreen, parent=self.frame)
        self.vol_slider = DirectSlider(range=(0, 100), value=audio.get("master_volume", 100), pos=(0.20, 0, 0.47), scale=0.30, frameColor=(0.15, 0.15, 0.15, 1), thumb_frameColor=(0.9, 0.9, 0.9, 1), thumb_relief=DGG.FLAT, thumb_scale=0.04, parent=self.frame, command=self.update_vol_text)
        self.vol_value_text = OnscreenText(text=f"{int(self.vol_slider.getValue())}%", pos=(0.55, 0.45), scale=0.045, fg=(1, 1, 1, 1), font=self.app.silkscreen, parent=self.frame)

        self.music_label = OnscreenText(text="GAME MUSIC", pos=(-0.5, 0.32), scale=0.045, fg=(0.7, 0.7, 0.7, 1), font=self.app.silkscreen, parent=self.frame)
        self.music_slider = DirectSlider(range=(0, 100), value=audio.get("game_music", 75), pos=(0.20, 0, 0.34), scale=0.30, frameColor=(0.15, 0.15, 0.15, 1), thumb_frameColor=(0.9, 0.9, 0.9, 1), thumb_relief=DGG.FLAT, thumb_scale=0.04, parent=self.frame, command=self.update_music_text)
        self.music_value_text = OnscreenText(text=f"{int(self.music_slider.getValue())}%", pos=(0.55, 0.32), scale=0.045, fg=(1, 1, 1, 1), font=self.app.silkscreen, parent=self.frame)

        self.menu_music_label = OnscreenText(text="MENU MUSIC", pos=(-0.5, 0.19), scale=0.045, fg=(0.7, 0.7, 0.7, 1), font=self.app.silkscreen, parent=self.frame)
        self.menu_music_slider = DirectSlider(range=(0, 100), value=audio.get("menu_music", 50), pos=(0.20, 0, 0.21), scale=0.30, frameColor=(0.15, 0.15, 0.15, 1), thumb_frameColor=(0.9, 0.9, 0.9, 1), thumb_relief=DGG.FLAT, thumb_scale=0.04, parent=self.frame, command=self.update_menu_music_text)
        self.menu_music_value_text = OnscreenText(text=f"{int(self.menu_music_slider.getValue())}%", pos=(0.55, 0.19), scale=0.045, fg=(1, 1, 1, 1), font=self.app.silkscreen, parent=self.frame)

        self.sfx_label = OnscreenText(text="SOUND EFFECTS", pos=(-0.5, 0.06), scale=0.045, fg=(0.7, 0.7, 0.7, 1), font=self.app.silkscreen, parent=self.frame)
        self.sfx_slider = DirectSlider(range=(0, 100), value=audio.get("sound_effects", 80), pos=(0.20, 0, 0.08), scale=0.30, frameColor=(0.15, 0.15, 0.15, 1), thumb_frameColor=(0.9, 0.9, 0.9, 1), thumb_relief=DGG.FLAT, thumb_scale=0.04, parent=self.frame, command=self.update_sfx_text)
        self.sfx_value_text = OnscreenText(text=f"{int(self.sfx_slider.getValue())}%", pos=(0.55, 0.06), scale=0.045, fg=(1, 1, 1, 1), font=self.app.silkscreen, parent=self.frame)

        self.vsync_state = video.get("vsync", True)
        self.fs_state = self.app.game_config.get("auto_fullscreen", True)

        self.vsync_title = OnscreenText(text="VSYNC", pos=(-0.5, -0.09), scale=0.045, fg=(0.7, 0.7, 0.7, 1), font=self.app.silkscreen, parent=self.frame)
        self.vsync_btn = DirectButton(text="ENABLED" if self.vsync_state else "DISABLED", scale=0.045, pos=(0.12, 0, -0.08), command=self.toggle_vsync_ui, text_font=self.app.silkscreen, relief=None, text_fg=(0.1, 0.7, 0.1, 1) if self.vsync_state else (0.7, 0.1, 0.1, 1), parent=self.frame)

        self.fs_title = OnscreenText(text="AUTO FULLSCREEN", pos=(-0.5, -0.22), scale=0.045, fg=(0.7, 0.7, 0.7, 1), font=self.app.silkscreen, parent=self.frame)
        self.fs_btn = DirectButton(text="ENABLED" if self.fs_state else "DISABLED", scale=0.045, pos=(0.12, 0, -0.21), command=self.toggle_fs_ui, text_font=self.app.silkscreen, relief=None, text_fg=(0.1, 0.7, 0.1, 1) if self.fs_state else (0.7, 0.1, 0.1, 1), parent=self.frame)

        self.res_list = ["1024x768", "1280x720", "1920x1080", "2560x1440"]
        current_res = f"{res.get('width', 1920)}x{res.get('height', 1080)}"
        self.res_index = self.res_list.index(current_res) if current_res in self.res_list else 2

        self.res_label = OnscreenText(text="RESOLUTION", pos=(-0.5, -0.35), scale=0.045, fg=(0.7, 0.7, 0.7, 1), font=self.app.silkscreen, parent=self.frame)
        self.res_menu = DirectOptionMenu(items=self.res_list, initialitem=self.res_index, pos=(0.12, 0, -0.34), scale=0.045, text_font=self.app.silkscreen, text_fg=(1, 1, 1, 1), frameColor=(0.15, 0.15, 0.15, 1), popupMarker_frameColor=(0.3, 0.3, 0.3, 1), highlightColor=(0.3, 0.3, 0.3, 1), parent=self.frame, command=self.on_option_changed)

        self.back_button = DirectButton(text="BACK", scale=self.app.normal_scale, pos=(-0.35, 0, -0.65), command=self.close_without_saving, text_font=self.app.silkscreen, pad=(0.5, 0.3), relief=None, text_fg=(0.7, 0.7, 0.7, 1), parent=self.frame)
        self.save_button = DirectButton(text="SAVE", scale=self.app.normal_scale, pos=(0.35, 0, -0.65), command=self.save_settings, text_font=self.app.silkscreen, pad=(0.5, 0.3), relief=None, text_fg=(1, 0.85, 0, 1), parent=self.frame)
        self.save_button.hide()

        self.app.setup_button_hover(self.back_button)
        self.app.setup_button_hover(self.save_button)

    def get_selected_resolution(self):
        return tuple(map(int, self.res_menu.get().split("x")))

    def update_vol_text(self):
        self.vol_value_text.setText(f"{int(self.vol_slider.getValue())}%")
        self.on_option_changed()

    def update_music_text(self):
        self.music_value_text.setText(f"{int(self.music_slider.getValue())}%")
        self.on_option_changed()

    def update_menu_music_text(self):
        self.menu_music_value_text.setText(f"{int(self.menu_music_slider.getValue())}%")
        self.on_option_changed()

    def update_sfx_text(self):
        self.sfx_value_text.setText(f"{int(self.sfx_slider.getValue())}%")
        self.on_option_changed()

    def on_option_changed(self, *args):
        if not self.ignore_changes:
            self.save_button.show()

    def toggle_vsync_ui(self):
        self.vsync_state = not self.vsync_state
        self.vsync_btn["text"] = "ENABLED" if self.vsync_state else "DISABLED"
        self.vsync_btn["text_fg"] = (0.1, 0.7, 0.1, 1) if self.vsync_state else (0.7, 0.1, 0.1, 1)
        self.on_option_changed()

    def toggle_fs_ui(self):
        self.fs_state = not self.fs_state
        self.fs_btn["text"] = "ENABLED" if self.fs_state else "DISABLED"
        self.fs_btn["text_fg"] = (0.1, 0.7, 0.1, 1) if self.fs_state else (0.7, 0.1, 0.1, 1)
        self.on_option_changed()

    def show(self):
        self.ignore_changes = True
        self.save_button.hide()

        audio = self.app.game_config.get("audio", {})
        video = self.app.game_config.get("video", {})
        res = self.app.game_config.get("resolution", {})

        self.vol_slider.setValue(audio.get("master_volume", 100))
        self.music_slider.setValue(audio.get("game_music", 75))
        self.menu_music_slider.setValue(audio.get("menu_music", 50))
        self.sfx_slider.setValue(audio.get("sound_effects", 80))

        self.vsync_state = video.get("vsync", True)
        self.fs_state = self.app.game_config.get("auto_fullscreen", True)

        self.vsync_btn["text"] = "ENABLED" if self.vsync_state else "DISABLED"
        self.vsync_btn["text_fg"] = (0.1, 0.7, 0.1, 1) if self.vsync_state else (0.7, 0.1, 0.1, 1)

        self.fs_btn["text"] = "ENABLED" if self.fs_state else "DISABLED"
        self.fs_btn["text_fg"] = (0.1, 0.7, 0.1, 1) if self.fs_state else (0.7, 0.1, 0.1, 1)

        current_res = f"{res.get('width', 1920)}x{res.get('height', 1080)}"
        if current_res in self.res_list:
            self.res_menu.set(self.res_list.index(current_res))

        self.frame.show()
        self.ignore_changes = False

    def hide(self):
        self.frame.hide()

    def close_without_saving(self):
        self.hide()
        self.app.main_menu_frame.show()

    def save_settings(self):
        w, h = self.get_selected_resolution()
        vsync_changed = self.vsync_state != self.initial_vsync_on_open

        self.app.game_config.setdefault("audio", {})
        self.app.game_config.setdefault("video", {})
        self.app.game_config.setdefault("resolution", {})

        self.app.game_config["resolution"]["width"] = w
        self.app.game_config["resolution"]["height"] = h
        self.app.game_config["auto_fullscreen"] = self.fs_state
        self.app.game_config["audio"]["master_volume"] = int(self.vol_slider.getValue())
        self.app.game_config["audio"]["game_music"] = int(self.music_slider.getValue())
        self.app.game_config["audio"]["menu_music"] = int(self.menu_music_slider.getValue())
        self.app.game_config["audio"]["sound_effects"] = int(self.sfx_slider.getValue())
        self.app.game_config["video"]["vsync"] = self.vsync_state

        with open("sources/options.json", "w") as f:
            json.dump(self.app.game_config, f, indent=4)

        loadPrcFileData("", f"sync-video {'true' if self.vsync_state else 'false'}")

        wp = WindowProperties()
        wp.setSize(w, h)
        wp.setFullscreen(self.fs_state)

        self.app.win.requestProperties(wp)

        if vsync_changed:
            os.execv(sys.executable, [sys.executable] + sys.argv)

        self.initial_vsync_on_open = self.vsync_state
        self.save_button.hide()