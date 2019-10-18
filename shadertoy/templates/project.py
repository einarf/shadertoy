from pathlib import Path
from shadertoy import ShaderToyWindow


class Project(ShaderToyWindow):
    resource_dir = Path(__file__).parent.resolve()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wnd.position = 0, 0


if __name__ == '__main__':
    Project.run()
