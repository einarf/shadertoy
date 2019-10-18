from pathlib import Path

import moderngl_window
from moderngl_window.resources import programs
from moderngl_window import geometry
from moderngl_window import resources

# Register system resource directory in this package
resources.register_dir(
    Path(__file__).parent / 'resources'
)


class ShaderToyWindow(moderngl_window.WindowConfig):
    title = "Python Shadertoy"
    resource_dir = Path(__file__).parent
    aspect_ratio = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_program_mtime = 0
        self.main_program_path = Path('test.glsl').resolve()
        self.main_program = None
        self.load_main_program()
        self.quad_fs = geometry.quad_fs()
        self.fallback_program = self.load_program('shadertoy/programs/fallback.glsl')
        self.error_state = False
        self.mouse_pos = 0, 0

    @classmethod
    def run(cls):
        moderngl_window.run_window_config(cls)

    def render(self, time, frame_time):
        self.check_reload()

        if self.error_state:
            self.quad_fs.render(self.fallback_program)
            return

        self.set_uniform('iTime', time)
        self.set_uniform('iMouse', self.mouse_pos)
        self.set_uniform(
            'iResolution',
            (self.wnd.buffer_size[0], self.wnd.buffer_size[1]),
        )
        self.quad_fs.render(self.main_program)

    def set_uniform(self, name, value):
        """Safely set uniform value"""
        try:
            self.main_program[name].value = value
        except KeyError:
            pass
        except NameError:
            pass

    def check_reload(self, force=False):
        mtime = self.main_program_path.stat().st_mtime
        if self.main_program_mtime < mtime:
            print("Reloading program...")
            self.main_program_mtime = mtime
            self.load_main_program()

    def load_main_program(self, force=False):
        try:
            new_program = self.load_program(self.main_program_path.parts[-1])
        except Exception as ex:
            self.error_state = True
            print(ex)
            return

        if self.main_program:
            self.main_program.release()

        self.main_program = new_program
        self.error_state = False

    def key_event(self, key, action, modifiers):
        keys = self.wnd.keys

    def mouse_drag_event(self, x, y):
        self.mouse_pos = x, y
