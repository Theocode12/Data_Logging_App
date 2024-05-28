# DataLogger

## Description

DataLogger is an application designed to run on a Raspberry Pi connected to multiple sensors. This application polls data from all the connected sensors and stores it (if required). Additionally, the stored data can be uploaded to a cloud service compatible with AWS.

## Table of Contents
1. [Installation](#installation)
2. [Usage](#usage)
3. [Configuration](#configuration)
4. [Adding a New Sensor](#adding-a-new-sensor)
5. [Contributing](#contributing)
6. [Testing](#testing)
7. [License](#license)
8. [Authors and Acknowledgments](#authors-and-acknowledgments)
9. [Contact Information](#contact-information)
10. [Additional Resources](#additional-resources)

## Installation

To install the application, you can either clone the repository or download it as a zip file.

Clone the repository using the following command:

```sh
git clone <repository-url>
```

Alternatively, download the repository as a zip file and extract it.

Make sure to install the required dependencies from the `requirements.txt` file. This should be done within a virtual environment on the Raspberry Pi to ensure proper installation of dependencies.

Create and activate a virtual environment, then install the dependencies:

```sh
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Usage

To run the application, execute the `app.py` file:

```sh
python app.py
```

The application will start, and the screen will hang (sort of). Use the following keyboard bindings to control the data collection process:

- **Ctrl+D**: Start/Stop data collection
- **Ctrl+Q**: Start/Stop data storage to the database
- **Ctrl+U**: Start/Stop data Upload to the cloud

## Configuration

### .env File

The `.env` file requires a path to a temporary database. For example:

```env
tmp_db_path=./tmp/tmp_db
```

To enable the cloud transfer functionality, the following configuration parameters are required:

```env
endpoint=[aws-server-to-communicate-to]
cert_filepath=[path-to-.cert.pem-file]
pri_key_filepath=[path-to-.private.key-file]
ca_filepath=[path-to-.crt-file]
client_id=[client-name]
message_topic=[topic-to-publish-data-to]
```

To obtain the necessary certificates, you must use a functioning AWS account to create a thing in AWS IoT. More details can be found in the [AWS IoT documentation](https://docs.aws.amazon.com/iot/latest/developerguide/register-device.html). Once these certificates have been obtained, they should be placed in the `aws-certs` folder and referred to from there.

### Meta File

The meta file contains information about the current file holding the data being uploaded to the cloud. Two metadata fields are important:

```meta
LastUploadFile=[path-to-last-uploaded-file] e.g /home/valentine/Data_Logging_App/backend/data/2024/04/22.txt
Offset=0
```

**CAUTION**: The `LastUploadFile` path must exist; otherwise, cloud transfer will fail.

## Adding a New Sensor

To add a new sensor, the new sensor class should inherit from the base `Sensor` class, which enforces the `get_data` function to be implemented. For example:

```python
class NewSensor(Sensor):
    def __init__(self):
        # some initialization

    def get_data(self):
        # perform operations to retrieve data from the physical sensor
        return data
```

For the data to be retrieved by the application, sensors must be registered in the `models.sensor_mgmt.register_sensor` module with other sensors. For example:

```python
MODULES = [
    "models.sensors.gps.GPS",  # other sensors
    "models.sensors.new_sensor.NewSensor",
]
```

Note: All new sensors should be placed in the `models/sensors` folder.

## Contributing

We welcome contributions to DataLogger! Please follow these guidelines when contributing:

- Fork the repository
- Create a new branch (`git checkout -b feature-branch`)
- Commit your changes (`git commit -m 'Add some feature'`)
- Push to the branch (`git push origin feature-branch`)
- Open a Pull Request

## Testing

(To be provided)

## License

[MIT Licence](License)

## Copyright
Copyright (c) 2023 Maduagwu Valentine


## Authors and Acknowledgments

Maduagwu Valentine

## Contact Information

GitHub: Theocode12

LinkedIn: [Maduagwu Valentine](https://www.linkedin.com/in/valentine-chidubem-9a076620a/)

## Additional Resources

(To be provided)


