from models.sensor_mgmt.sensor_manager import SensorDataManager
from models.data_manager.data_saving import DataSavingManager
from multiprocessing import Pipe, Process
from time import sleep


def process_target(instance, com_pipe, data_pipe):
    instance.run(com_pipe, data_pipe)


class Manager:
    send_cmd_dsa, recv_cmd_dsa = Pipe()
    send_cmd_sdm, recv_cmd_sdm = Pipe()
    send_cmd_aws, recv_cmd_aws = Pipe()
    send_data_sdm, recv_data_dsa = Pipe()

    class CommandHandler:
        def __init__(self):
            self.command_map = {
                "START_DATA_SAVING": self.start_data_saving,
                "STOP_DATA_SAVING": self.stop_data_saving,
                "START_CLOUD_TRANSFER": self.start_cloud_transfer,
                "STOP_CLOUD_TRANSFER": self.stop_cloud_transfer,
                "START_DATA_COLLECTION": self.start_data_collection,
                "STOP_DATA_COLLECTION": self.stop_data_collection,
            }

        def execute_command(self, command, *args, **kwargs):
            if command in self.command_map:
                return self.command_map[command](*args, **kwargs)
            else:
                print(f"Unknown command: {command}")


# after a command is called a dict with some metadata like process and status
if __name__ == "__main__":
    command_sensor_manager, sensor_manager_command_pipe = Pipe()
    command_saving_manager, data_saving_manager_comm_pipe = Pipe()
    send_data_pipe, receive_data_pipe = Pipe()

    sensor_manager = SensorDataManager()
    dm = Process(
        target=process_target,
        args=(sensor_manager, sensor_manager_command_pipe, send_data_pipe),
    )
    dm.start()

    data_saving_manager = DataSavingManager()
    dsm = Process(
        target=process_target,
        args=(data_saving_manager, data_saving_manager_comm_pipe, receive_data_pipe),
    )
    dsm.start()

    command_sensor_manager.send("START_SEND_DATA")
    command_sensor_manager.send("STOP")
    sleep(1)
    command_saving_manager.send("STOP")

    dsm.join()
    dm.join()
