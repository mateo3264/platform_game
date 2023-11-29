class PatternChecker2:
    def __init__(self, pattern, transposition_interval=0):
        
        self.pattern = pattern
        self.pattern = [note + transposition_interval for note in self.pattern]
        
        self.curr_idx = len(self.pattern) - 1

        self.max_idx = len(self.pattern) - 1

        self.last_timestamp = 0

        self.last_note = None

        self.interval_between_notes = 500
        
        
        self.chord = []
        self.note_idx = None

        self.max_timestamp_chord_interval = 500

        

    def check_pattern(self, midi2events, type='chord', just_once=True):
                
                note_idx = None
                direction = None
                vol = None
                same_chord = False
                notes = []
                #print(midi2events)
                # print('midi2events: ', midi2events)
                #print(list(filter(lambda event : event.data2 != 0, midi2events)))
                for midi_event in midi2events:
                    note = midi_event.data1
                    volume = midi_event.data2
                    timestamp = midi_event.timestamp
                    
                    
                    if type == 'chord':
                            
                            if volume != 0:
                                
                                if note in self.pattern:
                                    
                                    self.chord.append((note, timestamp))
                                    # print(self.chord)
                                if len(self.chord) >= 2:    
                                    timestamp_range = self.chord[-1][1] - self.chord[0][1]
                                    if timestamp_range < self.max_timestamp_chord_interval:
                                        if len(self.chord) >= len(self.pattern):
                                            
                                            if set([n for n, t in self.chord]) == set(self.pattern):
                                                
                                                same_chord = True 
                                            
                                            self.chord = []
                                    else:
                                        self.chord = []
                            else:
                                if self.chord:
                                    if timestamp - self.chord[0][1] > self.max_timestamp_chord_interval:
                                        self.chord = []
                    elif type == 'check-note':
                         if volume != 0:
                              notes.append(note)
                            
                    elif type == 'one-note':
                            if just_once:
                                if volume != 0:
                                    for i in range(len(self.pattern)):
                                        if note == self.pattern[i]:
                                            self.note_idx = i
                                else:
                                     self.note_idx = None
                            else:
                                for i in range(len(self.pattern)):
                                    if note == self.pattern[i]:
                                        if volume == 0:
                                            self.note_idx = None
                                        else:
                                            self.note_idx = i

                                    
                            
                    elif type == 'arpegios':
                            if volume != 0:
                            
                                if timestamp - self.last_timestamp < self.interval_between_notes \
                                        or timestamp - self.last_timestamp > self.interval_between_notes \
                                        and self.last_note is None:
                                    
                                    if note == self.pattern[0] and self.last_note is None:
                                        self.curr_idx = 1#(self.curr_idx + 1) % len(self.pattern)
                                        
                                        
                                        direction = 'right'
                                        vol = volume
                                        self.last_timestamp = timestamp
                                        self.last_note = note
                                    elif note == self.pattern[-1] and self.last_note is None:
                                        self.curr_idx = self.max_idx - 1
                                        
                                        
                                        direction = 'left'
                                        vol = volume
                                        self.last_timestamp = timestamp
                                        self.last_note = note
                                    
                                    elif note == self.pattern[self.curr_idx] \
                                            and self.last_note == self.pattern[self.curr_idx - 1]:
                                        if self.curr_idx < self.max_idx:
                                            self.curr_idx = (self.curr_idx + 1) % len(self.pattern)
                                            self.last_note = note
                                        else:
                                            self.curr_idx = 0
                                            self.last_note = None
                                            
                                        
                                        
                                        direction = 'right'
                                        vol = volume
                                        self.last_timestamp = timestamp
                                        
                                    
                                    elif note == self.pattern[self.curr_idx] \
                                            and self.last_note == self.pattern[self.curr_idx + 1]:
                                        if self.curr_idx > 0:
                                            self.curr_idx -= 1
                                            self.last_note = note   
                                        else:
                                            self.curr_idx = 0
                                            self.last_note = None
                                        
                                        
                                        direction = 'left'
                                        vol = volume
                                        self.last_timestamp = timestamp
                            else:
                                if type != 'chord' and type != 'one-note':
                                        
                                        if timestamp - self.last_timestamp > self.interval_between_notes \
                                                and self.last_note is not None:
                                            
                                            self.curr_idx = 0
                                            self.last_note = None
                                            self.last_timestamp = timestamp

                
                if type == 'chord':
                    # if not same_chord:
                    #      self.chord =
                    return same_chord
                elif type == 'check-note':
                     return notes
                elif type == 'one-note':
                    return self.note_idx
                if vol is not None:
                    return direction, vol
                else:
                    return direction, volume 
