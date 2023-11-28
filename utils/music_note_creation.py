from music21 import note, stream 
import random
import os
from os import path

RANGE_OF_NOTES = (48, 61)
NUMBER_OF_NOTES = 5
def create_seq_notes():
    notes = [note.Note(midi=random.randrange(*RANGE_OF_NOTES)) for _ in range(NUMBER_OF_NOTES)]
    midi_notes = [n.pitch.midi for n in notes]
    rel_path = '../tile_based/snd/'

    abs_path = path.abspath(rel_path)

    with open(path.join(rel_path, 'midi_notes.txt'), 'w') as f:
        f.write(','.join([str(mn) for mn in midi_notes]))

    s = stream.Stream(notes)
    n_scores = 0
    for file in os.listdir(rel_path):
        if 'score' in file and 'png' in file:
            n_scores += 1
        
    print('n_scores: ', n_scores)
    s.write('lilypond.png', path.join(rel_path, f'score{n_scores + 1}'))

    return midi_notes

if __name__ == '__main__':
    create_seq_notes()








