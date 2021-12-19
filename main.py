import time
import random
from ReaderAPI import Logger, ReaderAPI, bytes2HexString, hexString2Bytes

Logger.setEnabled( False )
reader = ReaderAPI()

if not reader.connectSerial( "COM5", 115200 ):
    raise RuntimeError("Cannot connect serial" )
print("Connected")

hwVersion, swVersion = reader.getReaderVersion()
print( f"{hwVersion=}  {swVersion=}" )

reader.selectAntenna(1)

PASSWORD = "00000000"
TAG = "E20090553315009020803EE8"

def tagDetected(reader, tagId):
    for tag in reader.listTagId( reader.MEM_EPC, 0, 0, bytearray() ):
        if tag == tagId:
            return True

    return False

# Wait until tag is detected
while not tagDetected(reader, TAG):
    time.sleep( 0.2 )
print( "Tag", TAG, "detected" )

# Read tag data
data = None
while data is None:
    data = reader.readWordBlock( TAG, reader.MEM_USER, 0, 4, PASSWORD )
    time.sleep( 0.2 )
print( "Userdata on the tag:", bytes2HexString(data) )

# Generate random data
data = random.randbytes(4*2)
print( "Write random userdata to tag:", bytes2HexString(data) )
while not reader.writeWordBlock( TAG, reader.MEM_USER, 0, data, PASSWORD ):
    time.sleep( 0.2 )

# Close connection
reader.closeConnection()