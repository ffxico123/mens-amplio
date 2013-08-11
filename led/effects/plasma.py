import math
import noise
import numpy
from base import EffectLayer, HeadsetResponsiveEffectLayer


class PlasmaLayer(EffectLayer):
    """A plasma cloud layer, implemented with smoothed noise.

       If 'color' is None, this modulates the brightness of the framebuffer's
       existing contents. Otherwise, it's a color 3-tuple.
       """

    def __init__(self, color=None, zoom=0.6):
        self.zoom = zoom
        self.octaves = 3
        self.color = None if color is None else numpy.array(color)
        self.time_const = -1.5
        self.modelCache = None
        self.ufunc = numpy.frompyfunc(noise.pnoise3, 4, 1)

    def render(self, model, params, frame):
        # Noise spatial scale, in number of noise datapoints at the fundamental frequency
        # visible along the length of the sculpture. Larger numbers "zoom out".
        # For perlin noise, we have multiple octaves of detail, so staying zoomed in lets
        # us have a lot of detail from the higher octaves while still having gradual overall
        # changes from the lower-frequency noise.

        s = self.zoom # defaults to 0.6

        # Time-varying vertical offset. "Flow" upwards, slowly. To keep the parameters to
        # pnoise3() in a reasonable range where conversion to single-precision float within
        # the module won't be a problem, we need to wrap the coordinates at the point where
        # the noise function seamlessly tiles. By default, this is at 1024 units in the
        # coordinate space used by pnoise3().

        z0 = math.fmod(params.time * self.time_const, 1024.0)

        # Cached values based on the current model
        if model is not self.modelCache:
            self.modelCache = model
            self.scaledX = s * model.edgeCenters[:,0]
            self.scaledY = s * model.edgeCenters[:,1]
            self.scaledZ = s * model.edgeCenters[:,2]

        # Compute noise values at the center of each edge
        noise = self.ufunc(self.scaledX, self.scaledY, self.scaledZ + z0,
            self.octaves).astype(frame.dtype)

        # Brightness scaling
        numpy.add(noise, 0.35, noise)
        numpy.multiply(noise, 1.2, noise)

        if self.color is None:
            # Multiply by framebuffer contents
            numpy.multiply(frame, noise.reshape(-1, 1), frame)
        else:
            # Multiply by color, accumulate into current frame
            numpy.add(frame, self.color * noise.reshape(-1, 1), frame)