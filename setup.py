import sys
from setuptools import setup
setup(
    name = "mstepcore_test_zmq",
    version = "0.1",
    packages = ["mstepcore_test_zmq", "mstepcore_test_zmq.modules"],
    package_data = {"mstepcore_test_zmq": ["default_config.json"]},
    entry_points = {"console_scripts": ["mstepcore_test_zmq = mstepcore_test_zmq.main:main"]},
    author = "Radoslav Pesek",
    author_email = "radoslav.pesek@microstep-mis.com",
    description = "Core app & modules using zeromq library",
    license = "proprietary",
    keywords = "zeromq",
    url = "",
)
