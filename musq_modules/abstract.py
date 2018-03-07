import os,binascii

class mm_abstract:
    prefix=""
    name=""
    description=""
    version=""
    settings={}
    id=""
    creator=0

# TODO: does not work for outputs yet
    def __init__(self):
        print("initted abstract musq module")

    def test(self):
        print("testing abstract musq module")

    def link(self, creator, settings):
        self.id=binascii.b2a_hex(os.urandom(4))
        self.creator=creator
        self.settings=settings
