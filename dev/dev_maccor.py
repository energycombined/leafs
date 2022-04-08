from pathlib import Path
import sys 

sys.path.append("/Users/thomasvandijk/Documents/LEAFS - github/leafs/leafspy")

import data_handler
import cellpy

filename = "/Users/thomasvandijk/Documents/LEAFS - github/leafs/test_data/Charge-discharge/Maccor/SIM-A7-1039 - 073.txt"

# print(filename.is_file())

instrument, test_type, extension = (
    "MACCOR-UBHAM",
    "CHARGE-DISCHARGE-GALVANOSTATIC CYCLING",
    "TXT",
)

# cellpy_instrument = data_handler._cellpy_instruments(instrument, test_type, extension)
# print(cellpy_instrument)
cellpy_instrument = "maccor_txt"
d = cellpy.get(
            filename=filename, instrument=cellpy_instrument, model='WMG_SIMBA')
c = d.cell
df_raw = c.raw

# d = cellpy.get(filename=filename, instrument=cellpy_instrument, sep="\t")
raw = d.cell.raw
print(raw.columns)
print("OK")

