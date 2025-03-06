import time, json
from json import encoder
import pandas as pd
import numpy as np
from tigerasi.device_codes import Cmds
from . import PartialInstrument
from pathlib import Path

from typing import TYPE_CHECKING

if TYPE_CHECKING :
    from tigerasi.tiger_controller import TigerController
    from voxel.devices.stage.asi.tiger import TigerStage
    from voxel.devices.daq.ni import NIDAQ

class StageInstrument(PartialInstrument):
    selected_device_types = ["stage","daq"]
    selected_daq_ports = ["stage","camera"]

    def stage_motion_run(self, step_size_um=1, pulse_count = 32, sampling_rate_hz = 10):
        stage : "TigerStage" = self.grab_first(self.scanning_stages)
        daq : "NIDAQ" = self.grab_first(self.daqs)

        self.log.info(f"Setuping debug test")

        stage.setup_step_shoot_scan(step_size_um)
        daq.add_task("ao")
        daq.generate_waveforms("ao", "639")
        daq.write_ao_waveforms()
        daq.add_task("co", pulse_count)

        self.log.info(f"Starting debug test")

        pulse_offset = self.config["instrument"]["devices"]["pcie-6738"]["properties"]["tasks"]["ao_task"]["ports"]["stage"]["parameters"]["start_time_ms"]["channels"]["639"] / 1000
        positions = []
        task_end = None
        pulse = 0

        for task in [daq.ao_task, daq.do_task, daq.co_task]:  # must start co task last in list
            if task is not None:
                task.start()
        
        start_time = time.time()
        next_time = start_time + pulse_offset  + ( 1.0 / daq.co_frequency_hz )
        self.log.info(f"Task started at {start_time}")
        while not task_end :
            try :
                position = stage.position_mm
            except ValueError:
                position = None
            if position is None :
                self.log.warning(f"Error getting the position")
                position = np.nan
            positions.append({"time":time.time(),"position":position, "pulse_nb":pulse})
            
            if time.time() >= next_time :
                pulse += 1
                next_time = start_time + pulse_offset  +  ( pulse * ( 1.0 / daq.co_frequency_hz ) )
                self.log.info(f"Pulses emmited : {pulse}")

            time.sleep(1 / sampling_rate_hz)

            if daq.co_task.is_task_done():
                task_end = time.time()
                self.log.info(f"Task finished at {task_end}")

        daq.stop()
        stage.mode = "off"

        encoder.FLOAT_REPR = lambda o: format(o, '.5f')
        with open(Path(__file__).parent / "stage_motion_run_results.json", "w") as f :
            json.dump(positions, f, indent = 4)

        df = pd.DataFrame(positions)

        ax = df.plot("time", "position", zorder = 2)

        pulse_offset = self.config["instrument"]["devices"]["pcie-6738"]["properties"]["tasks"]["ao_task"]["ports"]["stage"]["parameters"]["start_time_ms"]["channels"]["639"]
        for pulse in range(pulse_count):
            time_flag = start_time + (pulse_offset / 1000) + (pulse * ( 1.0 / daq.co_frequency_hz ))
            ax.axvline(time_flag, alpha = 0.2, color = 'gray',zorder = -1)

        ax = df.plot("time", "pulse_nb", ax = ax, secondary_y = True, zorder = 1)
        ax.figure.savefig(Path(__file__).parent / "stage_motion_run_results_position_vs_time.png")

        


        self.log.info(f"Finished debug test")

    
    def set_rotary_encoder(self):
        controller : TigerController = self.grab_first(self.stages)
        controller._set_cmd_args_and_kwds(Cmds.CCA, "X=4")
        controller._set_cmd_args_and_kwds(Cmds.RESET,)


    