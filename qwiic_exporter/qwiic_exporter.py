"""QwiicExporter v0.2.0 module.

Source code available at https://github.com/tykling/qwiic_exporter/
Can be installed from PyPi https://pypi.org/project/qwiic_exporter/
Read more at https://qwiic-exporter.readthedocs.io/en/latest/
"""
import argparse
import itertools
import logging
import time
import typing

import prometheus_client  # type: ignore
import serial  # type: ignore

__version__ = "0.2.0"
logger = logging.getLogger("qwiic_exporter.%s" % __name__)


class QwiicExporter:
    """The QwiicExporter class."""

    # each element in the sensors dict is itself a dict of the subsensors of that sensor,
    # as defined in the sensor unit documentation on
    # https://github.com/sparkfun/OpenLog_Artemis/blob/master/SENSOR_UNITS.md
    sensors: typing.Dict[
        str, typing.Dict[str, typing.List[typing.Tuple[str, str, str, float]]]
    ] = {
        "BME280 atmospheric sensor": {
            "Pressure": [
                (
                    "pressure_Pa",
                    "qwiic_pressure_pascals",
                    "The ambient pressure in pascals",
                    1,
                ),
            ],
            "Humidity": [
                (
                    "humidity_%",
                    "qwiic_humidity_percent",
                    "The relative humidity in percent",
                    1,
                ),
            ],
            "Altitude": [
                ("altitude_m", "qwiic_altitude_meters", "The altitude in meters", 1),
            ],
            "Temperature": [
                (
                    "temp_degC",
                    "qwiic_temperature_degrees",
                    "The temperature in degrees celcius",
                    1,
                ),
            ],
        },
        "CCS811 air quality sensor": {
            "TVOC": [
                (
                    "tvoc_ppb",
                    "qwiic_tvoc_ppb",
                    "TVOC (Total Volatile Organic Compounds) parts per billion",
                    1,
                ),
            ],
            "CO2": [
                ("co2_ppm", "qwiic_co2_ppm", "CO² parts per million", 1),
            ],
        },
        "ICM-20948 IMU": {
            "Accelerometer": [
                # sensor reads in milli g so divide by 1000 to get g
                (
                    "aX",
                    "qwiic_accelerometer_x_gs",
                    "Accelration on the X axis in gs",
                    0.001,
                ),
                (
                    "aY",
                    "qwiic_accelerometer_y_gs",
                    "Accelration on the Y axis in gs",
                    0.001,
                ),
                (
                    "aZ",
                    "qwiic_accelerometer_z_gs",
                    "Accelration on the Z axis in gs",
                    0.001,
                ),
            ],
            "Gyro": [
                (
                    "gX",
                    "qwiic_gyroscope_x_degrees",
                    "Gyroscope X axis degrees per second",
                    1,
                ),
                (
                    "gY",
                    "qwiic_gyroscope_y_degrees",
                    "Gyroscope Y axis degrees per second",
                    1,
                ),
                (
                    "gZ",
                    "qwiic_gyroscope_z_degrees",
                    "Gyroscope Z axis degrees per second",
                    1,
                ),
            ],
            "Magnetometer": [
                # sensor reads in micro teslas so divide by 1000000 to get teslas
                (
                    "mX",
                    "qwiic_magnetometer_x_teslas",
                    "Magnetometer X axis teslas",
                    0.000001,
                ),
                (
                    "mY",
                    "qwiic_magnetometer_y_teslas",
                    "Magnetometer Y axis teslas",
                    0.000001,
                ),
                (
                    "mZ",
                    "qwiic_magnetometer_z_teslas",
                    "Magnetometer Z axis teslas",
                    0.000001,
                ),
            ],
            "Temperature": [
                (
                    "imu_degC",
                    "qwiic_temperature_degrees",
                    "Temperature in degrees celcius",
                    1,
                ),
            ],
        },
        "MS8607 PHT sensor": {
            "Humidity": [
                (
                    "humidity_%",
                    "qwiic_humidity_percent",
                    "The relative humidity in percent",
                    1,
                ),
            ],
            "Pressure": [
                # sensor reading is in hectoPascals so multiply by 100 to get pascals
                ("hPa", "qwiic_pressure_pascals", "The pressure in pascals", 100),
            ],
            "Temperature": [
                (
                    "degC",
                    "qwiic_temperature_degrees",
                    "The temperature in degrees celcius",
                    1,
                ),
            ],
        },
        "OpenLog Artemis": {
            "Frequency": [
                (
                    "output_Hz",
                    "qwiic_output_hertz",
                    "The actual frequency of output from OpenLog Artemis in hertz",
                    1,
                ),
            ],
            "Counter": [
                (
                    "count",
                    "qwiic_measurements_total",
                    "The number of measurements made by OpenLog Artemis in hertz",
                    1,
                ),
            ],
        },
        "VCNL4040 proximity sensor": {
            "Proximity": [
                (
                    "prox(no unit)",
                    "qwiic_proximity",
                    "The output of the proximity sensor (higher value=object closer)",
                    1,
                ),
            ],
            "Ambient Light": [
                ("ambient_lux", "qwiic_light_lux", "The ambient light in Lux", 1),
            ],
        },
    }
    serialport: str
    prompath: str

    def __init__(self) -> None:
        """Find all possible sensor signatures with the current sensor config."""
        logger.debug("Getting sensor signature lookup table...")
        self.signatures = self.get_sensor_signature_lookup_table()
        logger.debug("Initiating Prometheus collector registry...")
        self.registry = prometheus_client.CollectorRegistry()

        # qwiic_build_info
        build_info = prometheus_client.Info(
            "qwiic_build",
            "Information about the qwiic_exporter itself.",
            registry=self.registry,
        )
        build_info.info(
            {"version": __version__, "pyserial_version": serial.__version__}
        )

    def initialise_serial(self) -> None:
        """Open serial port."""
        self.serial = serial.Serial(self.serialport, 115200, timeout=1)

    def get_sensor_signature_lookup_table(self) -> typing.Dict[str, str]:
        """Loop over sensors dict and get possible sensor signatures for all combinations of enabled subsensors.

        Args:
            sensors: dict of sensors

        Returns: A dict of signature: sensorname elements
        """
        logger.debug("Creating (sub)sensor signature lookup table...")
        signatures = {}
        for name, data in self.sensors.items():
            logger.debug(f"Getting subsensor signatures for sensor '{name}' ...")
            for signature in self.get_subsensor_signatures(data):
                signatures[",".join(signature)] = name
        logger.debug(f"Done. Returning {len(signatures)} signatures...")
        return signatures

    @staticmethod
    def get_subsensor_signatures(
        sensor: typing.Dict[str, typing.List[typing.Tuple[str, str, str, float]]]
    ) -> typing.List[typing.List[str]]:
        """Loop over subsensors for the sensor, and return a list of all possible combinations of subsensor signatures.

        Args:
            sensor: A dict of subsensors for this sensor. Each element has the sensor name as key
                    and as value a list of tuples of (spark_metric, prom_metric, desc, multiplier),
                    where spark_metric is the name of the metric in the output from the sensor,
                    prom_metric is the metric name in the prometheus output, desc is the description
                    of the metric for prometheus, and multiplier (optional) is the number to multiply
                    the sensor reading with before sending the data to prometheus.

        Returns: A list of all signatures it is possible to encounter with this sensor. If a
                 sensor has three subsensors with metrics a, b, and c, and each can be enabled or not,
                 then there is a total of 7 possible combinations: a,b,c; a,b; a,c; b,c; a; b; and c.
        """
        subsensor_signatures = []
        signatures = []
        logger.debug("Looping over subsensors to find the signature for each...")
        for subsensor, metrics in sensor.items():
            signature = ",".join([metric[0] for metric in metrics])
            logger.debug(f"Found subsensor signature: {signature}")
            subsensor_signatures.append(signature)

        logger.debug("Finding all valid combinations of subsensors for this sensor...")
        for i in reversed(range(len(subsensor_signatures))):
            for y in itertools.combinations(subsensor_signatures, i + 1):
                signatures.append(list(y))

        logger.debug(
            f"Done. Found {len(signatures)} possible signatures for this sensor."
        )
        return signatures

    def get_subsensor_signature(
        self, sensorname: str, subsensorname: str
    ) -> typing.List[str]:
        """Return the signature of the metrics in the subsensor.

        A subsensor can have multiple metrics. The signature for a sensor with three
        metrics could be ["aX", "aY", "aZ"].

        Args:
            sensorname: The name of the sensor
            subsensorname: The name of the subsensor

        Returns: A list of the elements of the subsensor signature.
        """
        return [x[0] for x in self.sensors[sensorname][subsensorname]]

    def parse_sensor_config(self, headerline: str) -> None:
        """Parse the help/header line with all the unit definitions and set self.sensorconfig."""
        self.sensorconfig: typing.List[typing.Tuple[str, typing.List[str]]] = []
        # gaugeindex is a list of tuples of (sensorname, sensorindex, subsensorname, metricname, Gauge obj)
        self.gaugeindex: typing.List[
            typing.Tuple[str, int, str, str, float, prometheus_client.Gauge]
        ] = []
        headerlist = headerline.split(",")
        # skip date and time and empty elements
        headerlist = headerlist[2:]
        headerlist = [x for x in headerlist if x not in ["", "\r\n"]]

        # loop as long as we still have unidentified header elements
        while headerlist:
            match = False
            # try longest first, we want to match a whole sensor rather than just a subsensor if possible
            for i in reversed(range(0, len(headerlist) + 1)):
                signature = headerlist[0:i]
                sigstr = ",".join(signature)
                if sigstr in self.signatures:
                    sensorname = self.signatures[sigstr]
                    match = True
                    break

            # no matches found, one or more unknown sensors might be attached
            if not match:
                logger.error(
                    f"Unable to find a matching sensor for headerlist {headerlist} - bailing out"
                )
                return

            headerlist = headerlist[len(signature) :]

            logger.debug(
                f"Found signature matching sensor {sensorname} - finding enabled subsensors..."
            )
            self.sensorconfig.append((sensorname, []))
            for subsensorname in self.sensors[sensorname].keys():
                subsig = self.get_subsensor_signature(sensorname, subsensorname)
                for i in range(0, len(signature)):
                    candidate = signature[i : len(subsig)]
                    if subsig == candidate:
                        signature = signature[len(subsig) :]
                        logger.debug(
                            f"Sensor {sensorname} has subsensor {subsensorname} enabled (signature {subsig}), creating metrics..."
                        )
                        self.sensorconfig[-1][1].append(subsensorname)
                        metrics = self.sensors[sensorname][subsensorname]
                        for metric in metrics:
                            # do we already have a metric with this name?
                            # more than one sensor can export the same metric (like temperature_degrees),
                            # and we can also have more than one of the same sensor
                            if metric[1] not in self.registry._names_to_collectors:
                                prometheus_client.Gauge(
                                    metric[1],
                                    metric[2],
                                    ["sensor", "sensorindex", "subsensor"],
                                    registry=self.registry,
                                )
                            # add this to the gaugeindex
                            self.gaugeindex.append(
                                (
                                    sensorname,
                                    len(self.sensorconfig),
                                    subsensorname,
                                    metric[1],
                                    metric[3],
                                    self.registry._names_to_collectors[metric[1]],
                                )
                            )

                        # The subsensor signature has been removed from the signature,
                        # and all metrics for this subsensor have Gauges,
                        # continue with the next subsensor for this sensor
                        break

    def trigger_header_line(self) -> None:
        """Send newline to open the menu, sleep 1 second, then send "h" to see headers."""
        self.serial.write(b"\n")
        time.sleep(1)
        self.serial.write(b"h")

    def ingest_data(self, data: str) -> None:
        """Parse a line of sensor data and update all the prometheus metrics."""
        # remove trailing comma, split into a list, skip date and timestamp
        readings = data.strip(",").split(",")[2:]

        # make sure we have the number of metrics we expect
        if len(self.gaugeindex) != len(readings):
            logger.error(
                f"Gauge index is out of sync (index has {len(self.gaugeindex)} metrics, reading has {len(readings)} metrics), getting new headers"
            )
            self.trigger_header_line()
            return

        # loop over readings and gauges and update each
        # gauge is a tuple of
        for gauge, reading in zip(self.gaugeindex, readings):
            # gauge is a tuple of (sensorname, sensorindex, subsensorname, metricname, multiplier, and Gauge object)
            gauge[5].labels(
                sensor=gauge[0], sensorindex=gauge[1], subsensor=gauge[2]
            ).set(float(reading) * gauge[4])
            logger.debug(f"Set gauge {gauge[3]} to {float(reading) * gauge[4]}")

    def write_textfile_collector_file(self) -> None:
        """Write metrics to the textfile collector path."""
        prometheus_client.write_to_textfile(self.prompath, self.registry)

    def disco(self) -> None:
        """Do stuff."""
        logger.debug(f"Initialising serial port {self.serialport} ...")
        self.initialise_serial()
        self.trigger_header_line()

        while True:
            try:
                reading = self.serial.readline().decode("ASCII").strip().strip(",")
            except UnicodeDecodeError:
                # skip random serial line noise
                continue

            logger.debug(f"Got line: {reading}")

            # detect reboots
            if reading[0 : len("Artemis OpenLog")] == "Artemis OpenLog":
                # reboot detected, check sensor config
                self.trigger_header_line()
                continue

            # detect header line
            if reading[0:15] == "rtcDate,rtcTime":
                logger.debug("Header line detected, parsing sensor config...")
                self.parse_sensor_config(headerline=reading)
                continue
            #
            # we can only ingest data after we've seen the header line and created metrics
            if hasattr(self, "gaugeindex"):
                self.ingest_data(data=reading)
                self.write_textfile_collector_file()
                continue


def get_parser() -> argparse.ArgumentParser:
    """Create and return the argparse object.

    Args: None
    Returns: The argparse object
    """
    parser = argparse.ArgumentParser(
        description=f"qwiic_exporter version {__version__}. Exports metrics from SparkFun OpenLog Artemis sensors to Prometheus node_exporter textfile collector path."
    )

    parser.add_argument(
        "SERIALPORT",
        type=str,
        help="The path to the serial port where the SparkFun OpenLog Artemis is connected.",
    )

    parser.add_argument(
        "PROMPATH",
        type=str,
        help="The path to the Prometheus node_exporter textfile collector file to write output to. Remember the .prom suffix.",
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_const",
        dest="loglevel",
        const="DEBUG",
        help="Debug mode. Equal to setting --log-level=DEBUG.",
        default=argparse.SUPPRESS,
    )

    parser.add_argument(
        "-l",
        "--log-level",
        dest="loglevel",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level. One of DEBUG, INFO, WARNING, ERROR, CRITICAL. Defaults to INFO.",
        default="INFO",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_const",
        dest="loglevel",
        const="WARNING",
        help="Quiet mode. No output at all if no errors are encountered. Equal to setting --log-level=WARNING.",
        default=argparse.SUPPRESS,
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s version {__version__}",
        help="Show qwiic_exporter version and exit.",
    )

    return parser


def main() -> None:
    """Get args, initialise QwiicExporter object, and start the loop.

    Args: None
    Returns: None
    """
    # get argparse object and parse args
    parser = get_parser()
    args = parser.parse_args()

    # define the log format used for stdout depending on the requested loglevel
    if args.loglevel == "DEBUG":
        console_logformat = "%(asctime)s %(levelname)s qwiic_exporter.%(funcName)s():%(lineno)i:  %(message)s"
    else:
        console_logformat = "%(asctime)s %(levelname)s qwiic_exporter %(message)s"

    # configure the log format used for console
    logging.basicConfig(
        level=getattr(logging, str(args.loglevel)),
        format=console_logformat,
        datefmt="%Y-%m-%d %H:%M:%S %z",
    )

    qwe = QwiicExporter()
    qwe.serialport = args.SERIALPORT
    qwe.prompath = args.PROMPATH
    qwe.disco()


def init() -> None:
    """Call the main() function if being invoked as a script. This is here just as a testable way of calling main()."""
    if __name__ == "__main__":
        main()


# call init(), which then calls main() when needed
init()
