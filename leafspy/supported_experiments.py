"""Currently supported tests and instruments."""

# TODO: check if we can refactor this using dataclasses.
# TODO: since this module is responsible for tracking supported experiments, it makes sense that it also includes
#  the method that does the check (move from flask_server.py).

accepted_files = ["MPR", "RES", "TXT"]
accepted_tests = [
    "VOLTAMMETRY-CYCLIC VOLTAMMETRY (CV)",
    "CHARGE-DISCHARGE-GALVANOSTATIC CYCLING",
    "EIS",
    "XRD",
]
accepted_instruments = [
    "ARBIN-BT-2000",
    "BIOLOGIC-VMP3",
    "BIOLOGIC-MPG2",
    "STOE-STADI P",
    "MACCOR-UBHAM",
]
used_functions = ["galvani", "cellpy", "xrd_custom"]


# file -> test -> instrument --> used function

accepted_combinations = {
    0: {0: {1: "galvani", 2: "galvani"},},
    1: {1: {0: "cellpy"},},
    2: {1: {4: "cellpy"}, 3: {3: "xrd_custom"}},
}
