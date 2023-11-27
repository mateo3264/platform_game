import pygame as pg
from pygame import midi
#todo: make an object which holds 
# all the parameters pass to this function
# to only pass the object

class MidiPlayer:
    def __init__(self, game, midi_notes):
        self.game = game
        
        self.midi_notes = midi_notes
        self.last_midi_update = 0
        self.midi_idx = 0
    def play_midi_note(self):
        now = pg.time.get_ticks()
        
        if now - self.last_midi_update > 500:
            self.last_midi_update = now
            if self.midi_idx == 0:
                vol = 100
            else:
                vol = 80
            self.game.midi_output.note_on(self.midi_notes[self.midi_idx], vol)
            self.midi_idx = (self.midi_idx + 1) % len(self.midi_notes)
        
        return self.midi_notes[(self.midi_idx - 1) % len(self.midi_notes)]