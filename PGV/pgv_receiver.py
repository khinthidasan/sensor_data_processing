#  https://www.pepperl-fuchs.com/ko-kr/products-gp25581/60355
#  PGV100-F200A-R4-V19 Optical reading head PGV Sensor
import serial

class SensorDataReceiver:
    def __init__(self, port='COM7', baudrate=115200):
        # Initialize serial communication parameters
        self.ser = serial.Serial(
            port=port,  
            baudrate=baudrate,      
            timeout=1,     
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        self.data_to_send_lane = b'\xE4\x1B\xFF'
        self.data_to_send = b'\xC8\x37\xFF'
        self.x = None
        self.y = None
        self.angle = None

    @staticmethod
    def custom_hex_to_decimal(hex_str):
        num = int(hex_str, 16)
        if num >= 0x7f00:
            base_hex = 0x7f7f
            offset = -1
            decimal_value = offset - (base_hex - num)
        else:
            decimal_value = num
        return decimal_value

    @staticmethod
    def hex_string_to_integer(hex_string, start_index, end_index):
        byte_array = bytes.fromhex(hex_string)
        selected_bytes = byte_array[start_index:end_index]
        integer_value = int.from_bytes(selected_bytes, byteorder='big')
        return integer_value

    @staticmethod
    def to_hex_string(value):
        return f'{value:02X}'

    @staticmethod
    def to_decimal(hex_string):
        return int(hex_string, 16)

    @staticmethod
    def process_data(received_data):
        hex_angle1 = SensorDataReceiver.to_hex_string(received_data[10])
        hex_angle2 = SensorDataReceiver.to_hex_string(received_data[11])
        
        concatenated_hex = hex_angle1 + hex_angle2
        decimal_number = SensorDataReceiver.to_decimal(hex_angle1)
        
        if decimal_number == 0:
            decimal_angle = SensorDataReceiver.to_decimal(concatenated_hex)
            return decimal_angle
        elif decimal_number == 2:
            hex_angle1 = SensorDataReceiver.to_hex_string(received_data[10] - 1)
            hex_angle2 = SensorDataReceiver.to_hex_string(received_data[11])
            concatenated_hex = hex_angle1 + hex_angle2
            decimal_angle = SensorDataReceiver.to_decimal(concatenated_hex)
            return decimal_angle
        elif decimal_number == 1:
            hex_angle1 = received_data[10]
            hex_angle2 = received_data[11]
            concatenated_hex = SensorDataReceiver.to_hex_string(hex_angle1) + SensorDataReceiver.to_hex_string(hex_angle2)
            int_value = SensorDataReceiver.to_decimal(concatenated_hex) - 128
            result_hex = SensorDataReceiver.to_hex_string(int_value)
            return int_value
        else:
            return SensorDataReceiver.to_hex_string(received_data[10]) + SensorDataReceiver.to_hex_string(received_data[11])

    def read_sensor_data(self):
        try:
            while True:
                self.ser.write(self.data_to_send_lane)
                response = self.ser.read(21)

                self.ser.write(self.data_to_send)
                response = self.ser.read(21)

                if response:
                    warning = response[0]
                
                if warning == 2:
                    print("No Positioning")
                else:
                    #print("Response Data:", response.hex())

                    # Tag
                    tag_bytes = response[14:18]
                    hex_representation = tag_bytes.hex()
                    integer_representation = int.from_bytes(tag_bytes, byteorder='big')
                    #print(f"Tag: {integer_representation}")

                    # X
                    self.x = self.hex_string_to_integer(response.hex(), 2, 6)
                    #print(f"X: {self.x}")

                    # Y value in signed
                    y_bytes = response[6:8]
                    hex_values = y_bytes.hex()
                    self.y = self.custom_hex_to_decimal(hex_values)
                    #print(f"Y: {self.y}")

                    # Angle
                    self.angle = self.process_data(response)
                    #print(f"Angle: {self.angle}")

        except Exception as e:
            print("Error:", str(e))

        finally:
            # Close the serial port
            self.ser.close()

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_angle(self):
        return self.angle
