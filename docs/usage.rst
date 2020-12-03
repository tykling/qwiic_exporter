Usage
=====

Until I get something better written here are the argparse usage instructions::

   $ qwiic_exporter -h
   usage: qwiic_exporter.py [-h] [-d] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                            [-q] [-v]
                            SERIALPORT PROMPATH

   qwiic_exporter version 0.3.0-dev. Exports metrics from SparkFun OpenLog
   Artemis sensors to Prometheus node_exporter textfile collector path.

   positional arguments:
     SERIALPORT            The path to the serial port where the SparkFun OpenLog
                           Artemis is connected.
     PROMPATH              The path to the Prometheus node_exporter textfile
                           collector file to write output to. Remember the .prom
                           suffix.

   optional arguments:
     -h, --help            show this help message and exit
     -d, --debug           Debug mode. Equal to setting --log-level=DEBUG.
     -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                           Logging level. One of DEBUG, INFO, WARNING, ERROR,
                           CRITICAL. Defaults to INFO.
     -q, --quiet           Quiet mode. No output at all if no errors are
                           encountered. Equal to setting --log-level=WARNING.
     -v, --version         Show qwiic_exporter version and exit.
   $

Read on for examples.
