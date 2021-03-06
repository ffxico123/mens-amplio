#!/usr/bin/env python

import time
import numpy
from effects.base import GammaLayer
from playlist import Playlist


class Renderer:
    """
    Renders the selected light routine in the currently active playlist. 
    Performs smooth transitions when the active routine changes (either due to swapping 
    playlists or to advancing the selection in the current playlist).
    
    Also applies a gamma correction layer after everything else is rendered.
    """
    def __init__(self, playlists, activePlaylist=None, useFastFades=False, gamma=2.2):
        # playlists argument should be dictionary of playlist names : playlists.        
        if not playlists:
            raise Exception("Can't define a renderer without any playlists")
        self.playlists = playlists
        
        # activePlaylist is the name of the first playlist to display. Can be
        # omitted if playlists only has one thing in it
        if activePlaylist:
            self.activePlaylist = activePlaylist
        else:
            if len(playlists.keys()) == 1:
                self.activePlaylist = playlists.keys()[0]
            else:
                raise Exception("Can't define multi-playlist renderer without specifying active playlist")
            
        # used when fading between playlists, to know what to return to when the fade is done
        self.nextPlaylist = None 
        
        self.useFastFades = useFastFades
        self.fade = None
        self.gammaLayer = GammaLayer(gamma)
        
    def _get(self, playlistKey):
        if playlistKey:
            return self.playlists[playlistKey]
        else:
            return None
        
    def _active(self):
        return self._get(self.activePlaylist)
        
    def _next(self):
        return self._get(self.nextPlaylist)
        
    def render(self, model, params, frame):
        if self.fade:
            self.fade.render(model, params, frame)
            if self.fade.done:
                # If the fade was to a new playlist, set that one to active
                if self.nextPlaylist:
                    self.activePlaylist = self.nextPlaylist
                    self.nextPlaylist = None
                self.fade = None
        elif self.activePlaylist:
            for layer in self._active().selection():
                layer.safely_render(model, params, frame)
        self.gammaLayer.render(model, params, frame)
        
    def advanceCurrentPlaylist(self, fadeTime=1):
        # Advance selection within current playlist
        active = self._active()
        if active:
            selection = active.selection()
            active.advance()
            self.fade = LinearFade(selection, active.selection(), fadeTime)
        else:
            raise Exception("Can't advance playlist - no playlist is currently active")
        

    def _fadeTimeForTransition(self, playlist):
        return max([effect.transitionFadeTime for effect in playlist.selection()])


    def swapPlaylists(self, nextPlaylist, intermediatePlaylist=None, advanceAfterFadeOut=True, fadeTime=1):
        # Swap to a new playlist, either directly or by doing a two-step fade to an intermediate one first.
        # TODO check for wonky behavior when one fade is set while another is still in progress
        
        active = self._active()
        self.nextPlaylist = nextPlaylist
        
        if self.useFastFades:
            self.fade = FastFade(active.selection(), self._next().selection(), fadeTime)
        else:
            if intermediatePlaylist:
                middle = self._get(intermediatePlaylist)
                self.fade = TwoStepLinearFade(active.selection(), middle.selection(), self._next().selection(), 0.25, self._fadeTimeForTransition(middle))
                if advanceAfterFadeOut:
                    middle.advance()
            else:
                self.fade = LinearFade(active.selection(), self._next().selection(), fadeTime)
        if advanceAfterFadeOut:
            active.advance()

class Fade:
    """
    Renders a smooth transition between multiple lists of effect layers
    """
    def __init__(self, startLayers, endLayers):
        self.done = False # should be set to True when fade is complete
        self.startLayers = startLayers
        self.endLayers = endLayers # final layer list to be rendered after fade is done
    
    def render(self, model, params, frame):
        raise NotImplementedException("Implement in fader subclass")
        
        
class LinearFade(Fade):
    """
    Renders a simple linear fade between two lists of effect layers
    """
    def __init__(self, startLayers, endLayers, duration):
        Fade.__init__(self, startLayers, endLayers)
        self.duration = float(duration)
        # set actual start time on first call to render
        self.start = None
        
    def render(self, model, params, frame):
        if not self.start:
            self.start = time.time()
        # render the end layers
        if self.endLayers:
            for layer in self.endLayers:
                layer.safely_render(model, params, frame)
        percentDone = (time.time() - self.start) / self.duration
        if percentDone >= 1:
            self.done = True
        else:
            # if the fade is still in progress, render the start layers
            # and blend them in
            numpy.multiply(frame, percentDone, frame)
            if self.startLayers:
                frame2 = numpy.zeros(frame.shape)
                for layer in self.startLayers:
                    layer.safely_render(model, params, frame2) 
                numpy.multiply(frame2, 1-percentDone, frame2)
                numpy.add(frame, frame2, frame)
            
            
class TwoStepFade(Fade):
    def __init__(self, fade1, fade2, startLayers, endLayers):
        Fade.__init__(self, startLayers, endLayers)
        self.fade1 = fade1
        self.fade2 = fade2
    
    def render(self, model, params, frame):
        if not self.fade1.done:
            self.fade1.render(model, params, frame)
        else:
            self.fade2.render(model, params, frame)
            self.done = self.fade2.done
            
            
class FastFade(TwoStepFade):
    """
    Fade from startLayers to nothing, then from nothing to endLayers. This should be
    more efficient than fading directly between two layer sets because we 
    never have to render both layer sets at the same time.
    """
    def __init__(self, startLayers, endLayers, duration):
        fade1 = LinearFade(startLayers, None, duration/2.)
        fade2 = LinearFade(None, endLayers, duration/2.)
        TwoStepFade.__init__(self, fade1, fade2, startLayers, endLayers)

            
class TwoStepLinearFade(TwoStepFade):
    """
    Performs a linear fade to an intermediate effect layer list, then another linear
    fade to a final effect layer list. Useful for making something brief and dramatic happen.
    """
    def __init__(self, currLayers, nextLayers, finalLayers, duration_1, duration_2):
        fade1 = LinearFade(currLayers, nextLayers, duration_1)
        fade2 = LinearFade(nextLayers, finalLayers, duration_2)
        TwoStepFade.__init__(self, fade1, fade2, currLayers, finalLayers)
        

