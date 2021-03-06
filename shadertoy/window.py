from pathlib import Path

import moderngl_window
from moderngl_window.resources import programs
from moderngl_window import geometry
from moderngl_window import resources
from moderngl_window.finders.program import FilesystemFinder

# Register system resource directory in this package
resources.register_dir(
    Path(__file__).parent / 'resources'
)


class ShaderToyWindow(moderngl_window.WindowConfig):
    title = "Python Shadertoy"
    resource_dir = Path(__file__).parent
    # Don't enforce a specific aspect ratio
    aspect_ratio = None
    main_program = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._main_program_mtime = 0
        self._main_program_path = FilesystemFinder().find(Path(self.main_program))
        self._main_program = None
        self.load_main_program()

        self._quad_fs = geometry.quad_fs()

        self._fallback_program = self.load_program('shadertoy/programs/fallback.glsl')
        self._error_state = False
        self._mouse_pos = 0, 0

    @classmethod
    def run(cls):
        moderngl_window.run_window_config(cls)

    def render(self, time, frame_time):
        self.check_reload()

        if self._error_state:
            self._quad_fs.render(self.fallback_program)
            return

        # Set standard shadertoy uniforrms
        self.set_uniform('iTime', time)
        self.set_uniform('iMouse', self._mouse_pos)
        self.set_uniform(
            'iResolution',
            (self.wnd.buffer_size[0], self.wnd.buffer_size[1]),
        )

        # Run the program
        self._quad_fs.render(self._main_program)

    def set_uniform(self, name, value):
        """Safely set uniform value"""
        try:
            self._main_program[name].value = value
        except KeyError:
            pass
        except NameError:
            pass

    def check_reload(self, force=False):
        """Check if the file has changed"""

        # FIXME: While this works fairly well on all platforms
        #        it's overkill to stat the file every frame.
        mtime = self._main_program_path.stat().st_mtime

        if self._main_program_mtime < mtime:
            print("Reloading program...")
            self._main_program_mtime = mtime
            self.load_main_program()

    def load_main_program(self, force=False):
        try:
            new_program = self.load_program(self._main_program_path.parts[-1])
        except Exception as ex:
            self._error_state = True
            print(ex)
            return

        if self._main_program:
            self._main_program.release()

        self._main_program = new_program
        self._error_state = False

    def key_event(self, key, action, modifiers):
        keys = self.wnd.keys

    def mouse_drag_event(self, x, y, dx, dy):
        self._mouse_pos = x, y
