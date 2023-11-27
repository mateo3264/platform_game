from music21 import note, stream 
import random
from os import path


def create_seq_notes():
    notes = [note.Note(midi=random.randrange(40, 53)) for _ in range(8)]
    midi_notes = [n.pitch.midi for n in notes]
    rel_path = '../tile_based/img/'

    abs_path = path.abspath(rel_path)

    with open(path.join(rel_path, 'midi_notes.txt'), 'w') as f:
        f.write(','.join([str(mn) for mn in midi_notes]))

    s = stream.Stream(notes)

    s.write('lilypond.png', path.join(rel_path, 'score1'))

    return midi_notes








