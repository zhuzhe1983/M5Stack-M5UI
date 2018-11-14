def main():
    from m5stack import lcd, buttonA
    from mpu9250 import MPU9250
    from time import sleep_ms
    from machine import I2C
    import network
    
	# lcd.font(lcd.FONT_Small, transparent=True, fixedwidth=False)

    try:
        sta_if = network.WLAN(network.STA_IF)
        if sta_if.active() == True:
            m_acc = network.mqtt('acc', 'mqtt://srdmobilex.ddns.net', port=65530, clientid='a')
            m_gyro = network.mqtt('gyro', 'mqtt://srdmobilex.ddns.net', port=65530, clientid='g')
            m_acc.start()
            m_gyro.start()
            m_acc.subscribe('acc', 2)
            m_gyro.subscribe('gyro', 0)

        i2c = I2C(sda = 21, scl = 22)
        
        imu = MPU9250(i2c)

        lcd.clear()
        lcd.setColor(lcd.WHITE)
        lcd.font(lcd.FONT_Small, transparent=False)

        counter = 0

        while not buttonA.isPressed():
            accel = imu.acceleration
            gyro = imu.gyro
            mag = imu.magnetic
            lcd.print("ACCEL: {:+7.2f}  {:+7.2f}  {:+7.2f}".format(accel[0], accel[1], accel[2]), lcd.CENTER, 20)
            lcd.print("GYRO:  {:+7.2f}  {:+7.2f}  {:+7.2f}".format(gyro[0], gyro[1], gyro[2]), lcd.CENTER, 40)
            lcd.print("MAG:   {:+7.2f}  {:+7.2f}  {:+7.2f}".format(mag[0], mag[1], mag[2]), lcd.CENTER, 60)
            if sta_if.active() == True:
                m_acc.publish('acc', '{:+7.2f},{:+7.2f},{:+7.2f}'.format(accel[0], accel[1], accel[2]) + '(%d)'%counter)
                m_gyro.publish('gyro', '{:+7.2f}  {:+7.2f}  {:+7.2f}'.format(gyro[0], gyro[1], gyro[2]) + '(%d)'%counter)
                counter += 1
            sleep_ms(20)

        m_acc.free()
        m_gyro.free()
        i2c.deinit()
        lcd.print('Exit.', 0, 100)
    except:
        return -1
