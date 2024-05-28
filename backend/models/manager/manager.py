from models.sensor_mgmt.sensor_manager import SensorDataManager
from models.data_manager.storage_manager import StorageManager
from models.data_manager.cloud_transfer import CloudTransferManager
from models import ModelLogger
from multiprocessing.connection import Pipe
from multiprocessing import Process
from time import sleep
from typing import Dict
from util import get_base_path
import os


class Managerlogger:
    logger = ModelLogger("manager").customiseLogger(
        filename=os.path.join("{}".format(get_base_path()), "logs", "manager.log")
    )


class Manager:
    """
    Manager class is a singleton that manages inter-process communication, processes, and command handling.

    Attributes:
    - pipes (dict): A dictionary to store pipe connections.
    - send_cmd_dsm, recv_cmd_dsm: Pipes for DSM command communication.
    - send_cmd_sdm, recv_cmd_sdm: Pipes for SDM command communication.
    - send_cmd_ctm, recv_cmd_ctm: Pipes for CTM command communication.
    - send_data_sdm, recv_data_dsm: Pipes for SDM data communication.
    - _instance (Manager): The singleton instance of the Manager class.
    """

    pipes = {}
    send_cmd_dsm, recv_cmd_dsm = Pipe()
    send_cmd_sdm, recv_cmd_sdm = Pipe()
    send_cmd_ctm, recv_cmd_ctm = Pipe()
    send_data_sdm, recv_data_dsm = Pipe()

    _instance = None

    def __new__(cls):
        """
        Override the __new__ method to implement the singleton pattern.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """
        Initialize the Manager instance.

        Attributes:
        - processes (dict): A dictionary to store processes.
        - cmd_hdlr (CommandHandler): An instance of the CommandHandler class.
        """
        self.processes = {}
        self.cmd_hdlr = CommandHandler()

    @classmethod
    def get_pipes_connections(cls, name):
        """
        Get the pipe connections for a given name.

        Args:
        - name (str): The name of the pipe connection.

        Returns:
        - The pipe connections associated with the name.
        """
        return cls.pipes.get(name)

    @classmethod
    def get_instance(cls):
        """
        Get the singleton instance of the Manager class.

        Returns:
        - The singleton instance of the Manager class.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def handle_command(self, command, *args, **kwargs) -> dict:
        """
        Handle a command by executing it through the CommandHandler and updating the process list.

        Args:
        - command (str): The command to handle.
        - args: Additional positional arguments for the command.
        - kwargs: Additional keyword arguments for the command.

        Returns:
        - dict: The status of the command execution.
        """
        Managerlogger.logger.info(f"Handling command: {command}")
        status = self.cmd_hdlr.execute_command(command, self, *args, **kwargs)
        self.update_processes(status.get("process_name"), status.get("process"))
        print(
            f"{status['status']}: ", end=""
        )
        return status

    def get_process(self, process_name) -> Process:
        """
        Get a process by its name.

        Args:
        - process_name (str): The name of the process.

        Returns:
        - Process: The process associated with the name.
        """
        return self.processes.get(process_name)

    def get_processes(self):
        """
        Get all processes managed by the Manager.

        Returns:
        - dict: A dictionary of all processes.
        """
        return self.processes

    def update_processes(self, process_name, process):
        """
        Update the processes dictionary with a new process.

        Args:
        - process_name (str): The name of the process.
        - process (Process): The process instance.
        """
        self.processes[process_name] = process

    def remove_process(self, process_name):
        """
        Remove a process from the processes dictionary.

        Args:
        - process_name (str): The name of the process to remove.
        """
        self.processes.pop(process_name)


class CommandHandler:
    """
    Handles execution of various commands related to data saving, cloud transfer,
    and data collection.

    Attributes:
    - command_map (dict): Maps commands to their corresponding handler methods.
    - data_saving (bool): Indicates if data saving is currently active.
    """

    def __init__(self):
        """
        Initializes the CommandHandler with a command map and data saving status.
        """
        self.command_map = {
            "START-DATA_SAVING": self.start_data_saving,
            "STOP-DATA_SAVING": self.stop_data_saving,
            "START-CLOUD_TRANSFER": self.start_cloud_transfer,
            "STOP-CLOUD_TRANSFER": self.stop_cloud_transfer,
            "START-DATA_COLLECTION": self.start_data_collection,
            "STOP-DATA_COLLECTION": self.stop_data_collection,
        }
        self.data_saving = False

    def execute_command(self, command, processes, *args, **kwargs):
        """
        Executes the given command by invoking the corresponding method.

        Args:
        - command (str): The command to execute.
        - processes: The processes manager.
        - args: Additional positional arguments for the command handler.
        - kwargs: Additional keyword arguments for the command handler.

        Returns:
        - dict: The status of the command execution, if the command is recognized.
        """
        if command in self.command_map:
            return self.command_map[command](command, processes, *args, **kwargs)
        else:
            Managerlogger.logger.info(f"Unknown command {command}")

    def start_data_saving(self, command, caller: Manager, *args, **kwargs):
        """
        Starts the data saving process.

        Args:
        - command (str): The command string.
        - caller (Manager): The manager instance invoking this command.
        - args: Sensor names to be passed to the StorageManager.
        - kwargs: Additional keyword arguments.

        Returns:
        - dict: The status of the command execution.
        """
        process_name = self.get_process_name_from_command(command)
        if (not caller.get_process(process_name)) or (
            not caller.get_process(process_name).is_alive()
        ):
            dsm_instance = StorageManager(sensor_names=args)
            process = self.process_generator(
                process_name, dsm_instance, Manager.recv_cmd_dsm, Manager.recv_data_dsm
            )
            process.start()
            Manager.send_cmd_sdm.send("START")
            self.data_saving = True
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
        """
        Generates a status dictionary.

        Args:
        - args: Additional positional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - dict: The generated status dictionary.
        """
        return kwargs

    def stop_data_saving(self, command, caller: Manager, *args, **kwargs):
        """
        Stops the data saving process.

        Args:
        - command (str): The command string.
        - caller (Manager): The manager instance invoking this command.
        - args: Additional positional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - dict: The status of the command execution.
        """
        process_name = self.get_process_name_from_command(command)
        process = caller.get_process(process_name)
        if process and process.is_alive():
            Manager.send_cmd_dsm.send("END")
            Managerlogger.logger.info("Command for termination of saving process sent")
            process.join()
            if process.is_alive():
                Managerlogger.logger.info("stop-Data_saving command Failed")
                return self.status_generator(
                    status="failed",
                    process=process,
                    process_name=process_name.lower(),
                    message="DSM Process is still alive",
                )
            Manager.send_cmd_sdm.send("STOP")
            self.data_saving = False
            Managerlogger.logger.info("stop-Data_saving command successfully Executed")
            return self.status_generator(
                status="success",
                process=None,
                process_name=process_name.lower(),
                message="DSM Process is terminated",
            )
        Managerlogger.logger.info(
            "data collection process does not exist or is not alive"
        )
        return self.status_generator(
            status="success",
            process=None,
            process_name=process_name.lower(),
            message="DSM Process does not exist to be terminated",
        )

    def start_data_collection(self, command, caller, *args, **kwargs):
        """
        Starts the data collection process.

        Args:
        - command (str): The command string.
        - caller: The manager instance invoking this command.
        - args: Additional positional arguments for the command handler.
        - kwargs: Additional keyword arguments for the command handler.

        Returns:
        - dict: The status of the command execution.
        """
        process_name = self.get_process_name_from_command(command)
        if (not caller.get_process(process_name)) or (
            not caller.get_process(process_name).is_alive()
        ):
            sdm_instance = SensorDataManager()
            process = self.process_generator(
                process_name, sdm_instance, Manager.recv_cmd_sdm, Manager.send_data_sdm
            )
            process.start()
            if self.data_saving:
                Manager.send_cmd_sdm.send("START")
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

    def start_command_helper(self, caller, process_name, obj):
        """
        Helper method for starting a command process.

        Args:
        - caller: The manager instance invoking this command.
        - process_name (str): The name of the process to start.
        - obj: The object associated with the process to start.
        """
        pass

    def stop_data_collection(self, command, caller, *args, **kwargs):
        """
        Stops the data collection process.

        Args:
        - command (str): The command string.
        - caller: The manager instance invoking this command.
        - args: Additional positional arguments for the command handler.
        - kwargs: Additional keyword arguments for the command handler.

        Returns:
        - dict: The status of the command execution.
        """
        process_name = self.get_process_name_from_command(command)
        process = caller.get_process(process_name)
        if process and process.is_alive():
            Manager.send_cmd_sdm.send("END")
            Managerlogger.logger.info(
                "Command for termination of data collection process sent"
            )
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
        Managerlogger.logger.info(
            "data collection process does not exist or is not alive"
        )
        return self.status_generator(
            status="success",
            process=None,
            process_name=process_name.lower(),
            message="SDM Process does not exist to be terminated",
        )

    def start_cloud_transfer(self, command, caller, *args, **kwargs):
        """
        Starts the cloud transfer process.

        Args:
        - command (str): The command string.
        - caller: The manager instance invoking this command.
        - args: Additional positional arguments for the command handler.
        - kwargs: Additional keyword arguments for the command handler.

        Returns:
        - dict: The status of the command execution.
        """
        process_name = self.get_process_name_from_command(command)
        if (not caller.get_process(process_name)) or (
            not caller.get_process(process_name).is_alive()
        ):
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
        """
        Stops the cloud transfer process.

        Args:
        - command (str): The command string.
        - caller: The manager instance invoking this command.
        - args: Additional positional arguments for the command handler.
        - kwargs: Additional keyword arguments for the command handler.

        Returns:
        - dict: The status of the command execution.
        """
        process_name = self.get_process_name_from_command(command)
        process = caller.get_process(process_name)
        if process and process.is_alive():
            Manager.send_cmd_ctm.send("END")
            Managerlogger.logger.info(
                "Command for termination of cloud transfer process sent"
            )
            process.join()
            if process.is_alive():
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
        Managerlogger.logger.info(
            "Cloud Transfer process does not exist or is not alive"
        )
        return self.status_generator(
            status="success",
            process=None,
            process_name=process_name.lower(),
            message="CTM Process does not exist to be terminated",
        )

    @staticmethod
    def get_process_name_from_command(command):
        """
        Extracts the process name from the command string.

        Args:
        - command (str): The command string.

        Returns:
        - str: The process name extracted from the command.
        """
        return command.split("-")[1].lower()

    @staticmethod
    def process_target(instance, com_pipe, data_pipe):
        """
        Target function for the process.

        Args:
        - instance: The instance to run.
        - com_pipe: The communication pipe.
        - data_pipe: The data pipe.
        """
        instance.run(com_pipe, data_pipe)

    def process_generator(self, name, *args):
        """
        Generates a new process.

        Args:
        - name (str): The name of the process.
        - args: Additional arguments for the process target.

        Returns:
        - Process: The generated process instance.
        """
        return Process(target=self.process_target, args=args, daemon=False, name=name)


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
