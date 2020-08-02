import enum
from still import Still

class LayerMode(enum.Enum):
    COPY = "copy"
    ALPHA = "alpha"

class LayerType(enum.Enum):
    ANIM = "anim"
    STILL = "still"

class Layer:
    def __init__(self, lyr, seq):
        self.lyr = lyr
        self.seq = seq

        self.mode = LayerMode(lyr.get("mode", "alpha"))
        self.type = LayerType(lyr.get("type", "still"))
        self.disable = lyr.get("disable", False)
        self.active = not self.disable

        if self.type == LayerType.STILL:
            l = lyr["still"]
            if isinstance(l, str):
                l = self.seq.stills[l]
        else:
            l = lyr["anim"]
            if isinstance(l, str):
                l = self.seq.anims[l]
        if isinstance(l, dict):
            l = Still(l)
        # else assume is a Still already.
        self.still = l

        if self.active and self.is_still:
            self.still.cache_image(self.seq)

    @property
    def is_still(self):
        return self.type == LayerType.STILL

    @property
    def is_anim(self):
        return self.type == LayerType.ANIM

    @property
    def copy_layer(self):
        return self.mode == LayerMode.COPY

    @property
    def alpha_layer(self):
        return self.mode == LayerMode.ALPHA