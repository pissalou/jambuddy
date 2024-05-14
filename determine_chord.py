from mingus.core import chords
import random

print(chords.determine('A C# E G'.split(), shorthand=True))
# expected ['A7', 'C#dim|AM']
print(chords.determine('D F# A C E'.split(), shorthand=True))
# expected ['D9', 'Am|DM', 'Am|D7', 'F#m7b5|DM', 'F#m7b5|D7']
print(chords.determine(["C", "E", "G"]))
print(chords.determine('C E G'.split()))
print(chords.determine('D F# A'.split()))
print(chords.determine('A F# D'.split()))
# print(chords.determine('F# D A'.split()))

print(chords.determine('A F# A'.split()))

dyad = ['A', 'F#', 'A']
reoccuring_note = next(iter([pitch for pitch, occurence in {note: dyad.count(note) / len(dyad) for note in dyad}.items() if occurence >= 0.5]), None)
print(reoccuring_note)


notes = ['D', 'F#', 'A']
# while 1:
#     random.shuffle(notes)
#     print(chords.determine(notes))
