class InputState:
    # TODO: Accept a callback for generating input
    def __init__(self):
        pass

    def poll(self):
        pass

    def state(self, port: int, device: int, index: int, id: int) -> int:
        pass