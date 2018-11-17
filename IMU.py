def main():
    from m5stack import lcd, buttonA
    from alib.mpu6050 import MPU6050
    from time import sleep_ms
    from machine import I2C

    
    # lcd.font(lcd.FONT_Small, transparent=True, fixedwidth=False)
    i2c = I2C(sda = 21, scl = 22, speed=400000)

    try:
        # lcd.println('I2C port has been used.')
        
        imu = MPU6050(i2c)

        lcd.clear()
        lcd.setColor(lcd.WHITE)
        lcd.font(lcd.FONT_Small, transparent=False)

        while not buttonA.isPressed():
            accel = imu.acceleration
            gyro = imu.gyro
            # mag = imu.magnetic
            # print("ACCEL:  {:8.3f}   {:8.3f}   {:8.3f}".format(accel[0], accel[1], accel[2]))
            # print("GYRO:   {:8.3f}   {:8.3f}   {:8.3f}".format(gyro[0], gyro[1], gyro[2]))
            # print("MAG:    {:8.3f}   {:8.3f}   {:8.3f}".format(mag[0], mag[1], mag[2]))
            # print('')
            lcd.print("ACCEL: {:+7.2f}  {:+7.2f}  {:+7.2f}".format(accel[0], accel[1], accel[2]), lcd.CENTER, 20)
            lcd.print("GYRO:  {:+7.2f}  {:+7.2f}  {:+7.2f}".format(gyro[0], gyro[1], gyro[2]), lcd.CENTER, 40)
            # lcd.print("MAG:   {:+7.2f}  {:+7.2f}  {:+7.2f}".format(mag[0], mag[1], mag[2]), lcd.CENTER, 60)
            sleep_ms(10)

        lcd.print('Exit.', 0, 100)
    except:
        print('ERR')
    i2c.deinit()

if __name__ == '__main__':
	main()