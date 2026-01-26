import traceback
import pexpect
import serial
from pexpect import fdpexpect
from src.utils.exception import UartSetupIssue


class Uart:
    def __init__(self, uart_port, baudrate=115200, log_file_path=None, log_level=0):
        self.uart_port_info = {
            "port": uart_port,
            "baudrate": baudrate,
            "bytesize": 8,
            "parity": "N",
            "stopbits": 1,
            "timeout": None,
            "xonxoff": 0,
            "rtscts": 0
        }
        self.log_file_path = log_file_path
        self.serial_conn_obj = None
        self.file_descriptor_process = None
        self.log_level = log_level
        self.log_file_obj = None
    
    def __del__(self):
        self.disconnect()
        if self.log_level > 1:
            print('[ Info ] Deleting UartInterface object and releasing the resources.')
        
    def connect(self):
        self.serial_conn_obj = serial.Serial(self.uart_port_info['port'])
        ser_settings = self.serial_conn_obj.getSettingsDict()
        ser_settings.update(self.uart_port_info)
        self.serial_conn_obj.applySettingsDict(ser_settings)
        
        if self.log_level > 1:
            print(f"[ Info ] Serial connection is opened for port {self.uart_port_info['port']}")
        
        if self.log_file_path is not None:
            self.log_file_obj = open(self.log_file_path, 'ab+')
            if self.log_level > 1:
                print('[ Info ] Uart log file opened.')
            
        # create logging for serial_log_obj
        self.file_descriptor_process = fdpexpect.fdspawn(self.serial_conn_obj, logfile=self.log_file_obj, use_poll=True)
        if self.log_level > 1:
            print("[ Info ] File descriptor process is opened.\n")
    
    def disconnect(self):
        try:
            if self.serial_conn_obj and self.serial_conn_obj.isOpen():
                self.serial_conn_obj.close()
                if self.log_level > 1:
                    print('\n[ Info ] Serial connection obj is closed.')
            if self.file_descriptor_process and self.file_descriptor_process.isalive():
                self.file_descriptor_process.close()
                if self.log_level > 1:
                    print('[ Info ] File descriptor process is closed.')
            if self.log_file_obj:
                self.log_file_obj.close()
                if self.log_level > 1:
                    print('[ Info ] Uart log file closed.')
        except Exception as e:
            if self.log_level > 0:
                print("[ Error ] Error while closing the UartInterface resources :", e)
                print(traceback.format_exc())


    def send_command(self, cmd, expected_string=None, return_code=None, timeout=120, retry_count=1) -> bool:
        # command success status
        status = False
        
        try:
            index = None
            # retry 3 times
            for iteration in range(retry_count):
                # run the command
                if self.log_level > 1:
                    print('[ Info ] Sending Uart Command : ' + str(cmd))
                self.file_descriptor_process.sendline(cmd + '\n')
        
                # check the output if expected_string is defined
                # skip otherwise
                if expected_string is not None:
                    # check the constraint
                    if self.log_level > 1:
                        print('[ Info ] Waiting for : ' + expected_string)
                    index = self.file_descriptor_process.expect([expected_string, pexpect.TIMEOUT, pexpect.EOF], timeout)
                        
                    # checking the return code based on the list provided in expect()
                    if index == 0:  # Process is completes and we received expected string
                        # Print the DUT UART logs
                        cmd_response = self.file_descriptor_process.before + self.file_descriptor_process.after
                        cmd_response = cmd_response.decode(encoding='iso8859-1')
                        if self.log_level > 2:
                            print(f"[ Info ] Command Output \n```\n{cmd_response}\n```\n")
                        log_buffer = cmd_response
        
                    # if command execute successfully then break the loop
                    if index == 0:
                        if self.log_level > 1:
                            print(f'[ Info ] Successfully Executed Uart Command.\n')
                        break
                    elif index == 1:  # Timeout and we did not received expected string
                        if self.log_level > 1:
                            print(
                                (f"[ Warning ] Did not fond expected_string in {timeout}s timeout.")
                                (f"Trying Again... iteration - {iteration + 1}")
                            )
        
            if index == 1:
                raise UartSetupIssue(f"[ Error ] Timeout while sending command : {cmd}")
            else:
                status = True
        except Exception as e:
            if self.log_level > 0:
                print('[ Error ] Error occurred while sending command : ', e)
                print(traceback.format_exc())
        finally:
            pass
        
        return status
