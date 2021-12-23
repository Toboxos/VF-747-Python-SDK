import serial
from .packet import *

def bytes2HexString( data ):
    s = ""
    for b in data:
        s += "{:02x}".format( b )
    
    return s.upper()

def hexString2Bytes( s ):
    data = bytearray()
    for i in range(0, len(s), 2):
        data += bytearray([ int(s[i:i+2], 16) ])

    return data


class Logger:
    LOG_ENABLED = True

    def setEnabled( enabled ):
        Logger.LOG_ENABLED = enabled

    def log( *args ):
        if not Logger.LOG_ENABLED:
            return
        
        print( "---", *args )

class PacketException(Exception):

    def __init__(self, packet : Packet ) -> None:
        self.errorCode = packet.getErrorCode()
        super().__init__( packet.getErrorMessage() )

class Connection:

    def write(self, data) -> None:
        raise NotImplementedError()

    def read(self, size=1) -> bytearray:
        raise NotImplementedError()

    def isOpen(self) -> bool:
        raise NotImplementedError()

    def close(self) -> None:
        raise NotImplementedError()

class SerialConnection(Connection):

    def __init__(self, portName, baudRate ) -> None:
        self.connection = serial.Serial( portName, baudRate )

    def write(self, data) -> None:
        self.connection.write( bytes( data ) )

    def read(self, size=1) -> bytearray:
        return self.connection.read(size)

    def isOpen(self) -> bool:
        return self.connection.is_open

    def close(self) -> None:
        self.connection.close()

class ReaderAPI:
    # BaudRates
    BAUD_9600   = 0x04
    BAUD_19200  = 0x05
    BAUD_38400  = 0x06
    BAUD_57600  = 0x07
    BAUD_115200 = 0x08

    # Relays
    REL1_ON = 0x01
    REL2_ON = 0x02

    # Memory banks
    MEM_PASSWORD    = 0
    MEM_EPC         = 1
    MEM_TID         = 2
    MEM_USER        = 3

    def __init__(self) -> None:
        self.connection = None

    def connectSerial(self, portName, baudRate ):
        self.connection = SerialConnection( portName, baudRate )

        return self.connection.isOpen()

    def closeConnection(self):
        self.connection.close()

    def sendCommand(self, commandCode, packetData, address):
        if address == 0:
            packet = Packet( 0x40, commandCode, packetData )
        else:
            packet = AddressedPacket( 0x40, commandCode, address, packetData )

        Logger.log( "Write packet data:", packet.asHexString() )
        self.connection.write( packet.build() )

        if address == 0:
            packet = Packet.readFrom( self.connection )
        else:
            packet = AddressedPacket.readFrom( self.connection )

        Logger.log( "Read packet data:", packet.asHexString() )

        if packet.failed():
            Logger.log( "Error:", packet.getErrorMessage() )

        return packet


    def setBaudRate(self, baudrate, address=0):
        packet = self.sendCommand( 0x01, bytearray([baudrate]), address )

    def getReaderVersion(self, address=0):
        packet = self.sendCommand( 0x02, bytearray(), address )
        packetData = packet.packetData

        return (packetData[0], packetData[1]), (packetData[2], packetData[3])

    def setRelay(self, flags, address=0):
        packet = self.sendCommand( 0x03, bytearray([flags]), address )

    def getRelay(self, address=0):
        packet = self.sendCommand( 0x0B, bytearray(), address )

    def setOutputPower(self, power, address=0):
        packet = self.sendCommand( 0x04, bytearray([power]), address )
        if packet.failed():
            raise PacketError( packet )

        return True

    def setFrequency(self, fmin, fmax, address=0):
        packet = self.sendCommand( 0x05, bytearray([fmin, fmax]) )

    def readParam(self, address=0):
        packet = self.sendCommand( 0x06, bytearray(), address )

    def setParam(self, params, address=0):
        raise NotImplementedError()
        # packet = self.sendCommand( 0x09, bytearray(), address )

    def readAutoParam(self, address=0):
        packet = self.sendCommand( 0x14, bytearray(), address )

    def setAutoParam(self, params, address=0):
        raise NotImplementedError()
        # packet = self.sendCommand( 0x13, bytearray(), address )

    def selectAntenna(self, antenna, address=0):
        packet = self.sendCommand( 0x0A, bytearray([ 1 << ( antenna - 1 ) ]), address )

    def restoreFactorySettings(self, address=0):
        packet = self.sendCommand( 0x0D, bytearray(), address )

    def reboot(self, address=0):
        packet = self.sendCommand( 0x0E, bytearray(), address )

    def setAutoMode(self, enabled, address=0):
        packet = self.sendCommand( 0x0F, bytearray([enabled]), address )

    def clearMemory(self, address=0):
        packet = self.sendCommand( 0x10, bytearray(), address )

    def setReaderTime( self, time, address=0 ):
        raise NotImplementedError()
        # packet = self.sendCommand( 0x11, bytearray(), address )

    def getReaderTime( self, address=0 ):
        packet = self.sendCommand( 0x12, bytearray(), address )

    def setReportFilter( self, filter, address=0 ):
        raise NotImplementedError()
        # packet = self.sendCommand( 0x15, bytearray(), address )

    def getReportFilter(self, address=0):
        packet = self.sendCommand( 0x16, bytearray(), address )

    def setReaderNetworkAddress(self, ip : str, port : int, mask : str, gateway : str, address=0):
        ipData = [int(s) for s in ip.split('.')]
        portData = int.to_bytes(self.port, length=2, byteorder="big")
        maskData = [int(s) for s in mask.split('.')]
        gatewayData = [int(s) for s in gateway.split('.')]

        packetData = bytearray( ipData ) + portData + bytearray( maskData + gatewayData )
        packet = self.sendCommand( 0x30, packetData, address )

    def getReaderNetworkAddress(self, address=0):
        packet = self.sendCommand( 0x31, bytearray(), address )

    def setReaderMac(self, mac, address=0):
        packet = self.sendCommand( 0x32, bytearray([int(s, 16) for s in self.mac.split('-')]), address )

    def getReaderMac(self, address=0):
        packet = self.sendCommand( 0x33, bytearray(), address )

    def reportNow(self, address=0):
        packet = self.sendCommand( 0x54, bytearray(), address )

    def getTagInfo(self, startAddress, recordSize, address=0):
        raise NotImplementedError()
        # packet = self.sendCommand( 0x57, bytearray(), address )

    def setReaderID(self, readerID, address=0):
        raise NotImplementedError()
        # packet = self.sendCommand( 0x8B, bytearray(), address )

    def getReaderID(self, address=0):
        packet = self.sendCommand( 0x8C, bytearray(), address )

    def listTagId(self, memoryBank, memoryPtr, maskSize, mask : bytearray, address=0):
        packetData = bytearray([memoryBank]) # Param 1: memory bank
        packetData += int.to_bytes( memoryPtr, length=2, byteorder="big") # Param 2: start address of mask?
        packetData += bytearray([maskSize]) # Param 3: size of mask in bits
        packetData += mask # Param 4: mask data bytes

        packet = self.sendCommand( 0xEE, packetData, address )
        if packet.failed():
            if packet.getErrorCode() == 0x02: # No Tag detected:
                return []    
                
            raise PacketException( packet )

        packetData = packet.packetData

        tagIDs = []
        ptr = 1

        numTags = packetData[0]
        for i in range( numTags ):
            count = packetData[ptr]
            startOfId = ptr + 1
            endOfId = ptr + 1 + 2*count
            tagIDs.append( bytes2HexString( packetData[ startOfId : endOfId ] ) )

            ptr = endOfId + 1
            
        return tagIDs
        
    def readWordBlock(self, tagId : str, memoryBank, startAddress, numWords, password : str, address=0):
        tagIdBytes = hexString2Bytes( tagId )
        tagIdWordCount = len( tagIdBytes ) // 2

        assert len( password ) == 8

        packetData = bytearray([tagIdWordCount]) # Param 1: word count of tag id
        packetData += tagIdBytes # Param 2: tag id in bytes
        packetData += bytearray([memoryBank]) # Param 3: memory bank
        packetData += bytearray([startAddress]) # Param 4: start address for reading
        packetData += bytearray([numWords]) # Param 5: length of data in word count
        packetData += hexString2Bytes( password ) # Param 6: password

        packet = self.sendCommand( 0xEC, packetData, address )
        if packet.failed():
            if packet.getErrorCode() == 0x02: # no tag detected
                return None

            raise PacketException( packet )

        return packet.packetData

    def writeWordBlock(self, tagId : str, memoryBank, startAddress, data : bytearray, password : str, address=0):
        tagIdBytes = hexString2Bytes( tagId )
        tagIdWordCount = len( tagIdBytes ) // 2

        assert len( password ) == 8

        packetData = bytearray([tagIdWordCount]) # Param 1: word count of tag id
        packetData += tagIdBytes # Param 2: tag id in bytes
        packetData += bytearray([memoryBank]) # Param 3: memory bank
        packetData += bytearray([startAddress]) # Param 4: start address for reading
        packetData += bytearray([len(data) // 2]) # Param 5: length of data in word count
        packetData += data # Param 6: data
        packetData += hexString2Bytes( password ) # Param 7: password 
        
        packet = self.sendCommand( 0xEB, packetData, address )

        if packet.failed():
            if packet.getErrorCode() == 0x02: # No tag detected
                return False

            raise PacketException( packet )
        
        return True