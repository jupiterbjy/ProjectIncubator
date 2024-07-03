import pathlib

import pandas as pd


data = """
0.7319,0.1979,0.4434,0.1862,0.9935
0.9294,0.1011,0.9114,0.1939,0.838
0.2386,0.1529,0.8174,0.3015,0.2691
0.6291,0.8105,0.5586,0.5512,0.3286
0.8575,0.0055,0.0441,0.2989,0.0135
0.331,0.0968,0.89,0.8253,0.2725
0.7356,0.8136,0.5955,0.0051,0.7264
0.6151,0.7336,0.275,0.5213,0.47
0.9855,0.9211,0.1162,0.0454,0.838
0.4032,0.9121,0.8177,0.519,0.5087
"""

ROOT = pathlib.Path(__file__).parent
FILE = ROOT / "data.csv"

# just writing data file so code run without any external file
FILE.write_text(data)


# this way read_csv infer column names from first row
csv_data_0 = pd.read_csv(FILE)

# this doesn't do a thing. Already header=0 is default as we have no name to pass.
csv_data_1 = pd.read_csv(FILE, header=0)

# this way read_csv does not infer column names. no header so header=None.
csv_data_2 = pd.read_csv(FILE, header=None)


print(csv_data_0, csv_data_1, csv_data_2, sep="\n\n")
