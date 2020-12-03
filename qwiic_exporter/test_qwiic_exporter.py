# type: ignore
"""qwiic_exporter.py test suite.

Runs with pytest and tox.
"""
import logging

from qwiic_exporter import QwiicExporter


def test_get_sensor_signatures():
    """Make sure the get_sensor_signatures() method returns the expected signatures for known sensors."""
    qwe = QwiicExporter()
    for name, data in qwe.sensors.items():
        if name == "ICM-20948 IMU":
            assert qwe.get_subsensor_signatures(data) == [
                ["aX,aY,aZ", "gX,gY,gZ", "mX,mY,mZ", "imu_degC"],
                ["aX,aY,aZ", "gX,gY,gZ", "mX,mY,mZ"],
                ["aX,aY,aZ", "gX,gY,gZ", "imu_degC"],
                ["aX,aY,aZ", "mX,mY,mZ", "imu_degC"],
                ["gX,gY,gZ", "mX,mY,mZ", "imu_degC"],
                ["aX,aY,aZ", "gX,gY,gZ"],
                ["aX,aY,aZ", "mX,mY,mZ"],
                ["aX,aY,aZ", "imu_degC"],
                ["gX,gY,gZ", "mX,mY,mZ"],
                ["gX,gY,gZ", "imu_degC"],
                ["mX,mY,mZ", "imu_degC"],
                ["aX,aY,aZ"],
                ["gX,gY,gZ"],
                ["mX,mY,mZ"],
                ["imu_degC"],
            ]
        elif name == "BME280 atmospheric sensor":
            assert qwe.get_subsensor_signatures(data) == [
                ["pressure_Pa", "humidity_%", "altitude_m", "temp_degC"],
                ["pressure_Pa", "humidity_%", "altitude_m"],
                ["pressure_Pa", "humidity_%", "temp_degC"],
                ["pressure_Pa", "altitude_m", "temp_degC"],
                ["humidity_%", "altitude_m", "temp_degC"],
                ["pressure_Pa", "humidity_%"],
                ["pressure_Pa", "altitude_m"],
                ["pressure_Pa", "temp_degC"],
                ["humidity_%", "altitude_m"],
                ["humidity_%", "temp_degC"],
                ["altitude_m", "temp_degC"],
                ["pressure_Pa"],
                ["humidity_%"],
                ["altitude_m"],
                ["temp_degC"],
            ]
        elif name == "VCNL4040 proximity sensor":
            assert qwe.get_subsensor_signatures(data) == [
                ["prox(no unit)", "ambient_lux"],
                ["prox(no unit)"],
                ["ambient_lux"],
            ]
        elif name == "OpenLog Artemis":
            assert qwe.get_subsensor_signatures(data) == [
                ["output_Hz", "count"],
                ["output_Hz"],
                ["count"],
            ]
        elif name == "CCS811 air quality sensor":
            assert qwe.get_subsensor_signatures(data) == [
                ["tvoc_ppb", "co2_ppm"],
                ["tvoc_ppb"],
                ["co2_ppm"],
            ]
        elif name == "MS8607 PHT sensor":
            assert qwe.get_subsensor_signatures(data) == [
                ["humidity_%", "hPa", "degC"],
                ["humidity_%", "hPa"],
                ["humidity_%", "degC"],
                ["hPa", "degC"],
                ["humidity_%"],
                ["hPa"],
                ["degC"],
            ]
        else:
            assert (
                qwe.get_subsensor_signatures(data) is False
            ), "Unknown sensor, cannot test get_sensor_signatures()"


def test_parse_sensor_config():
    """Make sure the parse_sensor_config() function does the right thing with various headerlines.

    TODO: Also check gaugeindex here maybe.
    """
    qwe = QwiicExporter()

    # the full lineup
    qwe.parse_sensor_config(
        headerline="rtcDate,rtcTime,aX,aY,aZ,gX,gY,gZ,mX,mY,mZ,imu_degC,tvoc_ppb,co2_ppm,prox(no unit),ambient_lux,pressure_Pa,humidity_%,altitude_m,temp_degC,output_Hz,count,"
    )
    assert qwe.sensorconfig == [
        ("ICM-20948 IMU", ["Accelerometer", "Gyro", "Magnetometer", "Temperature"]),
        ("CCS811 air quality sensor", ["TVOC", "CO2"]),
        ("VCNL4040 proximity sensor", ["Proximity", "Ambient Light"]),
        (
            "BME280 atmospheric sensor",
            [
                "Pressure",
                "Humidity",
                "Altitude",
                "Temperature",
            ],
        ),
        ("OpenLog Artemis", ["Frequency", "Counter"]),
    ]
    for metric in qwe.sensors["ICM-20948 IMU"]["Accelerometer"]:
        assert metric[1] in qwe.registry._names_to_collectors

    for metric in qwe.sensors["ICM-20948 IMU"]["Gyro"]:
        assert metric[1] in qwe.registry._names_to_collectors

    for metric in qwe.sensors["ICM-20948 IMU"]["Magnetometer"]:
        assert metric[1] in qwe.registry._names_to_collectors

    for metric in qwe.sensors["ICM-20948 IMU"]["Temperature"]:
        assert metric[1] in qwe.registry._names_to_collectors

    # partial lineup
    qwe.parse_sensor_config(
        headerline="rtcDate,rtcTime,aX,aY,aZ,gX,gY,gZ,co2_ppm,prox(no unit),ambient_lux,pressure_Pa,humidity_%,altitude_m,output_Hz,"
    )
    assert qwe.sensorconfig == [
        ("ICM-20948 IMU", ["Accelerometer", "Gyro"]),
        ("CCS811 air quality sensor", ["CO2"]),
        ("VCNL4040 proximity sensor", ["Proximity", "Ambient Light"]),
        (
            "BME280 atmospheric sensor",
            [
                "Pressure",
                "Humidity",
                "Altitude",
            ],
        ),
        ("OpenLog Artemis", ["Frequency"]),
    ]

    # duplicate sensors
    qwe.parse_sensor_config(
        headerline="rtcDate,rtcTime,aX,aY,aZ,gX,gY,gZ,mX,mY,mZ,imu_degC,tvoc_ppb,co2_ppm,prox(no unit),ambient_lux,prox(no unit),ambient_lux,prox(no unit),ambient_lux,pressure_Pa,humidity_%,altitude_m,temp_degC,tvoc_ppb,co2_ppm,output_Hz,"
    )
    assert qwe.sensorconfig == [
        ("ICM-20948 IMU", ["Accelerometer", "Gyro", "Magnetometer", "Temperature"]),
        ("CCS811 air quality sensor", ["TVOC", "CO2"]),
        ("VCNL4040 proximity sensor", ["Proximity", "Ambient Light"]),
        ("VCNL4040 proximity sensor", ["Proximity", "Ambient Light"]),
        ("VCNL4040 proximity sensor", ["Proximity", "Ambient Light"]),
        (
            "BME280 atmospheric sensor",
            [
                "Pressure",
                "Humidity",
                "Altitude",
                "Temperature",
            ],
        ),
        ("CCS811 air quality sensor", ["TVOC", "CO2"]),
        ("OpenLog Artemis", ["Frequency"]),
    ]

    # nothing except hz enabled
    qwe.parse_sensor_config(headerline="rtcDate,rtcTime,output_Hz,")
    assert qwe.sensorconfig == [("OpenLog Artemis", ["Frequency"])]


class MockSerial:
    """A mock serial device."""

    def write(self, data):
        """Faked write method for writing data to serial device."""
        # print(f"written to MockSerial: {data}")
        pass


def test_ingest_data():
    """Make sure the ingest_data method works as expected."""
    qwe = QwiicExporter()
    qwe.serial = MockSerial()

    qwe.parse_sensor_config(
        headerline="rtcDate,rtcTime,aX,aY,aZ,gX,gY,gZ,mX,mY,mZ,imu_degC,tvoc_ppb,co2_ppm,prox(no unit),ambient_lux,pressure_Pa,humidity_%,altitude_m,temp_degC,output_Hz,count,"
    )
    qwe.ingest_data(
        data="01/07/2000,16:18:45.54,-638.67,153.32,782.23,-1.69,1.47,-0.42,21.45,37.80,-5.85,9.77,2,417,20,0,99500.64,53.06,152.98,6.32,1.00,2523,"
    )

    # check labels
    assert list(
        qwe.registry._names_to_collectors["qwiic_accelerometer_x_gs"]._samples()
    )[0][1] == {
        "sensor": "ICM-20948 IMU",
        "sensorindex": "1",
        "subsensor": "Accelerometer",
    }

    # check values
    assert (
        list(qwe.registry._names_to_collectors["qwiic_accelerometer_x_gs"]._samples())[
            0
        ][2]
        == -0.63867
    )
    assert (
        list(qwe.registry._names_to_collectors["qwiic_accelerometer_y_gs"]._samples())[
            0
        ][2]
        == 0.15331999999999998
    )
    assert (
        list(qwe.registry._names_to_collectors["qwiic_accelerometer_z_gs"]._samples())[
            0
        ][2]
        == 0.78223
    )

    assert (
        list(qwe.registry._names_to_collectors["qwiic_output_hertz"]._samples())[0][2]
        == 1.0
    )
    assert (
        list(qwe.registry._names_to_collectors["qwiic_measurements_total"]._samples())[
            0
        ][2]
        == 2523
    )


def test_ingest_data_wrong_metric_count(caplog):
    """Make sure the ingest_data() method does what it is supposed to when given a line of data with fewer elements than expected."""
    caplog.set_level(logging.DEBUG)
    qwe = QwiicExporter()
    qwe.serial = MockSerial()

    qwe.parse_sensor_config(
        headerline="rtcDate,rtcTime,aX,aY,aZ,gX,gY,gZ,mX,mY,mZ,imu_degC,tvoc_ppb,co2_ppm,prox(no unit),ambient_lux,pressure_Pa,humidity_%,altitude_m,temp_degC,output_Hz,count,"
    )
    qwe.ingest_data(
        data="01/07/2000,16:18:45.54,-638.67,153.32,782.23,-1.69,1.47,-0.42,21.45,37.80,-5.85,9.77,2,417,20,0,99500.64,53.06,152.98,6.32,1.00,"
    )
    assert "Gauge index is out of sync" in caplog.text
