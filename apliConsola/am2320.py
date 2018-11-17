#!/usr/bin/python

import posix
from fcntl import ioctl
import time

class AM2320:
  I2C_ADDR = 0x5c
  I2C_SLAVE = 0x0703
  
  def __init__(self, i2cbus = 1):
    self._i2cbus = i2cbus #atributo
    self._fd = posix.open("/dev/i2c-%d" % self._i2cbus, posix.O_RDWR) #i2c-1
    print ("fd:"+ str(self._fd))

    ioctl(self._fd, AM2320.I2C_SLAVE, AM2320.I2C_ADDR)
  
   ##print (__name__)

  def _despertar(self, espera):
    # wake AM2320 up, goes to sleep to not warm up and affect the humidity sensor 
    # This write will fail as AM2320 won't ACK this write
    try:
      posix.write(self._fd, b'\0x00')
    except:
      pass	   	#se lanza excepcion al enviarle NULL
    time.sleep(espera)


  #metodo para todos los objetos, por eso no tiene self
  @staticmethod
  def _calc_crc16(data):
    crc = 0xFFFF
    for x in data:
      crc = crc ^ x
      for bit in range(0, 8):
        if (crc & 0x0001) == 0x0001:
          crc >>= 1
          crc ^= 0xA001
        else:
          crc >>= 1
    return crc

  @staticmethod
  def _combine_bytes(msb, lsb):
    return msb << 8 | lsb #suma binaria (OR)


  #Wait at least 0.8ms, at most 3ms
  def leerTemHume(self):
    self._despertar(0.008)
      
    # write command 0x03, start reg = 0x00, num regs = 0x04
    posix.write(self._fd, b'\x03\x00\x04')
    #Wait at least 1.5ms for result
    time.sleep(0.0016) 

    # Read out 8 bytes of result data
    # Byte 0: Should be Modbus function code 0x03
    # Byte 1: Should be number of registers to read (0x04)
    # Byte 2: Humidity msb
    # Byte 3: Humidity lsb
    # Byte 4: Temperature msb
    # Byte 5: Temperature lsb
    # Byte 6: CRC lsb byte
    # Byte 7: CRC msb byte
    data = bytearray(posix.read(self._fd, 8))
  
    # Check data[0] and data[1] if not correct throw Exception
    if data[0] != 0x03 or data[1] != 0x04:
      raise Exception("First two bytes not as expected")

    # CRC check
    if self._calc_crc16(data[0:6]) != self._combine_bytes(data[7], data[6]):
      raise Exception("CRC failed")
    
    # Temperature resolution is 16Bit, 
    # temperature highest bit (Bit15) is equal to 1 indicates a
    # negative temperature, the temperature highest bit (Bit15)
    # is equal to 0 indicates a positive temperature; 
    # temperature in addition to the most significant bit (Bit14 ~ Bit0)
    # indicates the temperature sensor string value.
    # Temperature sensor value is a string of 10 times the
    # actual temperature value.
    temp = self._combine_bytes(data[4], data[5])
    if temp & 0x8000:
      temp = -(temp & 0x7FFF)
    temp /= 10.0
  
    humi = self._combine_bytes(data[2], data[3]) / 10.0

    return (temp, humi)

  def leerTem(self):
    self._despertar(0.008)
      
    # write command 0x03, start reg = 0x00, num regs = 0x02
    posix.write(self._fd, b'\x03\x02\x02')
    #Wait at least 1.5ms for result
    time.sleep(0.0016) 

    # Read out 8 bytes of result data
    # Byte 0: Should be Modbus function code 0x03
    # Byte 1: Should be number of registers to read (0x02)
    # Byte 2: Temperature msb
    # Byte 3: Temperature lsb
    # Byte 4: CRC lsb byte
    # Byte 5: CRC msb byte
    data = bytearray(posix.read(self._fd, 6))
  
    # Check data[0] and data[1] if not correct throw Exception
    if data[0] != 0x03 or data[1] != 0x02:
      raise Exception("First two bytes not as expected")

    # CRC check
    if self._calc_crc16(data[0:4]) != self._combine_bytes(data[5], data[4]):
      raise Exception("CRC failed")
    
    # Temperature resolution is 16Bit, 
    # temperature highest bit (Bit15) is equal to 1 indicates a
    # negative temperature, the temperature highest bit (Bit15)
    # is equal to 0 indicates a positive temperature; 
    # temperature in addition to the most significant bit (Bit14 ~ Bit0)
    # indicates the temperature sensor string value.
    # Temperature sensor value is a string of 10 times the
    # actual temperature value.
    temp = self._combine_bytes(data[2], data[3])
    if temp & 0x8000:
      temp = -(temp & 0x7FFF)
    temp /= 10.0

    return temp

  def leerHume(self):
    self._despertar(0.008)
      
    # write command 0x03, start reg = 0x00, num regs = 0x02
    posix.write(self._fd, b'\x03\x00\x02')
    #Wait at least 1.5ms for result
    time.sleep(0.0016) 

    # Read out 8 bytes of result data
    # Byte 0: Should be Modbus function code 0x03
    # Byte 1: Should be number of registers to read (0x02)
    # Byte 2: Humidity msb
    # Byte 3: Humidity lsb
    # Byte 4: CRC lsb byte
    # Byte 5: CRC msb byte
    data = bytearray(posix.read(self._fd, 6))
  
    # Check data[0] and data[1] if not correct throw Exception
    if data[0] != 0x03 or data[1] != 0x02:
      raise Exception("First two bytes not as expected")

    # CRC check
    if self._calc_crc16(data[0:4]) != self._combine_bytes(data[5], data[4]):
      raise Exception("CRC failed")
    
    # Temperature resolution is 16Bit, 
    # temperature highest bit (Bit15) is equal to 1 indicates a
    # negative temperature, the temperature highest bit (Bit15)
    # is equal to 0 indicates a positive temperature; 
    # temperature in addition to the most significant bit (Bit14 ~ Bit0)
    # indicates the temperature sensor string value.
    # Temperature sensor value is a string of 10 times the
    # actual temperature value.
    
    humi = self._combine_bytes(data[2], data[3]) / 10.0

    return humi

  def close(self):
    posix.close(self._fd)
