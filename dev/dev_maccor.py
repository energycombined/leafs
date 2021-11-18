
from pathlib import Path

from leafspy import data_handler
import cellpy

filename = Path("../test_data/Charge-discharge/Maccor/01_UBham_M50_Validation_0deg_01.txt")

print(filename.is_file())

instrument, test_type, extension = (
        "MACCOR-UBHAM",
        "CHARGE-DISCHARGE-GALVANOSTATIC CYCLING",
        "TXT",
    )

cellpy_instrument = data_handler._cellpy_instruments(instrument, test_type, extension)
print(cellpy_instrument)
d = cellpy.get(filename=filename, instrument=cellpy_instrument, sep="\t")
raw = d.cell.raw
print(raw.columns)
print("OK")


