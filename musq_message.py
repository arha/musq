#!/usr/bin/python3

from enum import Enum

class musq_payload_type(Enum):
    plain = 1
    json = 2

class musq_message:
    topic = ""
    payload = b''
    
