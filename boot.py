# This file is executed on every boot (including wake-boot from deepsleep)
import sys
sys.path[1] = '/flash/lib'
from m5stack import lcd, speaker, buttonA, buttonB, buttonC
import uos
uos.chdir('/flash')

# ---------- M5Cloud ------------

if buttonB.isPressed():
	import Sync
	Sync.main()
else:
	lcd.println('On: OFF-LINE Mode', color=lcd.ORANGE)
