import subprocess
import sys
import json

# Read configure file
def read_file(file_path):
    try:
        # Read and load JSON data from the file
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return print(f"File not found: {file_path}")
    except json.JSONDecodeError:
        return print(f"Error decoding JSON data in file: {file_path}")


def run_rfid_script(machine_id, port, baudrate, mqtt_broker, mqtt_port, rfid_type):
    """Run the RFID Python script with the provided parameters."""
    
    # Prepare the command to run
    command = [
        sys.executable,
        'rfid_pub_hex.py',
        '--machine_id', machine_id,
        '--port', port,
        '--baudrate', str(baudrate),
        '--mqtt_broker', mqtt_broker,
        '--mqtt_port', str(mqtt_port),
        '--rfid_type', rfid_type
    ]
    
    # Run the command as a subprocess
    subprocess.Popen(command)

def main():

    machine_id = "machine1"

    # Read configuration files before main
    config_data = read_file("config.json")

    # MQTT Broker Information
    mqtt_broker = config_data["MQTT_BROKER"]["IP"]
    mqtt_port = config_data["MQTT_BROKER"]["PORT"]

    # Travel RFID configure
    port_travel = config_data["RFID"]["TRAVEL"]["PORT"]
    baudrate_travel = config_data["RFID"]["TRAVEL"]["BAUDRATE"]

    # Front RFID configure
    port_front = config_data["RFID"]["FRONT"]["PORT"]
    baudrate_front = config_data["RFID"]["FRONT"]["BAUDRATE"]

    # Back RFID configure
    port_back = config_data["RFID"]["BACK"]["PORT"]
    baudrate_back = config_data["RFID"]["BACK"]["BAUDRATE"]

    
    # Run the TRAVEL RFID reader
    if( config_data["RFID"]["TRAVEL"]["ENABLED"] ):
        run_rfid_script(machine_id = machine_id,  port=port_travel, baudrate=baudrate_travel, mqtt_broker=mqtt_broker, mqtt_port=mqtt_port, rfid_type='travel')

    # Run the FRONT RFID reader
    if( config_data["RFID"]["FRONT"]["ENABLED"] ):
        run_rfid_script(machine_id = machine_id, port=port_front, baudrate=baudrate_front, mqtt_broker=mqtt_broker, mqtt_port=mqtt_port, rfid_type='front')

    # Run the BACK RFID reader
    if( config_data["RFID"]["BACK"]["ENABLED"] ):
        run_rfid_script(machine_id = machine_id, port=port_back, baudrate=baudrate_back, mqtt_broker=mqtt_broker, mqtt_port=mqtt_port, rfid_type='back')

    # Keep the main process alive to let the subprocesses run
    input("Press Enter to terminate the program...\n")

if __name__ == "__main__":
    print(" Ctrl+C and Enter to terminate the program")
    main()
