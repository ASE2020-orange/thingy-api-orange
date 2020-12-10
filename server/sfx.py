import time


def pou_pi(play):
    play(notes["g5"], 0.1)
    play(notes["c6"], 0.15)

def pi_pou(play):
    play(notes["c6"], 0.1)
    play(notes["g5"], 0.15)


def note(n, duration, blank_time, play):
    play(notes[n], duration)
    time.sleep(blank_time)

def ff7_victory_fanfare(play):
    noir = 60.0 / 130.0 # 130 bpm
    blank_time = noir / 9
    note("c5", noir / 3, blank_time, play)
    note("c5", noir / 3, blank_time, play)
    note("c5", noir / 3, blank_time, play)
    note("c5", noir, blank_time, play)
    note("g4#", noir, blank_time, play)
    note("a4#", noir, blank_time, play)
    note("c5", noir / 3 * 2, blank_time, play)
    note("a4#", noir / 3, blank_time, play)
    note("c5", noir * 3, blank_time, play)

def smb_game_over(play):
    noir = 60.0 / 120.0 # 100 bpm
    blank_time = noir / 9
    note("c5", noir, noir / 2, play)
    note("g4", noir / 2, noir, play)
    note("e4", noir, blank_time, play)
    note("a4", 2/3 * noir, blank_time, play)
    note("b4", 2/3 * noir, blank_time, play)
    note("a4", 2/3 * noir, blank_time, play)
    note("g4#", noir, blank_time, play)
    note("a4#", noir, blank_time, play)
    note("g4#", noir, blank_time, play)
    note("g4", 3 * noir, blank_time, play)

notes = {
    "": 0,
    "a3": 220.0000,
    "a3#": 233.0819,
    "b3": 246.9417,
    "c4": 261.6256,
    "c4#": 277.1826,
    "d4": 293.6648,
    "d4#": 311.1270,
    "e4": 329.6276,
    "f4": 349.2282,
    "f4#": 369.9944,
    "g4": 391.9954,
    "g4#": 415.3047,
    "a4": 440.0000,
    "a4#": 466.1638,
    "b4": 493.8833,
    "c5": 523.2511,
    "c5#": 554.3653,
    "d5": 587.3295,
    "d5#": 622.2540,
    "e5": 659.2551,
    "f5": 698.4565,
    "f5#": 739.9888,
    "g5": 783.9909,
    "g5#": 830.6094,
    "a5": 880.0000,
    "a5#": 932.3275,
    "b5": 987.7666,
    "c6":1046.502,
    "c6#":1108.731,
    "d6":1174.659,
}

songs = {
    "CORRECT": pou_pi,
    "INCORRECT": pi_pou,
    "VICTORY": ff7_victory_fanfare,
    "DEFEAT": smb_game_over,
}
