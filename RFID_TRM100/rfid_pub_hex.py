import serial
import paho.mqtt.client as mqtt
import threading
import time
import argparse

# python rfid_pub_hex.py --machine_id machine1 --port COM8 --baudrate 115200 --mqtt_broker 192.168.0.72 --mqtt_port 1883 --rfid_type front

class Rfid:
    def __init__(self, mqtt_broker, mqtt_port, topic_rfid, baudrate, port): # '/dev/ttyUSB0' 

        #Single read #according to the documentation of RFID Reader
        self.hex_data_to_send = [0xBB, 0x00, 0x22, 0x00, 0x00, 0x22, 0x7E]

        # Multiple read #according to the documentation of RFID Reader
        self.hex_data_to_send = [0xBB, 0x00, 0x27, 0x00, 0x03, 0x22, 0xFF, 0xFF, 0x4A, 0x7E ]
      
        # Initialize serial communication parameters
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=1,  # Timeout for read operations
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        

        # MQTT Broker Information
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.topic_rfid = topic_rfid

        # MQTT clients
        self.publish_client = mqtt.Client()

        # Shared state
        self.running = True


    def send_data(self, data):
        if self.ser.is_open:
            self.ser.write(bytearray(data))
            #print(f"Sent: {data}")
        else:
            print("ERROR: Serial port is not open")
    
    def manage_frame(self):
        # Receive the data
        try:
            while self.running:
                self.send_data(self.hex_data_to_send)
                self.receive_data()
                #time.sleep(0.1)  # Keep the thread alive
        except KeyboardInterrupt:
            pass
        finally:
            self.publish_client.loop_stop()
            self.publish_client.disconnect()
            print("Disconnected from rfid broker.")
    
    def receive_data(self):
        """
        Receive data from the serial port until a complete frame is received.
        A frame starts with 0xBB and ends with 0x7E.
        :return: Received frame as a list of bytes
        """
        if self.ser.is_open:
            frame = []
            while True:
                # Read one byte at a time
                byte = self.ser.read(1)
                if byte:
                    # Convert byte to integer
                    byte_value = int.from_bytes(byte, "big")
                    
                    # Start of the frame (Header)
                    if byte_value == 0xBB and not frame:
                        frame.append(byte_value)
                    
                    # Add bytes to the frame if the header is detected
                    elif frame:
                        frame.append(byte_value)
                        
                        # End of the frame (Terminator)
                        if byte_value == 0x7E:
                            # print(f"Received Frame: {bytes(frame).hex(' ').upper()}")
                            # self.publish_client.publish(self.topic_rfid, payload=bytes(frame).hex(' ').upper(), qos=1)
                            # return frame
                            
                            if(len(frame)>8):
                                # publish RFID hexa byte form 8 to 20 if a tag is reading
                                self.publish_client.publish(self.topic_rfid, payload=bytes(frame[8:20]).hex(' ').upper(), qos=1)
                            else:
                                # publish no reading tag
                                self.publish_client.publish(self.topic_rfid, payload=bytes(frame).hex(' ').upper(), qos=1)
                            return frame
                else:
                    # No data available (timeout or end of stream)
                    print("Timeout: No complete frame received")
                    return None
        else:
            print("ERROR: Serial port is not open")
            return None

    
    def start(self):
      
        """Start the MQTT handlers in threads."""
        # Connect the publishing client
        self.publish_client.connect(self.mqtt_broker, self.mqtt_port)
        self.publish_client.loop_start()

        # Create threads
        publish_rfid = threading.Thread(target=self.manage_frame)
        publish_rfid.start()

        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            # Gracefully stop on Ctrl+C
            self.running = False
            publish_rfid.join()
            self.publish_client.loop_stop()
            self.publish_client.disconnect()
            print("RFID Program terminated.")


if __name__ == "__main__":


    parser = argparse.ArgumentParser(description="RFID Reader MQTT Publisher")

    # Add arguments for Port and Baudrate
    parser.add_argument('--machine_id', type=str, default='oht1', help="machine1 to machine10")
    parser.add_argument('--mqtt_broker', type=str, default='192.168.0.72', help="MQTT Broker IP address")
    parser.add_argument('--mqtt_port', type=int, default=1883, help="MQTT Broker Port")
    parser.add_argument('--port', type=str, default='COM6', help="Serial port for RFID reader (e.g., COM6 or /dev/ttyUSB0)")
    parser.add_argument('--baudrate', type=int, default=115200, help="Baudrate for the RFID reader (default: 115200)")
    parser.add_argument('--rfid_type', type=str, default='travel', help="travel or front or back")

    # Parse command-line arguments
    args = parser.parse_args()

    # Topic
    TOPIC_RFID = f"rfid/{args.machine_id}/{args.rfid_type}"

    # Run Program
    app = Rfid(
        mqtt_broker=args.mqtt_broker,
        mqtt_port=args.mqtt_port,
        topic_rfid=TOPIC_RFID,
        baudrate=args.baudrate,
        port=args.port
    )

    app.start()



