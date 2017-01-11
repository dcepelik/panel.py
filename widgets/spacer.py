from widgets.widget import StaticWidget

class SpacerWidget(StaticWidget):
    
    def __init__(self, panel, width):
        super().__init__(panel, "spacer")
        self.width = width;

    def render(self):
        return "^p({})".format(self.width)


    def measure_width(self, font):
        return self.width
