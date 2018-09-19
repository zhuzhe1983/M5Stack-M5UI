def main():
    from m5stack import lcd, buttonA
    import time, machine
    try:
        rtc = machine.RTC()
        print("Synchronize time from NTP server ...")
        # lcd.println("Synchronize time from NTP server ...")
        rtc.ntp_sync(server="cn.ntp.org.cn")

        lcd.font(lcd.FONT_7seg, fixedwidth=True, dist=16, width=2)

        while not buttonA.isPressed():
            d = time.strftime("%Y-%m-%d", time.localtime())
            t = time.strftime("%H:%M:%S", time.localtime())
            lcd.print(d, lcd.CENTER, 50, lcd.ORANGE)
            lcd.print(t, lcd.CENTER, 130, lcd.ORANGE)
            time.sleep(1)
    except:
        pass
