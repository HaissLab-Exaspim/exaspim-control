import logging
import sys
from logging import FileHandler
from exaspim_control.exa_spim_instrument import ExASPIM
from exaspim_control.exa_spim_acquisition import ExASPIMAcquisition

if __name__ == "__main__":

    # Setup logging.
    # Create log handlers to dispatch:
    # - User-specified level and above to print to console if specified.
    logger = logging.getLogger()  # get the root logger.
    # Remove any handlers already attached to the root logger.
    logging.getLogger().handlers.clear()
    # logger level must be set to the lowest level of any handler.
    logger.setLevel(logging.DEBUG)
    fmt = "%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s"
    datefmt = "%Y-%m-%d,%H:%M:%S"
    log_formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
    file_handler = FileHandler("output.log", "w")
    file_handler.setLevel("INFO")
    file_handler.setFormatter(log_formatter)
    log_handler = logging.StreamHandler(sys.stdout)
    log_handler.setLevel("INFO")
    log_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    logger.addHandler(log_handler)

    # instrument
    microscope = ExASPIM("./test/camera_only/instrument.yaml")
    # acquisition
    acquisition = ExASPIMAcquisition(microscope, "./test/camera_only/acquisition.yaml")
    # acquisition.check_local_acquisition_disk_space()
    # acquisition.check_external_acquisition_disk_space()
    # acquisition.check_system_memory()
    # acquisition.check_gpu_memory()
    # acquisition.check_write_speed()
    acquisition.run()

    log_handler.close()
    logger.removeHandler(log_handler)