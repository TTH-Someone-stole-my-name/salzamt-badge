from st3m.application import Application, ApplicationContext
from ctx import Context
import uos
import leds
import math

class FancyNickApp(Application):
    def __init__(self, app_ctx: ApplicationContext) -> None:
        super().__init__(app_ctx)
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

        self._AT=[]
        red=(255,0,0)
        white=(255,255,255)
        self._AT=[white]*40
        self._AT[0]=red
        # TOP
        for i in range(0,9):
            self._AT[i]=red
        for i in range(32,40):
            self._AT[i]=red
        # MID
        for i in range(10,14):
            self._AT[i]=white
        for i in range(27,31):
            self._AT[i]=white
        for i in range(15,26):
            self._AT[i]=red
        self._flag = self._AT

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
        self._flag = self._AT
        self._ironman = False
        self._cthulhu = False

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
        # paint image
        img = None
        #ctx.text_align=ctx.CENTER
        #ctx.text_baseline=ctx.MIDDLE
        if self._rotate: #or self._angle < 6.28:
            ctx.save()
            ctx.rotate(self._angle)
        
        if self._spin: 
            ctx.save()
            ctx.scale(abs(math.cos(self._angle)) , 1)        

        ctx.translate(-120,-120)
        try:
            path=f"/flash/profile{self._picture}.png"
            uos.stat(path)

            img = ctx.image(path, 0, 0, 241, 241)

            #img = ctx.image(path, 0,0, -241, -241)
        except OSError:
            img = ctx.image(f"/flash/sys/apps/profile-pic/profile.png", -120, -120, 241, 241)
        if self._rotate or self._spin:
            ctx.restore()
        # colorful petals
        if self._pulse:
            leds.set_brightness(self.pulse(leds.get_brightness()))
        #end if
        flag = self._flag
        if flag != None:
            if self._rotate:
                for i in range(40):
                    leds.set_rgb((self._offset + i) % 40, flag[i][0], flag[i][1], flag[i][2])
                self._offset += 1
            else:
                for i in range(40):
                    leds.set_rgb(i, flag[i][0], flag[i][1], flag[i][2])
            #end if
        #end if
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
        #elif self._angle < 6.28:
        #    self._angle= (self._angle + math.radians(0.5)) % (math.pi * 2)
        if self._petal_pressed[1]:
            self.toggle_pulse()
        if self._petal_pressed[2]:
            self._picture=(self._picture+1) % 3
        if self._petal_pressed[4]:
            self._spin= not self._spin
        if self._petal_pressed[9]:
            self.set_ironman()
        if self._petal_pressed[8]:
            self.set_flag()
        if self._petal_pressed[7]:
            self.set_cthulhu()
        #print(math.cos(self._angle))

# For running with `mpremote run`:
if __name__ == "__main__":
    import st3m.run

    st3m.run.run_view(FancyNickApp(ApplicationContext()))

