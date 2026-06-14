from direct.task import Task
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import (
    TransparencyAttrib,
    Fog,
    AmbientLight,
    DirectionalLight,
    WindowProperties
)
import time
import math

class AAAIntro:
    def __init__(self, base_app, on_finish_callback):
        # Store references to main app and callback
        self.base_app = base_app
        self.on_finish_callback = on_finish_callback

        # Access Panda3D engine nodes through the active base instance
        self.base_app.disableMouse()
        self.base_app.setBackgroundColor(0, 0, 0)
        self.base_app.ignore("escape")
        
        props = WindowProperties()
        props.setCursorHidden(True)
        self.base_app.win.requestProperties(props)

        # Scene lighting and fog setups
        self.fog = Fog("fog")
        self.fog.setColor(0, 0, 0)
        self.fog.setExpDensity(0.035)
        self.base_app.render.setFog(self.fog)

        self.amb = AmbientLight("amb")
        self.amb.setColor((0.04, 0.04, 0.05, 1))
        self.amb_np = self.base_app.render.attachNewNode(self.amb)
        self.base_app.render.setLight(self.amb_np)

        self.key = DirectionalLight("key")
        self.key.setColor((0.6, 0.6, 0.65, 1))
        self.key_np = self.base_app.render.attachNewNode(self.key)
        self.key_np.setHpr(35, -20, 0)
        self.base_app.render.setLight(self.key_np)

        self.base_app.camera.setPos(0, -22, 2)
        self.base_app.camera.lookAt(0, 0, 0)

        # Audio and assets
        self.audio = self.base_app.loader.loadSfx("audio/intro.wav")
        self.audio.play()

        self.duration = self.audio.length()

        self.company = OnscreenImage(image="assets/logo.png", pos=(0, 0, 0), scale=0.7)
        self.company.setTransparency(TransparencyAttrib.MAlpha)
        self.company.setColorScale(1, 1, 1, 0)

        self.panda = OnscreenImage(image="assets/panda3d_logo.png", pos=(0, 0, 0), scale=0.7)
        self.panda.setTransparency(TransparencyAttrib.MAlpha)
        self.panda.setColorScale(1, 1, 1, 0)

        self.start = time.time()
        
        self.base_app.taskMgr.add(self.update_intro_task, "update_intro_task")

    def ease(self, t):
        return t * t * (3 - 2 * t)

    def update_intro_task(self, task):
        t = time.time() - self.start

        self.base_app.camera.setPos(math.sin(t * 0.4) * 0.2, -22 + t * 0.18, 2)

        if t < 4:
            a = self.ease(t / 4)
            self.company.setColorScale(1, 1, 1, a)
        elif t < 6:
            self.company.setColorScale(1, 1, 1, 1)
        elif t < 8:
            f = 1 - self.ease((t - 6) / 2)
            self.company.setColorScale(1, 1, 1, f)

        if 7 < t < 10:
            a = self.ease((t - 7) / 3)
            self.panda.setColorScale(1, 1, 1, a)
        elif t >= 10:
            self.panda.setColorScale(1, 1, 1, 1)

        fade_start = max(self.duration - 3.0, 10)
        if t > fade_start:
            f = max(1 - (t - fade_start) / 3.0, 0)
            self.panda.setColorScale(1, 1, 1, f)

        if t >= self.duration:
            # Cleanup Assets
            self.company.destroy()
            self.panda.destroy()
            
            # Clear Intro Specific Lighting/Fog
            self.base_app.render.clearFog()
            self.base_app.render.clearLight(self.amb_np)
            self.base_app.render.clearLight(self.key_np)
            self.amb_np.removeNode()
            self.key_np.removeNode()
            
            props = WindowProperties()
            props.setCursorHidden(False)
            self.base_app.win.requestProperties(props)
            
            # Fire transition trigger out to Main Menu
            self.on_finish_callback()
            return Task.done

        return Task.cont
