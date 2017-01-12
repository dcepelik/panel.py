from widgets.widget import StaticWidget

class SpacerWidget(StaticWidget):
    
    def __init__(self, panel, width):
        super().__init__(panel, "spacer")
        self.width = width;

    def render(self, font):
        return "^p({})".format(self.width)

    def get_rendered_width(self):
        return self.width
