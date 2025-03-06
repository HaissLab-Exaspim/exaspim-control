import copy, sys
from ruamel.yaml import YAML
from pathlib import Path
from voxel.instruments.instrument import Instrument
from threading import Lock, RLock
import inflection
import logging

from typing import Dict, Optional, Any

class PartialInstrument(Instrument):
    """Represents an instrument with various devices and configurations."""

    selected_device_types = []
    selected_daq_ports = []

    def __init__(self, log_level: str = "INFO"):
        """
        Initialize the Instrument class.

        :param config_path: Path to the configuration file.
        :type config_path: str
        :param yaml_handler: YAML handler for loading and dumping config, defaults to None.
        :type yaml_handler: YAML, optional
        :param log_level: Logging level, defaults to "INFO".
        :type log_level: str, optional
        """
        self.setup_logger(log_level)

        self.set_config()
        self.filter_out_config()
        self._construct()

    def setup_logger(self, log_level: str = "INFO"):

        logger = logging.getLogger()  # get the root logger.
        # Remove any handlers already attached to the root logger.
        logging.getLogger().handlers.clear()
        # logger level must be set to the lowest level of any handler.
        logger.setLevel(logging.DEBUG)
        fmt = "%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s"
        datefmt = "%Y-%m-%d,%H:%M:%S"
        log_formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
        log_handler = logging.StreamHandler(sys.stdout)
        log_handler.setLevel("INFO")
        log_handler.setFormatter(log_formatter)
        logger.addHandler(log_handler)

        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.log.setLevel(log_level)

    def filter_out_config(self):
        devices_to_remove = []
        for device_name, device_specs in self.config["instrument"]["devices"].items():
            if device_specs['type'] not in self.selected_device_types :
                devices_to_remove.append(device_name)
        for device_name in devices_to_remove :
            self.config["instrument"]["devices"].pop(device_name)
        
        for device_name, device_specs in self.config["instrument"]["devices"].items():
            if device_specs["type"] == "daq" :
                ports_to_remove = []
                ports = device_specs["properties"]["tasks"]["ao_task"]["ports"]
                for port_name, port_specs in ports.items() :
                    if port_name not in self.selected_daq_ports and port_specs["port"] not in self.selected_daq_ports :
                        ports_to_remove.append(port_name)
                for port_name in ports_to_remove :
                    device_specs["properties"]["tasks"]["ao_task"]["ports"].pop(port_name)


    def set_config(self):
        config_path = Path(__file__).parent.parent / "experimental" / "instrument.yaml"
        config = YAML().load(config_path)
        self.config = config
        self.config_path = config_path

    def grab_first(self, object_dict: dict) -> object:
        """
        Grab the first object from a dictionary.

        :param object_dict: Dictionary containing devices
        :type object_dict: dict
        :return: The first device in the dictionary
        :rtype: object
        """
        object_name = list(object_dict.keys())[0]
        return object_dict[object_name]
    
    def _construct(self) -> None:
        """
        Construct the instrument from the configuration file.

        :raises ValueError: If the instrument ID or device configurations are invalid.
        """
        # construct devices
        self.log.info(f"constructing partial instrument")
        for device_name, device_specs in self.config["instrument"]["devices"].items():
            self._construct_device(device_name, device_specs)
        self.channels = self.config["instrument"]["channels"]

    def _construct_device(self, device_name: str, device_specs: Dict[str, Any], lock: Optional[Lock] = None) -> None:
        """
        Construct a device based on its specifications.

        :param device_name: Name of the device.
        :type device_name: str
        :param device_specs: Specifications of the device.
        :type device_specs: dict
        :param lock: Lock for thread safety, defaults to None.
        :type lock: Lock, optional
        :raises ValueError: If the device configuration is invalid.
        """
        self.log.info(f"constructing {device_name}")
        lock = RLock() if lock is None else lock
        device_type = inflection.pluralize(device_specs["type"])
        driver = device_specs["driver"]
        module = device_specs["module"]
        init = device_specs.get("init", {})
        device_object = self._load_device(driver, module, init, lock)
        properties = device_specs.get("properties", {})
        self._setup_device(device_object, properties)

        # create device dictionary if it doesn't already exist and add device to dictionary
        if not hasattr(self, device_type):
            setattr(self, device_type, {})
        getattr(self, device_type)[device_name] = device_object

        # added logic for stages to store and check stage axes
        if device_type == "tiling_stages" or device_type == "scanning_stages":
            instrument_axis = device_specs["init"]["instrument_axis"]
            if getattr(self, "stage_axes", None) is not None :
                if instrument_axis in self.stage_axes:
                    raise ValueError(f"{instrument_axis} is duplicated and already exists!")
                else:
                    self.stage_axes.append(instrument_axis)

        # Add subdevices under device and fill in any needed keywords to init
        for subdevice_name, subdevice_specs in device_specs.get("subdevices", {}).items():
            # copy so config is not altered by adding in parent devices
            self._construct_subdevice(device_object, subdevice_name, copy.deepcopy(subdevice_specs), lock)
