from widgets.widget import StaticWidget

class TextWidget(StaticWidget):
    
    def __init__(self, panel, text):
        super().__init__(panel, "text")
        self.text = text

    def do_render(self):
        return self.text
