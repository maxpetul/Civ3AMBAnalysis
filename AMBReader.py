
###
###
###
### AMBReader.py is a script I've been using to explore & experiment with AMB files. In the process I've also built it up as an AMB reader, though
### it's by no means a user friendly format loading library.
### BASIC USAGE: First set civ3_root_dir below to your Civ 3 install directory. Then run the script in interactive mode (py -i AMBReader.py). It will
### automatically load all AMBs from your vanilla, PTW, and Conquests installs. You can look up an AMB by name using the "find_amb" method and print
### out its contents using its "describe" method. For example, try:
###   >>> find_amb("TrebuchetRun").describe()
###
###
###

civ3_root_dir = "/media/c/GOG Games/Civilization III Complete/" # "C:\\GOG Games\\Civilization III Complete\\"



import os

civ3_unit_art_paths = [os.path.join (civ3_root_dir             , "Art", "Units"),
                       os.path.join (civ3_root_dir, "civ3PTW"  , "Art", "Units"),
                       os.path.join (civ3_root_dir, "Conquests", "Art", "Units")]

def read_string (_file):
    tr = b""
    while True:
        byte = _file.read (1)
        if byte[0] != 0:
            tr += byte
        else:
            break
    return tr.decode ()

def read_amb_int (_file, unsigned = True):
    return int.from_bytes (_file.read (4), byteorder = "little", signed = not unsigned)

def read_midi_int (_file, unsigned = True):
    return int.from_bytes (_file.read (4), byteorder = "big", signed = not unsigned)

def read_midi_short (_file, unsigned = True):
    return int.from_bytes (_file.read (2), byteorder = "big", signed = not unsigned)

# Reads a "variable length quantity", which is an int made up of a variable number of bytes. Each byte contains 7 bits of the int and the 8th
# (highest) bit determines whether or not the next byte is included as well.
def read_midi_var_int (_file):
    tr = 0
    while True:
        bs = _file.read (1)
        if len (bs) > 0:
            tr = (tr << 7) + (bs[0] & 0x7F)
            if (bs[0] & 0x80) == 0:
                return tr
        else:
            raise Exception ("Unexpected EOF in variable length quantity")

# assert   0       == read_midi_var_int (b"\x00")
# assert 0x40      == read_midi_var_int (b"\x40")
# assert 0x7F      == read_midi_var_int (b"\x7F")
# assert 0x80      == read_midi_var_int (b"\x81\x00")
# assert 0x2000    == read_midi_var_int (b"\xC0\x00")
# assert 0x3FFF    == read_midi_var_int (b"\xFF\x7F")
# assert 0x4000    == read_midi_var_int (b"\x81\x80\x00")
# assert 0x100000  == read_midi_var_int (b"\xC0\x80\x00")
# assert 0x1FFFFF  == read_midi_var_int (b"\xFF\xFF\x7F")
# assert 0x200000  == read_midi_var_int (b"\x81\x80\x80\x00")
# assert 0x8000000 == read_midi_var_int (b"\xC0\x80\x80\x00")
# assert 0xFFFFFFF == read_midi_var_int (b"\xFF\xFF\xFF\x7F")

class Prgm:
    def __init__ (self, amb_file):
        # Size does not include the type tag or size field itself. The AMB reader code checks if size == 0x1C, implying it's possible for prgm chunks
        # to have no strings, but in fact all prgm chunks in Civ 3 do have strings (at least the first prgm chunks in each file do).
        self.size = read_amb_int (amb_file)

        # PRGM chunk number, equals n where this is the n-th PRGM chunk in the file. There is ONE exception to this rule: in ChariotAttack.amb, the
        # 8th PRGM chunk has number 5.
        self.number = read_amb_int (amb_file)

        # Observations about dat fields, by index:
        #   0. One of [0, 1, 2, 3]. 3 is the most common
        #   1. One of [0, 20, 100, 150, 200]. 200 is the most common. 20 occurs once, in PikemanAttackA.amb.
        #   2. Looks like most values are negative
        #   3. One of [0, 25, 127, 1237]. 1237 occurs once, in JaguarWarriorDeath.amb.
        #   4. One of [0, 10, 127, 75, 785]. 75 is the most common.
        #   1 & 2 are upper and lower bounds for randomized playback speed. +/- 100 points corresponds to about +/- 6%.
        #   3 & 4 are upper and lower bounds for randomized volume.
        self.dat = []
        for n in range(5):
            self.dat.append (read_amb_int (amb_file, unsigned = False))

        if read_amb_int (amb_file) != 0xFA:
            raise Exception ("Expected (0x FA 00 00 00) before strings in Prgm chunk in \"" + amb_file + "\"")

        self.str1 = read_string (amb_file) # effect name
        self.str2 = read_string (amb_file) # var name

    def describe (self):
        print ("\tprgm\t" + "\t".join ([str (d) for d in self.dat]) + "\t'" + self.str1 + "'  '" + self.str2 + "'")

class KmapItem:
    def __init__ (self, amb_file, int2, int6):
        if (int2 & 6) == 0: # False for all AMBs in Civ 3
            self.Aint1 = read_amb_int (amb_file)
            self.Aint2 = read_amb_int (amb_file)
        else:
            self.Bdat1 = amb_file.read (int6) # Always 0x (7F 00 00 00 00 00 00 00 01 00 00 00)
        self.str1 = read_string (amb_file)

    def get_description (self):
        return str (self.Bdat1) + "  '" + self.str1 + "'"

class Kmap:
    def __init__ (self, amb_file):
        self.size = read_amb_int (amb_file)

        self.int2 = read_amb_int (amb_file) # flags? Equals 2 for all Kmap chunks in all files
        self.int3 = read_amb_int (amb_file) # Always zero
        self.int4 = read_amb_int (amb_file) # Always zero
        self.str1 = read_string (amb_file)
        self.int5 = read_amb_int (amb_file) # item count

        if (self.int2 & 6) != 0: # True for all AMBs in Civ 3
            self.int6 = read_amb_int (amb_file) # Always 12
        else:
            self.int6 = None

        # In all Civ 3 AMBs, there are 3 chunks with 0 items and all the rest have 1 item
        self.items = []
        for n in range(self.int5):
            self.items.append(KmapItem(amb_file, self.int2, self.int6))

        if read_amb_int (amb_file) != 0xFA:
            raise Exception ("Expected (0x FA 00 00 00) at end of Kmap chunk in \"" + amb_file + "\"")

    def describe (self):
        item_descriptions = [i.get_description () for i in self.items]
        print ("\tkmap\t" + "{}\t{}\t{}\t'{}'\t{}\t{}\t{}".format (self.int2, self.int3, self.int4, self.str1, self.int5, self.int6, str (item_descriptions)))

class Glbl:
    def __init__ (self, amb_file):
        self.size = read_amb_int (amb_file)
        tell0 = amb_file.tell()

        self.int2 = read_amb_int (amb_file) # Always 12
        self.dat1 = amb_file.read (self.int2) # Always 0x (00 00 00 00 00 00 00 00 CD CD CD CD)

        # Dump the rest of the chunk into dat2 for now. The decompiled code to read the rest of the chunk is really weird and maybe corrupt.
        # Dat2 is empty for all chunks in all files
        self.dat2 = amb_file.read (self.size - (amb_file.tell() - tell0))

    def describe (self):
        print ("\tglbl\t" + str (self.int2) + "\t" + str (self.dat1) + "\t" + str (self.dat2))

class MidiTrackName:
    def __init__ (self, midi_file, delta_time):
        self.delta_time = delta_time
        length = read_midi_var_int (midi_file)
        self.name = midi_file.read (length).decode ("utf-8")

    def describe (self, timestamp):
        print ("\t\t\t{:01.3f}\tTrackName '{}'".format (timestamp, self.name))

class MidiSMPTEOffset:
    def __init__ (self, midi_file, delta_time):
        self.delta_time = delta_time
        self.hr = int.from_bytes(midi_file.read (1), "big")
        self.mn = int.from_bytes(midi_file.read (1), "big")
        self.se = int.from_bytes(midi_file.read (1), "big")
        self.fr = int.from_bytes(midi_file.read (1), "big")
        self.ff = int.from_bytes(midi_file.read (1), "big")

    def describe (self, timestamp):
        contents = " ".join ([str(v) for v in [self.hr, self.mn, self.se, self.fr, self.ff]])
        print ("\t\t\t{:01.3f}\tSMPTEOffset {}".format (timestamp, contents))

class MidiTimeSignature:
    def __init__ (self, midi_file, delta_time):
        self.delta_time = delta_time
        self.nn = int.from_bytes(midi_file.read (1), "big")
        self.dd = int.from_bytes(midi_file.read (1), "big")
        self.cc = int.from_bytes(midi_file.read (1), "big")
        self.bb = int.from_bytes(midi_file.read (1), "big")

    def describe (self, timestamp):
        contents = " ".join ([str(v) for v in [self.nn, self.dd, self.cc, self.bb]])
        print ("\t\t\t{:01.3f}\tTimeSignature {}".format (timestamp, contents))

class MidiSetTempo:
    def __init__ (self, midi_file, delta_time):
        self.delta_time = delta_time
        self.microseconds_per_quarter_note = int.from_bytes(midi_file.read (3), "big")

    def describe (self, timestamp):
        print ("\t\t\t{:01.3f}\tSetTempo {}".format (timestamp, self.microseconds_per_quarter_note))

class MidiEndOfTrack:
    def __init__ (self, midi_file, delta_time):
        self.delta_time = delta_time

    def describe (self, timestamp):
        print ("\t\t\t{:01.3f}\tEndOfTrack".format (timestamp))

def is_midi_meta_event (event):
    t = type (event)
    return (t == MidiTrackName) or (t == MidiSMPTEOffset) or (t == MidiTimeSignature) or (t == MidiSetTempo) or (t == MidiEndOfTrack)

class MidiControlChange:
    def __init__ (self, midi_file, delta_time, event_byte):
        self.delta_time = delta_time
        self.channel_number = int.from_bytes (event_byte, "big") & 0xF
        self.controller_number = int.from_bytes (midi_file.read (1), "big")
        if self.controller_number >= 122:
            raise Exception ("This is actually a channel mode message")
        self.value = int.from_bytes (midi_file.read (1), "big")

    def describe (self, timestamp):
        print ("\t\t\t{:01.3f}\tControlChange {} {} {}".format (timestamp, self.channel_number, self.controller_number, self.value))

class MidiProgramChange:
    def __init__ (self, midi_file, delta_time, event_byte):
        self.delta_time = delta_time
        self.channel_number = int.from_bytes (event_byte, "big") & 0xF
        self.program_number = int.from_bytes (midi_file.read (1), "big")

    def describe (self, timestamp):
        print ("\t\t\t{:01.3f}\tProgramChange {} {}".format (timestamp, self.channel_number, self.program_number))

class MidiNoteOff:
    def __init__ (self, midi_file, delta_time, event_byte):
        self.delta_time = delta_time
        self.channel_number = int.from_bytes (event_byte, "big") & 0xF
        self.key = int.from_bytes (midi_file.read (1), "big")
        self.velocity = int.from_bytes (midi_file.read (1), "big")

    def describe (self, timestamp):
        print ("\t\t\t{:01.3f}\tNoteOff {} {} {}".format (timestamp, self.channel_number, self.key, self.velocity))

class MidiNoteOn:
    def __init__ (self, midi_file, delta_time, event_byte):
        self.delta_time = delta_time
        self.channel_number = int.from_bytes (event_byte, "big") & 0xF
        self.key = int.from_bytes (midi_file.read (1), "big")
        self.velocity = int.from_bytes (midi_file.read (1), "big")

    def describe (self, timestamp):
        print ("\t\t\t{:01.3f}\tNoteOn {} {} {}".format (timestamp, self.channel_number, self.key, self.velocity))

class MidiTrackUnknownEvent:
    def __init__ (self, delta_time, sig):
        self.delta_time = delta_time
        self.sig = sig

def read_midi_track_event (midi_file, prev_event):
    delta_time = read_midi_var_int (midi_file)
    byte1 = midi_file.read (1)
    int_byte1 = int.from_bytes (byte1, "big")

    # Implement running status: If the previous event was not a meta-event and the highest bit of the first byte of this event is not set, then this
    # is event inherits the status byte from the previous one, determining its delta time, event type, and channel number
    if (prev_event is not None) and (not is_midi_meta_event (prev_event)) and (0 == (int_byte1 & 0x80)):
        return type (prev_event) (midi_file, prev_event.delta_time, prev_event.channel_number.to_bytes (1, "big"))

    if byte1 == b"\xFF":
        byte2 = midi_file.read (1)
        if byte2 == b"\x03":
            return MidiTrackName (midi_file, delta_time)
        elif byte2 == b"\x2F":
            byte3 = midi_file.read (1)
            if byte3 == b"\x00":
                return MidiEndOfTrack (midi_file, delta_time)
            else:
                return MidiTrackUnknownEvent (delta_time, byte1 + byte2 + byte3)
        elif byte2 == b"\x51":
            byte3 = midi_file.read (1)
            if byte3 == b"\x03":
                return MidiSetTempo (midi_file, delta_time)
            else:
                return MidiTrackUnknownEvent (delta_time, byte1 + byte2 + byte3)
        elif byte2 == b"\x54":
            byte3 = midi_file.read (1)
            if byte3 == b"\x05":
                return MidiSMPTEOffset (midi_file, delta_time)
            else:
                return MidiTrackUnknownEvent (delta_time, byte1 + byte2 + byte3)
        elif byte2 == b"\x58":
            byte3 = midi_file.read (1)
            if byte3 == b"\x04":
                return MidiTimeSignature (midi_file, delta_time)
            else:
                return MidiTrackUnknownEvent (delta_time, byte1 + byte2 + byte3)
        else:
            return MidiTrackUnknownEvent (delta_time, byte1 + byte2)
    elif (int_byte1 >> 4) == 8:
        return MidiNoteOff (midi_file, delta_time, byte1)
    elif (int_byte1 >> 4) == 9:
        return MidiNoteOn (midi_file, delta_time, byte1)
    elif (int_byte1 >> 4) == 0xB:
        return MidiControlChange (midi_file, delta_time, byte1)
    elif (int_byte1 >> 4) == 0xC:
        return MidiProgramChange (midi_file, delta_time, byte1)
    else:
        return MidiTrackUnknownEvent (delta_time, byte1)

class MidiTrack:
    def __init__ (self, midi_file):
        self.size = read_midi_int (midi_file)
        events_starting_offset = midi_file.tell ()
        self.events = []
        while midi_file.tell () < events_starting_offset + self.size:
            event = read_midi_track_event (midi_file, self.events[-1] if len (self.events) > 0 else None)
            self.events.append (event)

            # If we encountered an unknown event, skip the rest of the track data. This is necessary since we couldn't parse this event.
            if type (event) == MidiTrackUnknownEvent:
                self.unknown_event_offset = midi_file.tell ()
                midi_file.read (events_starting_offset + self.size - midi_file.tell ())
                break

    def length (self):
        return sum ([e.delta_time for e in self.events])

    def get_name (self):
        for event in self.events:
            if type (event) == MidiTrackName:
                return event.name
        return None

    def describe (self, seconds_per_tick):
        print ("\t\tTrack:")
        timestamp = 0
        for e in self.events:
            timestamp += e.delta_time * seconds_per_tick
            e.describe (timestamp)

class Midi:
    def __init__ (self, midi_file):
        header_size = read_midi_int (midi_file)
        if header_size != 6:
            raise Exception ("Unexpected MIDI header size: " + str (header_size))
        midi_format = read_midi_short (midi_file)
        if midi_format != 1:
            raise Exception ("Unexpected MIDI format: " + str (midi_format))
        track_count = read_midi_short (midi_file)
        division_info = read_midi_short (midi_file)
        if (division_info >> 15) != 0:
            raise Exception ("Unexpected MIDI division format in: " + hex (division_info))
        self.ticks_per_quarter_note = division_info # Always 480
        self.tracks = []
        for n in range (track_count):
            tag = midi_file.read (4)
            if tag == b"MTrk":
                self.tracks.append (MidiTrack (midi_file))
            elif tag == b"":
                raise Exception ("Unexpected EOF while reading tracks")
            else:
                raise Exception ("Unexpected chunk tag " + tag + " encountered while reading tracks")

        # Read tempo info from SetTempo meta-event in first track
        set_tempos = [e for e in self.tracks[0].events if type (e) == MidiSetTempo]
        if len (set_tempos) != 1:
            raise Exception ("Expected exactly one SetTempo event in first track of file")
        self.seconds_per_quarter_note = set_tempos[0].microseconds_per_quarter_note / 1000000

    def describe (self):
        print ("\tMidi:")
        print ("\t\tticks per quarter note: " + str (self.ticks_per_quarter_note))
        for t in self.tracks:
            t.describe (self.seconds_per_quarter_note / self.ticks_per_quarter_note)

#
# Misc facts about AMB files:
#   Every one begins with a prgm chunk
#   All prgm chunk sizes are strictly greater than 0x1C
#   The number of prgm and kmap chunks does not necessarily match, though it does in almost all cases (there are 4 exceptions)
#

class Amb:
    def __init__ (self, file_path):
        self.file_path = file_path
        with open (file_path, "rb") as amb_file:
            self.chunks = []
            self.midi = None
            while True:
                tag = amb_file.read (4)
                if tag == b"prgm":
                    self.chunks.append (Prgm (amb_file))
                elif tag == b"kmap":
                    self.chunks.append (Kmap (amb_file))
                elif tag == b"glbl":
                    self.chunks.append (Glbl (amb_file))
                elif tag == b"MThd":
                    if self.midi == None:
                        self.midi = Midi (amb_file)
                    else:
                        raise Exception ("File contains multiple MIDI headers")
                elif tag == b"":
                    break # EOF
                else:
                    raise Exception ("Invalid chunk tag " + str(tag) + " at offset " + str(amb_file.tell() - 4))

    def describe (self):
        (_, file_name) = os.path.split (self.file_path)
        print (file_name + ":")
        for c in self.chunks:
            c.describe ()
        self.midi.describe ()

all_amb_paths = []
for art_path in civ3_unit_art_paths:
    for unit_name in os.listdir(art_path):
        unit_folder = os.path.join (art_path, unit_name)
        if os.path.isdir (unit_folder):
            for file_name in os.listdir(unit_folder):
                if file_name.endswith (".amb") or file_name.endswith (".AMB"):
                    all_amb_paths.append (os.path.join (unit_folder, file_name))

print ("Found " + str (len (all_amb_paths)) + " AMB files")

ambs = {}
success_count = 0
for amb_path in all_amb_paths:
    try:
        amb = Amb (amb_path)
        ambs[amb_path] = amb
        success_count += 1
    except Exception as e:
        print ("Failed to load AMB from \"" + amb_path + "\": " + str (e))

print ("Successfully loaded " + str (success_count) + " of " + str (len (all_amb_paths)) + " files")

def find_amb (pattern):
    matches = [k for k in ambs.keys () if pattern in k]
    if len (matches) == 0:
        raise Exception("No match")
    elif len (matches) > 1:
        raise Exception("Pattern is ambiguous. Matches: " + str (matches))
    else:
        return ambs[matches[0]]

def list_all_chunks_of_type (chunk_class):
    tr = []
    for a in ambs.values ():
        tr += [x for x in a.chunks if type (x) == chunk_class]
    return tr

def list_all_midi_tracks ():
    tr = []
    for a in ambs.values ():
        tr += a.midi.tracks
    return tr

def list_all_unknown_midi_track_events ():
    tr = []
    for amb in ambs.values ():
        for track in amb.midi.tracks:
            tr += [e for e in track.events if type (e) == MidiTrackUnknownEvent]
    return tr

def histogram(vals):
    tr = {}
    for v in vals:
        if v in tr:
            tr[v] = tr[v] + 1
        else:
            tr[v] = 1
    return tr

def investigate_format ():
    empty_kmap_count = 0
    one_item_kmap_count = 0
    multiple_items_kmap_count = 0
    for kmap in list_all_chunks_of_type (Kmap):
        if len (kmap.items) == 0:
            empty_kmap_count += 1
        elif len (kmap.items) == 1:
            one_item_kmap_count += 1
        else:
            multiple_items_kmap_count += 1

    print ("No. of KMap chunks with no items: " + str (empty_kmap_count))
    print ("No. of KMap chunks with one item: " + str (one_item_kmap_count))
    print ("No. of KMap chunks with two or more items: " + str (multiple_items_kmap_count))

    all_sound_tracks_have_names = True
    unmatched_effect_name_count = 0
    any_ambiguous_effect_names = False
    for a in ambs.values ():
        for track in a.midi.tracks[1:]: # Skip first track which has metadata
            effect_name = track.get_name ()
            if effect_name is not None and effect_name != "":
                matching_prgm_count = len([x for x in a.chunks if type (x) == Prgm and x.str1 == effect_name])
                if matching_prgm_count == 0:
                    unmatched_effect_name_count += 1
                elif matching_prgm_count > 1:
                    any_ambiguous_effect_names = True
            else:
                all_sound_tracks_have_names = False

    print ("All MIDI sound tracks have non-empty names: " + str (all_sound_tracks_have_names))
    print ("No. of MIDI track names that don't match any PRGM effect names: " + str (unmatched_effect_name_count))
    print ("Any MIDI track names match multiple PRGM effect names: " + str (any_ambiguous_effect_names))

    unreferenced_prgm_chunk_count = 0
    multi_referenced_prgm_chunk_count = 0
    for a in ambs.values ():
        for prgm in a.chunks:
            if type (prgm) == Prgm:
                effect_name = prgm.str1
                ref_count = len([x for x in a.midi.tracks[1:] if x.get_name () == effect_name])
                if ref_count == 0:
                    unreferenced_prgm_chunk_count += 1
                elif ref_count > 1:
                    multi_referenced_prgm_chunk_count += 1

    print ("No. of PRGM chunks with effect names not referenced by any track: " + str (unreferenced_prgm_chunk_count))
    print ("No. of PRGM chunks with effect names referenced by two or more tracks: " + str(multi_referenced_prgm_chunk_count))

    unreferenced_kmap_chunk_count = 0
    multi_referenced_kmap_chunk_count = 0
    for a in ambs.values ():
        for kmap in a.chunks:
            if type (kmap) == Kmap:
                var_name = kmap.str1
                ref_count = len([x for x in a.chunks if type (x) == Prgm and x.str2 == var_name])
                if ref_count == 0:
                    unreferenced_kmap_chunk_count += 1
                elif ref_count > 1:
                    multi_referenced_kmap_chunk_count += 1

    print ("No. of KMAP chunks with var names not referenced by any PRGM: " + str (unreferenced_kmap_chunk_count))
    print ("No. of KMAP chunks with var names referenced by two or more PRGMs: " + str(multi_referenced_kmap_chunk_count))

    any_wave_files_contain_slashes = False
    for kmap in list_all_chunks_of_type (Kmap):
        for item in kmap.items:
            if '/' in item.str1 or '\\' in item.str1:
                any_wave_files_contain_slashes = True

    print ("Any slashes appear in any wave file names: " + str (any_wave_files_contain_slashes))
