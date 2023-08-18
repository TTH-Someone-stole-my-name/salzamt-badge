from st3m.application import Application, ApplicationContext
from ctx import Context
import uos
import leds
import math
import os

class SalzamtNickApp(Application):
    PROFILES_DIR = f'/sd/salzamt'

    def get_profiles(self):
        try:
            os.mkdir(self.PROFILES_DIR)
        except OSError:
            # May already exist, we don't care
            pass
        return os.listdir(self.PROFILES_DIR)

    def __init__(self, app_ctx: ApplicationContext) -> None:
        super().__init__(app_ctx)
        self._selected_profile=0
        self._selected_flag=0
        self._offset=0
        self._rotate=False
        self._spin=False
        self._pulse=False
        self._pulse_inc=True
        self._pulse_by=7
        self._ironman=False
        self._cthulhu=False
        self._picture=0
        self._petal_states = [0]*10
        self._petal_pressed = [False]*10
        self._angle = 0
        self.time = 0
        self.rotation = 0
        self.debug=[]
        for i in range(0, 10):
            self._petal_states[i] = 0
            self._petal_pressed[i] = False
        leds.set_brightness(32)

        self._flags = self.init_flags()

    def init_flags(self):
        red=(255,0,0)
        white=(255,255,255)
        yellow=(255,255,0)
        black=(10,10,10)
        # Draw Austrian flag
        AT=[]
        AT=[white]*40
        # TOP
        for i in range(0,9):
            AT[i]=red
        for i in range(32,40):
            AT[i]=red
        # MID
        for i in range(9,17):
            AT[i]=white
        for i in range(24,32):
            AT[i]=white
        # BOT
        for i in range(17,25):
            AT[i]=red
        DE=[]
        DE=[white]*40
        # TOP
        for i in range(0,9):
            DE[i]=black
        for i in range(32,40):
            DE[i]=black
        # MID
        for i in range(9,17):
            DE[i]=red
        for i in range(24,32):
            DE[i]=red
        # BOT
        for i in range(17,25):
            DE[i]=yellow
        # Draw AustrianHungarian flag
        ATHU=[]
        ATHU=[white]*40
        # TOP
        for i in range(0,9):
            ATHU[i]=yellow
        for i in range(32,40):
            ATHU[i]=yellow
        # MID
        for i in range(9,17):
            ATHU[i]=black
        for i in range(24,32):
            ATHU[i]=black
        for i in range(17,25):
            ATHU[i]=black
        return [ AT, ATHU, DE ]

    def pulse(self, brightness):
        if self._pulse_inc:
            brightness = brightness + self._pulse_by
        else:
            brightness = brightness - self._pulse_by
        if brightness <= 0:
            self._pulse_inc = not self._pulse_inc
            return 0
        if brightness >= 255:
            self._pulse_inc = not self._pulse_inc
            return 255
        return brightness

    def toggle_pulse(self):
        self._pulse=not self._pulse
        if self._pulse:
            self._pulse_inc=True
            self._pulse_by=5
            leds.set_brightness(0)

    def set_ironman(self):
        self._flag = None
        self._ironman = True
        self._cthulhu = False

    def set_cthulhu(self):
        self._flag = None
        self._ironman = False
        self._cthulhu = True

    def set_flag(self):
        self._selected_flag = (self._selected_flag + 1) % len(self._flags)
        self._flag = self._flags[self._selected_flag]
        self._ironman = False
        self._cthulhu = False

    # Debounce switch
    def update_petals(self, petals):
        for i in range(0, 10):
            if self._petal_states[i] == 0 and petals[i].pressure > 0:
               self._petal_states[i] = 1
               self._petal_pressed[i] = True
            elif (self._petal_states[i] == 1 or self._petal_states[i] == 2) and petals[i].pressure > 0:
               self._petal_states[i] = 2
               self._petal_pressed[i] = False
            elif self._petal_states[i] == 2 and petals[i].pressure == 0:
               self._petal_states[i] = 3
               self._petal_pressed[i] = False
            elif self._petal_states[i] == 3 and petals[i].pressure == 0:
               self._petal_states[i] = 0
               self._petal_pressed[i] = False

    def draw(self, ctx: Context) -> None:
        # Paint the background black
        ctx.rgb(0, 0, 0).rectangle(-120, -120, 240, 240).fill()
        # Rotate the image around z axis
        if self._rotate: #or self._angle < 6.28:
            ctx.save()
            ctx.rotate(self._angle)
        # Simulate rotation around y axis (it's a 2D graphics context)
        if self._spin:
            ctx.save()
            ctx.scale(abs(math.cos(self._angle)) , 1)

        # Needed for correct origin for above translations.
        ctx.translate(-120,-120)

        # Load picture, fall back on profile picture
        try:
            path=self.PROFILES_DIR + '/' + self.get_profiles()[self._selected_profile]
            uos.stat(path)

            ctx.image(path, 0, 0, 241, 241)
        except OSError:
            ctx.image(f"/flash/profile.png", 0, 0, 241, 241)
        if self._rotate or self._spin:
            ctx.restore()
        # colorful petals
        if self._pulse:
            leds.set_brightness(self.pulse(leds.get_brightness()))
        flag = self._flags[self._selected_flag]

        if flag != None:
            if self._rotate:
                for i in range(40):
                    leds.set_rgb((self._offset + i) % 40, *flag[i])
                self._offset += 1
            else:
                for i in range(40):
                    leds.set_rgb(i, *flag[i])
        # Effects:
        if self._ironman:
            for i in range(40):
                leds.set_rgb(i,170,255,255)
        if self._cthulhu:
            for i in range(40):
                leds.set_rgb(i,0,255,0)
        leds.update()

    def think(self, ins: InputState, delta_ms: int) -> None:
        super().think(ins, delta_ms)
        # zeroth element being the pad closest to the USB port. Then, every other pad in a clockwise direction.
        # Pads 0, 2, 4, 6, 8 are Top pads.
        # Pads 1, 3, 5, 7, 9 are Bottom pads.
        self.update_petals(self.input.captouch.petals)
        if self._petal_pressed[0]:
            self._rotate = not self._rotate
            if self._rotate:
                self._angle=0
        elif self._rotate or self._spin:
            self._angle= (self._angle + math.radians(0.5)) % (math.pi * 2)
        if self._petal_pressed[1]:
            self.toggle_pulse()
        # Profile down
        if self._petal_pressed[2]:
            if self._selected_profile <= 0:
                self._selected_profile = len(self.get_profiles()) - 1
            else:
                self._selected_profile -= 1
        # Profile up
        if self._petal_pressed[3]:
            self._selected_profile = (self._selected_profile + 1) % len(self.get_profiles())
        if self._petal_pressed[4]:
            self._spin= not self._spin
        if self._petal_pressed[9]:
            self.set_ironman()
        if self._petal_pressed[8]:
            self.set_flag()
        if self._petal_pressed[7]:
            self.set_cthulhu()

# For running with `mpremote run`:
if __name__ == "__main__":
    import st3m.run

    st3m.run.run_view(SalzamtNickApp(ApplicationContext()))

