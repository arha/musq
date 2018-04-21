import logging

class SerialPacketizer:
  data = b''

  def __init__(self):
    self.log = logging.getLogger('arha.serialbox.SerialPacketizer')
    self.log.info("init")

  def feed(self, byte):
    """ puts a single byte to the in buffer of the packetizer """

  def feedString(self, string, encoding="UTF-8"):
    """ converts a string to a bunch of bytes, and feeds it to the packetizer FSM """

  def prepare(self, string, encoding="UTF-8"):
    """ converts a string to a bunch of UTF-8 bytes (or a custom encoding) returns a byte array that will be correctly decoder by feedString """

  def _dummyCallback(self, data):
    """ dummy callback """
    logging.debug("dummy callback on data >%s<" % data)

class LaxCRLFPacketizer(SerialPacketizer):
  def prepare(self, string, encoding="UTF-8"):
    data_bytes = (string + "\r\n").encode(encoding)
    return data_bytes

  def __init__(self):
    self.packetAssembledCallback = self._dummyCallback
    logging.info("init")

  def feed(self, byte):
    self.data += byte
    self._stepFSM()

  def feedString(self, string, encoding="UTF-8"):
    try:
      data = string.encode(encoding)
    except:
      data = string
      """ eh, maybe it's already bytes """
    for i in range(len(data)):
      self.feed(data[i:i+1])

  def _stepFSM(self):
    """ runs a single step through the FSM packet decoder, used when appending a byte. mostly internal """
    lastByte = self.data[-1:]
    # logging.info("FSM step, last byte: >%s<" % lastByte)
    if lastByte == b'\n' or lastByte == b'\r':
      #logging.info("TOKEN")
      packet = self.data[:-1]
      self.data = b''
      if packet != b'\r' and packet != b'\n' and packet != b'':
        # logging.info("packet: >%s<, remains >%s<" % (packet, self.data))
        self.packetAssembledCallback(packet)