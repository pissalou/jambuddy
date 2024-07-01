from mido import MidiFile, tempo2bpm


def extract_bpm(mid: MidiFile):
    meta_msgs = [msg for msg in list(mid) if msg.is_meta]
    return tempo2bpm([meta_msg.tempo for meta_msg in meta_msgs if meta_msg.type == 'set_tempo'][0])
