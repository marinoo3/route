from app.modules import Display
from app.vues.base import Vue



class Ui:
    vue: Vue
    
    def __init__(self, display: Display) -> None:
        self.display = display

    def load_vue(self, vue: Vue) -> None:
        """
        Load a vue on UI

        Args:
            screen (Screen): Screen to load, child of Screen class
        """
        self.vue = vue
        self.vue.load(self.display)

    def update(self) -> None:
        """
        Update the ui and vue
        """
        self.vue.update()

