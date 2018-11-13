def main():
    from m5stack import lcd, buttonA
    from mpu9250 import MPU9250
    from time import sleep_ms
    from machine import I2C
    import os

    with open('/flash/timenow.txt', 'r') as o:
        t = int(o.read())
    FNAME_DATA = '/sd/ACC_%d.csv' % t

    try:
        i2c = I2C(sda = 21, scl = 22)
        # lcd.println('I2C port has been used.')
        
        imu = MPU9250(i2c)

        lcd.clear()
        lcd.setColor(lcd.WHITE)
        lcd.font(lcd.FONT_Small, transparent=False)

        i = 0
        buf = 'a0,a1,a2,g0,g1,g2,m0,m1,m2\n'
        lcd.print('Recording...')

        while not buttonA.isPressed():
            i += 1
            accel = imu.acceleration
            gyro = imu.gyro
            mag = imu.magnetic

            buf += ('%f,%f,%f,%f,%f,%f,%f,%f,%f\n' % (accel[0], accel[1], accel[2], gyro[0], gyro[1], gyro[2], mag[0], mag[1], mag[2]))
            if i == 10:
                with open(FNAME_DATA, 'a') as o:
                    o.write(buf)
                buf = ''
                i = 0
            # print("ACCEL:  {:8.3f}   {:8.3f}   {:8.3f}".format(accel[0], accel[1], accel[2]))
            # print("GYRO:   {:8.3f}   {:8.3f}   {:8.3f}".format(gyro[0], gyro[1], gyro[2]))
            # print("MAG:    {:8.3f}   {:8.3f}   {:8.3f}".format(mag[0], mag[1], mag[2]))
            # print('')
            # lcd.print("ACCEL: {:+7.2f}  {:+7.2f}  {:+7.2f}".format(accel[0], accel[1], accel[2]), lcd.CENTER, 20)
            # lcd.print("GYRO:  {:+7.2f}  {:+7.2f}  {:+7.2f}".format(gyro[0], gyro[1], gyro[2]), lcd.CENTER, 40)
            # lcd.print("MAG:   {:+7.2f}  {:+7.2f}  {:+7.2f}".format(mag[0], mag[1], mag[2]), lcd.CENTER, 60)
            sleep_ms(20)
            

        i2c.deinit()
        lcd.print('Exit.', 0, 100)
    except:
        pass
