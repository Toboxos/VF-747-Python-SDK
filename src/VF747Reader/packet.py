def BYTE( value ):
    return value % 0x100

def computeChecksum( data : bytearray ):
    sum = 0
    for i in range( len(data) ):
        sum = BYTE( sum + data[i] )

    sum = BYTE( (sum ^ 0xFF) + 1  )
    return sum

class Packet:
    def __init__(self, bootCode, commandCode, packetData ):
        super().__init__()
        self.bootCode = bootCode
        self.commandCode = commandCode
        self.packetData = packetData

    def readFrom(stream):
        bootCode, length = stream.read(2)
        data = stream.read( length )

        commandCode = data[0]
        packetData = data[1:-1]
        checksum = data[-1]

        return Packet(bootCode, commandCode, packetData)

    def build(self) -> bytearray:
        packetLen = 2 + len( self.packetData )
        data = bytearray(
            [self.bootCode] + [packetLen] + [self.commandCode]
        ) + self.packetData
        checksum = computeChecksum( data )

        return data + bytearray([checksum])

    def asHexString(self):
        data = self.build()
        
        s = ""
        for c in data:
            s += "{:02x} ".format( c )

        return s.strip()

    def failed(self) -> bool:
        return self.bootCode == 0xF4

    def getErrorCode(self):
        return self.packetData[0]

    def getErrorMessage(self):
        code = self.getErrorCode()

        if code == 0x00:
            return "Command success or detect correct"

        if code == 0x01:
            return "Antenna connection fail"

        if code == 0x02:
            return "Detect no tag"

        if code == 0x03:
            return "illegal tag"

        if code == 0x04:
            return "read write power is inadequate"

        if code == 0x05:
            return "Write protection in this area"

        if code == 0x06:
            return "Checksum error"

        if code == 0x07:
            return "Parameter wrong"

        if code == 0x08:
            return "Nonexistent data area"

        if code == 0x09:
            return "Wrong password"

        if code == 0x0A:
            return "kill password can’t be 0"

        if code == 0x0B:
            return "When reader in Auto mode, the command is illegal."
        
        if code == 0x0C:
            return "Illegal user with unmatched password"

        if code == 0x0D:
            return "RF interference from external"

        if code == 0x0E:
            return "Read protection on tag"

        if code == 0x1E:
            return "Invalid command, such as wrong parameter command"

        if code == 0x1F:
            return "Unknown command"

        if code == 0x20:
            return "Other error"

        return "Unknown error code"

class AddressedPacket(Packet):
    def __init__(self, bootCode, commandCode, address, packetData ):
        super().__init__( bootCode, commandCode, packetData )
        self.address = address

    def readFrom(stream):
        bootCode, length = stream.read()
        data = stream.read( length )

        commandCode = data[0]
        address = data[1]
        packetData = data[2:-1]
        checksum = data[-1]

        return AddressedPacket(bootCode, commandCode, address, packetData)

    def build(self) -> bytearray:
        packetLen = 3 + len( self.packetData )
        data = bytearray(
            [self.bootCode] + [packetLen] + [self.commandCode] + [self.address] 
        ) + self.packetData
        checksum = computeChecksum( data )

        return data + bytearray([checksum])

class PacketError(Exception):

    def __init__(self, packet : Packet) -> None:
        self.packet = packet
        super().__init__( packet.getErrorMessage() )
