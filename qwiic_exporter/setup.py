# type: ignore
"""QwiicExporter setup.py for setuptools.

Source code available at https://github.com/tykling/QwiicExporter/
Can be installed from PyPi https://pypi.org/project/QwiicExporter/
Read more at https://qwiicexporter.readthedocs.io/en/latest/
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="qwiic_exporter",
    version="0.1.0-dev",
    author="Thomas Steen Rasmussen",
    author_email="thomas@gibfest.dk",
    description="QwiicExpoter is a Prometheus exporter for SparkFun QWIIC sensor shield Artemis OpenLog.",
    license="BSD License",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tykling/QwiicExporter",
    packages=["qwiic_exporter"],
    entry_points={
        "console_scripts": ["qwiic_exporter = qwiic_expoterl.qwiic_expoter:main"]
    },
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=["pyserial", "prometheus_client"],
    include_package_data=True,
)
