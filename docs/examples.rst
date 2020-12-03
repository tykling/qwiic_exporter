Examples
========

An example of the metrics exported with a single VCNL4040 proximity sensor attached: 

    # HELP qwiic_build_info Information about the qwiic_exporter itself.
    # TYPE qwiic_build_info gauge
    qwiic_build_info{pyserial_version="3.5",version="0.1.0-dev"} 1.0
    # HELP qwiic_accelerometer_x_gs Accelration on the X axis in gs
    # TYPE qwiic_accelerometer_x_gs gauge
    qwiic_accelerometer_x_gs{sensor="ICM-20948 IMU",sensorindex="1",subsensor="Accelerometer"} -20510.0
    # HELP qwiic_accelerometer_y_gs Accelration on the Y axis in gs
    # TYPE qwiic_accelerometer_y_gs gauge
    qwiic_accelerometer_y_gs{sensor="ICM-20948 IMU",sensorindex="1",subsensor="Accelerometer"} 249020.0
    # HELP qwiic_accelerometer_z_gs Accelration on the Z axis in gs
    # TYPE qwiic_accelerometer_z_gs gauge
    qwiic_accelerometer_z_gs{sensor="ICM-20948 IMU",sensorindex="1",subsensor="Accelerometer"} 992680.0
    # HELP qwiic_gyroscope_x_degrees Gyroscope X axis degrees per second
    # TYPE qwiic_gyroscope_x_degrees gauge
    qwiic_gyroscope_x_degrees{sensor="ICM-20948 IMU",sensorindex="1",subsensor="Gyro"} -2.85
    # HELP qwiic_gyroscope_y_degrees Gyroscope Y axis degrees per second
    # TYPE qwiic_gyroscope_y_degrees gauge
    qwiic_gyroscope_y_degrees{sensor="ICM-20948 IMU",sensorindex="1",subsensor="Gyro"} 1.73
    # HELP qwiic_gyroscope_z_degrees Gyroscope Z axis degrees per second
    # TYPE qwiic_gyroscope_z_degrees gauge
    qwiic_gyroscope_z_degrees{sensor="ICM-20948 IMU",sensorindex="1",subsensor="Gyro"} 0.81
    # HELP qwiic_magnetometer_x_teslas Magnetometer X axis teslas
    # TYPE qwiic_magnetometer_x_teslas gauge
    qwiic_magnetometer_x_teslas{sensor="ICM-20948 IMU",sensorindex="1",subsensor="Magnetometer"} -21450000.0
    # HELP qwiic_magnetometer_y_teslas Magnetometer Y axis teslas
    # TYPE qwiic_magnetometer_y_teslas gauge
    qwiic_magnetometer_y_teslas{sensor="ICM-20948 IMU",sensorindex="1",subsensor="Magnetometer"} -33150000.0
    # HELP qwiic_magnetometer_z_teslas Magnetometer Z axis teslas
    # TYPE qwiic_magnetometer_z_teslas gauge
    qwiic_magnetometer_z_teslas{sensor="ICM-20948 IMU",sensorindex="1",subsensor="Magnetometer"} -19650000.0
    # HELP qwiic_temperature_degrees Temperature in degrees celcius
    # TYPE qwiic_temperature_degrees gauge
    qwiic_temperature_degrees{sensor="ICM-20948 IMU",sensorindex="1",subsensor="Temperature"} 31.0
    # HELP qwiic_proximity The output of the proximity sensor (higher value=object closer)
    # TYPE qwiic_proximity gauge
    qwiic_proximity{sensor="VCNL4040 proximity sensor",sensorindex="2",subsensor="Proximity"} 1.0
    # HELP qwiic_light_lux The ambient light in Lux
    # TYPE qwiic_light_lux gauge
    qwiic_light_lux{sensor="VCNL4040 proximity sensor",sensorindex="2",subsensor="Ambient Light"} 123.0
    # HELP qwiic_output_hertz The actual frequency of output from OpenLog Artemis in hertz
    # TYPE qwiic_output_hertz gauge
    qwiic_output_hertz{sensor="OpenLog Artemis",sensorindex="3",subsensor="Frequency"} 1.5

Read on for changelog.
