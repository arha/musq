import os,binascii

class mm_abstract:
    prefix=""
    name=""
    description=""
    version=""
    settings={}
    my_id="deadbeef"
    creator=-1

# TODO: does not work for outputs yet
    def __init__(self):
        self.prefix="abstract"
        print("initted abstract musq module")

    def test(self):
        print("testing abstract musq module")

    def link(self, creator, settings):
        self.my_id=self.get_id()
        self.creator=creator
        self.settings=settings
        # logger.debug("*** LINKING id=%s, object=%s, creator=%s, settings=%s" % (self.my_id, self, self.creator, self.settings))

    def get_id(self):
        my_id=( "%08X" % (id(self)))
        return my_id
