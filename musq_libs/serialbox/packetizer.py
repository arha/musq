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

class SLIP1055Packetizer(SerialPacketizer):
  # rick adams' SLIP
  # https://tools.ietf.org/html/rfc1055
  END = 0xC0
  ESC = 0xDB
  ESC_END = 0xDC
  ESC_ESC = 0xDD

  STATE_NORMAL = 0
  STATE_ESC = 1

  state = STATE_NORMAL

  def prepare(self, string, encoding="UTF-8"):
    result = bytearray()
    # send an initial END character to flush out any data that may
    # have accumulated in the receiver due to line noise
    result.append(self.END)
    input = string.encode(encoding)
    print ("encoded string: >%s<" % input )
    for c in input:
      if c == self.END:
        result.append(self.ESC)
        result.append(self.ESC_END)
      elif c == self.ESC:
        result.append(self.ESC)
        result.append(self.ESC_ESC)
      else:
        result.append(c)

    result.append(self.END)
    return bytes(result)

  def feed(self, byte):
    self._stepFSM(byte)

  def feedString(self, string, encoding="UTF-8"):
    try:
      data = string.encode(encoding)
    except:
      data = string
      """ eh, maybe it's already bytes """
    for i in range(len(data)):
      self.feed(data[i:i + 1])

  def _stepFSM(self, byte):
    byte_value = ord(byte)
    """ runs a single step through the FSM packet decoder, used when appending a byte. internal use """
    # logging.info("FSM step, last byte: >%s<" % lastByte)

    if byte_value == self.ESC_END and self.state == self.STATE_ESC:
      self.state = self.STATE_NORMAL
      self.data += bytes ( [self.END] )
    elif byte_value == self.ESC_ESC and self.state == self.STATE_ESC:
      self.state = self.STATE_NORMAL
      self.data += bytes( [self.ESC] )
    elif self.state == self.STATE_ESC and (byte != self.ESC_ESC and byte_value != self.ESC_END):
      self.state = self.STATE_NORMAL
      logging.warning("WARNING: got ESCAPED byte [%s] which does not need escaping" % byte)
    elif byte_value == self.ESC:
      self.state = self.STATE_ESC
      # this writes nothing into the buffer, it's simply an in-band control character
    elif byte_value == self.END:
      self.state = self.STATE_NORMAL
      packet = self.data
      self.data = b''
      if packet != b'':
        # logging.info("packet: >%s<, remains >%s<" % (packet, self.data))
        self.packetAssembledCallback(packet)
      else:
        logging.debug("Discarded empty packet")
    else:
      self.data += byte