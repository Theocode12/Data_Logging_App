from models.sensor_mgmt.sensor_manager import SensorDataManager
from models.data_manager.data_saving import DataSavingManager
from models.data_manager.cloud_transfer import CloudTransferManager
from models import ModelLogger
from multiprocessing.connection import Pipe
from multiprocessing import Process
from time import sleep
from typing import Dict


class Managerlogger:
    logger = ModelLogger("manager").customiseLogger()


class Manager:
    pipes = {}
    send_cmd_dsm, recv_cmd_dsm = Pipe()
    send_cmd_sdm, recv_cmd_sdm = Pipe()
    send_cmd_ctm, recv_cmd_ctm = Pipe()
    send_data_sdm, recv_data_dsm = Pipe()

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.processes = {}
        self.cmd_hdlr = CommandHandler()

    @classmethod
    def get_pipes_connections(cls, name):
        return cls.pipes.get(name)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def handle_command(self, command, *args, **kwargs) -> dict:
        Managerlogger.logger.info(f"Handling command: {command}")
        status = self.cmd_hdlr.execute_command(command, self, *args, **kwargs)
        self.update_processes(status.get("process_name"), status.get("process"))
        return status

    def get_process(self, process_name):
        return self.processes.get(process_name)

    def get_processes(self):
        return self.processes

    def update_processes(self, process_name, process):
        self.processes[process_name] = process

    def remove_process(self, process_name):
        self.processes.pop(process_name)


class CommandHandler:
    def __init__(self):
        self.command_map = {
            "START-DATA_SAVING": self.start_data_saving,
            "STOP-DATA_SAVING": self.stop_data_saving,
            "START-CLOUD_TRANSFER": self.start_cloud_transfer,
            "STOP-CLOUD_TRANSFER": self.stop_cloud_transfer,
            "START-DATA_COLLECTION": self.start_data_collection,
            "STOP-DATA_COLLECTION": self.stop_data_collection,
        }
        self.is_data_saving = False
        self.is_cloud_transfer = False
        self.is_data_collection = False

    def execute_command(self, command, processes, *args, **kwargs):
        if command in self.command_map:
            return self.command_map[command](command, processes, *args, **kwargs)
        else:
            Managerlogger.logger.info(f"Unknown command {command}")

    def start_data_saving(self, command, caller: Manager, *args, **kwargs):
        process_name = self.get_process_name_from_command(command)
        if not caller.get_process(process_name):
            dsm_instance = DataSavingManager(sensor_names=args)
            process = self.process_generator(
                process_name, dsm_instance, Manager.recv_cmd_dsm, Manager.recv_data_dsm
            )
            process.start()
            Manager.send_cmd_sdm.send("START")
            Managerlogger.logger.info("start-Data_saving command successfully Executed")
            return self.status_generator(
                status="success",
                process=process,
                process_name=process.name.lower(),
                message="Data is being stored",
            )
        return self.status_generator(
            status="success",
            process=caller.get_process(process_name),
            process_name=process_name.lower(),
            message="Data is already being saved",
        )

    def status_generator(self, *args, **kwargs):
        return kwargs

    def stop_data_saving(self, command, caller: Manager, *args, **kwargs):
        process_name = self.get_process_name_from_command(command)
        if process := caller.get_process(process_name):
            Manager.send_cmd_dsm.send("END")
            process.join()
            if process.is_alive():
                Managerlogger.logger.info("stop-Data_saving command Failed")
                return self.status_generator(
                    status="failed",
                    process=process,
                    process_name=process_name.lower(),
                    message="DSM Process is still alive",
                )
            Managerlogger.logger.info("stop-Data_saving command successfully Executed")
            return self.status_generator(
                status="success",
                process=None,
                process_name=process_name.lower(),
                message="DSM Process is terminated",
            )
        return self.status_generator(
            status="success",
            process=None,
            process_name=process_name.lower(),
            message="DSM Process does not exist to be terminated",
        )

    def start_data_collection(self, command, caller, *args, **kwargs):
        process_name = self.get_process_name_from_command(command)
        if not caller.get_process(process_name):  # check if process exists and alive
            sdm_instance = SensorDataManager()
            process = self.process_generator(
                process_name, sdm_instance, Manager.recv_cmd_sdm, Manager.send_data_sdm
            )
            process.start()
            return self.status_generator(
                status="success",
                process=process,
                process_name=process.name.lower(),
                message="Data is being collected",
            )
        return self.status_generator(
            status="success",
            process=caller.get_process(process_name),
            process_name=process_name.lower(),
            message="Data collection ongoing",
        )

    def stop_data_collection(self, command, caller, *args, **kwargs):
        process_name = self.get_process_name_from_command(command)
        if process := caller.get_process(process_name):
            Manager.send_cmd_sdm.send("END")
            process.join()
            if process.is_alive():
                return self.status_generator(
                    status="failed",
                    process=process,
                    process_name=process_name.lower(),
                    message="SDM Process is still alive",
                )
            Managerlogger.logger.info(
                "stop-Data_collection command successfully Executed"
            )
            return self.status_generator(
                status="success",
                process=None,
                process_name=process_name.lower(),
                message="SDM Process is terminated",
            )
        return self.status_generator(
            status="success",
            process=None,
            process_name=process_name.lower(),
            message="SDM Process does not exist to be terminated",
        )

    def start_cloud_transfer(self, command, caller, *args, **kwargs):
        process_name = self.get_process_name_from_command(command)
        if not caller.get_process(process_name):
            ctm_instance = CloudTransferManager()
            process = self.process_generator(
                process_name, ctm_instance, Manager.recv_cmd_ctm, None
            )
            process.start()
            return self.status_generator(
                status="success",
                process=process,
                process_name=process.name.lower(),
                message="Data is being uploaded to AWS",
            )
        return self.status_generator(
            status="failed",
            process=caller.get_process(process_name),
            process_name=process_name.lower(),
            message="Data Upload Ongoing",
        )

    def stop_cloud_transfer(self, command, caller, *args, **kwargs):
        process_name = self.get_process_name_from_command(command)
        if process := caller.get_process(process_name):
            Manager.send_cmd_ctm.send("END")
            process.join()
            if process.is_alive():
                # process.terminate()
                return self.status_generator(
                    status="failed",
                    process=process,
                    process_name=process_name.lower(),
                    message="SDM Process is still alive",
                )
            Managerlogger.logger.info(
                "stop-cloud_transfer command successfully Executed"
            )
            return self.status_generator(
                status="success",
                process=None,
                process_name=process_name.lower(),
                message="CTM Process is terminated",
            )
        return self.status_generator(
            status="success",
            process=None,
            process_name=process_name.lower(),
            message="CTM Process does not exist to be terminated",
        )

    @staticmethod
    def get_process_name_from_command(command):
        return command.split("-")[1].lower()

    @staticmethod
    def process_target(instance, com_pipe, data_pipe):
        instance.run(com_pipe, data_pipe)

    def process_generator(self, name, *args):  # check weather to name the process
        return Process(target=self.process_target, args=args, daemon=True, name=name)


if __name__ == "__main__":
    # recv_cmd_dsm, recv_data_dsm = Pipe()
    manager = Manager()
    # Example usage:

    # Manager.send_data_sdm.send({"arg1": "value1", "arg2": "value2"})

    # manager.handle_command("START-DATA_COLLECTION")
    # sleep(1)

    # manager.handle_command(
    #     "START-DATA_SAVING", "longitude", "latitude", kwarg1="value1", kwarg2="value2"
    # )
    # sleep(1)

    manager.handle_command("START-CLOUD_TRANSFER")
    sleep(5)
    # manager.handle_command("STOP-DATA_COLLECTION")
    sleep(10)
    # Manager.send_cmd_ctm.send("END")
    manager.handle_command("STOP-CLOUD_TRANSFER")
    # manager.handle_command("STOP-DATA_SAVING")
