from multiprocessing import Process, Pipe
from models.data_manager.data_saving import DataSavingManager


class Manager:
    pipes = {}
    send_cmd_dsm, recv_cmd_dsm = Pipe()
    send_cmd_sdm, recv_cmd_sdm = Pipe()
    send_cmd_aws, recv_cmd_aws = Pipe()
    send_data_sdm, recv_data_dsm = Pipe()

    def __init__(self) -> None:
        self.processes = {}
        self.cmd_hdlr = self.CommandHandler()

    @classmethod
    def get_pipes_connections(cls, name):
        return cls.pipes.get(name)

    def handle_command(self, command, *args, **kwargs):
        status = self.command_handler.execute_command(command, *args, **kwargs)
        self.update_processes(status.get("process_name"), status.get("process"))
        return status

    def get_process(self, process_name):
        return self.processes.get(process_name)

    def get_processes(self):
        return self.processes

    def update_processes(self, process_name, process):
        if process_name:
            self.processes[process_name] = process

    def remove_process(self, process_name):
        self.processes.pop(process_name, None)


class CommandHandler:
    def __init__(self, recv_cmd_dsm, recv_data_dsm):
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
            return {"status": "ERROR", "message": f"Unknown command: {command}"}

    def start_data_saving(self, *args, **kwargs):
        data_recv_pipe = Manager.get_pipes_connections("data_pipe")
        if data_recv_pipe is None:
            return {"status": "Failed", "message": "Data is not being collected"}
        send_cmd_dsm, recv_cmd_dsm = Pipe()
        pipe = {"data_saving_pipe": (send_cmd_dsm, recv_cmd_dsm)}
        dsm_instance = DataSavingManager(
            recv_cmd_pipe=recv_cmd_dsm,
            data_pipe=data_recv_pipe,
            sensor_names=args,
            **kwargs,
        )
        process = self.process_generator("data_saving_process", dsm_instance)

        return {
            "status": "OK",
            "message": "Data is being stored",
            "process": process,
            "pipe": pipe,
        }

    def stop_data_saving(self, process_name, *args, **kwargs):
        process = self.get_process(process_name)
        if process:
            process.terminate()
            return {
                "status": "OK",
                "message": "Data saving stopped",
                "process_name": process_name,
                "process": None,
            }
        else:
            return {
                "status": "ERROR",
                "message": f"Process '{process_name}' not found",
                "process_name": process_name,
                "process": None,
            }

    def process_generator(self, name, instance):
        process = Process(
            target=self.process_target, args=(instance,), daemon=True, name=name
        )
        process.start()
        return process

    @staticmethod
    def process_target(instance):
        instance.run()


if __name__ == "__main__":
    recv_cmd_dsm, recv_data_dsm = Pipe()
    manager = Manager()
    command_handler = CommandHandler(recv_cmd_dsm, recv_data_dsm)
    manager.command_handler = command_handler

    # Example usage:
    manager.handle_command(
        "START_DATA_SAVING",
        "dsm_process",
        "arg1",
        "arg2",
        kwarg1="value1",
        kwarg2="value2",
    )
