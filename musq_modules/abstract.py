class mm_abstract:
    prefix=""
    name=""
    description=""
    version=""
    __settings={}

# TODO: does not work for outputs yet
    def __init__(self):
        print("initted abstract musq module")

    def test(self):
        print("testing abstract musq module")

    def set_creator(self, creator):
        self.creator = creator

    def set_settings(self, settings):
        self.__settings = settings
