from st3m.application import Application, ApplicationContext
from st3m.input import InputState
from st3m.input import InputController
from st3m.run import run_view
from .constants import *

from ctx import Context
import sys_display
import bl00mbox
import leds
import math
import os


class SalzApp(Application):
    def __init__(self, app_ctx: ApplicationContext) -> None:
        super().__init__(app_ctx)
        self.input = InputController()
        self.rot, self.flag_id, self.picture_id, self.brightness = 0, 0, 0, 100
        self.petal_last_frame = [False] * 10
        files = os.listdir(PATH)
        self.img_files = [PATH + p for p in files if p.endswith(".png") or p.endswith(".jpg")]
        self.audio_files = [self.blm.new(bl00mbox.patches.sampler, PATH + p) for p in files if p.endswith(".wav")]

    def update_leds(self):
        colors = COLORS[self.flag_id]
        for i in range(NR_LEDS):  # set flag
            i_led = int(i + self.rot * NR_LEDS) % NR_LEDS
            i_color = int(i / NR_LEDS * len(colors))
            leds.set_rgb(i_led, *colors[i_color])
        leds.update()
        leds.set_brightness(self.brightness)  # max: 255
        sys_display.set_backlight(int(self.brightness / 2.5))  # max: 100

    def update_debounce_petals(self, petals):
        for i in range(len(petals)):
            if petals[i].pressure > 0 and not self.petal_last_frame[i]:
                if i < len(self.audio_files):
                    self.audio_files[i].signals.trigger.start()
            self.petal_last_frame[i] = petals[i].pressure > 0  # debouncing

    def update_rot(self, gyro):
        rot = -(math.atan2(gyro[1], gyro[0]) / math.pi / 2) % 1
        if 0.2 < (abs(self.rot - rot) % 1) < 0.8:
            return
        self.rot = rot

    def update_buttons(self, ins):
        if abs(ins.buttons.os) == 1:
            self.brightness += ins.buttons.os  # left: -1, right: 1, pressed: 2
            self.brightness = max(0, min(255, self.brightness))
        if self.input.buttons.app.left.pressed:  # debounced by InputController
            self.flag_id = (self.flag_id - 1) % len(COLORS)  # rotate flags
        if self.input.buttons.app.right.pressed:
            self.picture_id = (self.picture_id - 1) % len(self.img_files)  # rotate image

    def think(self, ins: InputState, delta_ms: int) -> None:
        super().think(ins, delta_ms)
        self.update_rot(ins.imu.acc)
        self.update_leds()
        self.update_debounce_petals(ins.captouch.petals)
        self.update_buttons(ins)

    def draw(self, ctx: Context) -> None:
        ctx.rgb(0, 0, 0).rectangle(-120, -120, 240, 240).fill()
        if not self.img_files: return  # noqa
        ctx.rotate(self.rot * math.pi * 2)
        ctx.translate(-120, -120)
        try:
            path = self.img_files[self.picture_id]
            ctx.image(path, 0, 0, 240, 240)
        except: pass  # noqa


if __name__ == "__main__":
    run_view(SalzApp(ApplicationContext()))
