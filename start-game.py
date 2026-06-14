from panda3d.core import loadPrcFileData
from main import MyApp
from intro import AAAIntro

# Load your custom graphic multisample settings window parameters upfront
loadPrcFileData(
    "", 
    "framebuffer-multisample 1\nmultisamples 4\nundecorated 1\nfullscreen 1\nwin-size 1920 1080\nshow-frame-rate-meter 0"
)

if __name__ == "__main__":
    # 1. Open the underlying system application window context
    app = MyApp()
    
    # 2. Inject the Intro sequence inside it and point it to the main menu reveal function
    intro_sequence = AAAIntro(base_app=app, on_finish_callback=app.show_main_menu)
    
    # 3. Start running engine context updates
    app.run()
