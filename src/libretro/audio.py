from array import array


class AudioState:
    def __init__(self):
        self._buffer = array('h')

    def audio_sample(self, left: int, right: int):
        self._buffer.append(left)
        self._buffer.append(right)

    def audio_sample_batch(self, data: bytes) -> None:
        self._buffer.frombytes(data)

    @property
    def buffer(self) -> array:
        return self._buffer
