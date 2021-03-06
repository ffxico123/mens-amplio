# Defines full set of lighting effect playlists to use when actually running piece 

from led.effects.base import (
    EffectParameters, SnowstormLayer, TechnicolorSnowstormLayer, WhiteOutLayer, BrainStaticLayer)
from led.effects.digital_rain import DigitalRainLayer
from led.effects.drifters import *
from led.effects.firefly_swarm import FireflySwarmLayer
from led.effects.impulses import *
from led.effects.lightning_storm import LightningStormLayer
from led.effects.plasma import *
from led.effects.waves import WavesLayer
from led.effects.rain import RainLayer
from led.renderer import Playlist

headsetOn = Playlist([
    [
        WavesLayer(inverse=True),
        TimedColorDrifterLayer([ (0,0,0.4) ], 1),
        ImpulseLayer2(),
    ],
    [
        ResponsiveColorDrifterLayer([ (.7,0,.1), (0,0,1) ]),
        ZoomingPlasmaLayer(),
        UpwardImpulseLayer(),
    ],
    [
        TimedColorDrifterLayer([ (0,.3,.1), (0,.1,.3) ], 20),
        FireflySwarmLayer(color=(0.2,0,0.8)),
        ImpulseLayer2(),
    ],
    [
        ResponsiveColorDrifterLayer([ ( 0, .4, 0), (0.1,0.,0.4) ]),
        WavesLayer(inverse=True),
        ImpulseLayer2(),
    ],
    [
        ResponsiveColorDrifterLayer([ (.6,0,.6), (0,0.2,1) ]),
        ZoomingPlasmaLayer(),
        LightningStormLayer()
    ],
    [
        OutwardColorDrifterLayer([ (0,.6,.2), (0,0.2,.6) ], 2),
        BrainStaticLayer(),
        UpwardImpulseLayer()
    ],
])

def make_plasma_playlist(drifters):
    l = []
    for d in drifters:
        rand = random.random()
        routine = [d, PlasmaLayer(zoom=0.2+rand/2)]
        if random.random() < 1:
            routine.append(RainLayer(dropEvery=2+rand*3))
        l.append(routine)
        
    return Playlist(l, shuffle=True)
        
headsetOff = make_plasma_playlist([
        OutwardColorDrifterLayer([ (1,0.1,0.2), (0.2,0.1,1) ], 15), #red/purple/blue
        TreeColorDrifterLayer([ (0.5,1,0.5), (0.5,0.5,1), (0.6,0.1,0.8)], 15), #green/blue, a bit of purple
        OutwardColorDrifterLayer([ (1,.6,.4), (0, 0.2, 1) ], 15), #purple/pink/blue
        TreeColorDrifterLayer([ (1, .8, 0), (0, .9, .5) ], 15), # yellow/orange/green
        OutwardColorDrifterLayer([ (.5, 0, 1), (1, .4, .4) ], 15), #deep pink/blue/purple
        TimedColorDrifterLayer([ (.8, .3, 0), (.6, .6, .8) ], 15), #red/pink/blue
        TreeColorDrifterLayer([ (0.1,1,0.2), (0.1,0.2,1) ], 15), #green/blue
    ])
        
transition = Playlist([
    [WhiteOutLayer()],
    [SnowstormLayer()]
    ])