import context

import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import zentables as zen

from context import data_dir

model = "wrf"
trail_name = "02"

## define directory to save figures
save_dir = Path(str(data_dir) + f"/images/stats/{trail_name}/{model}/taylor/")
save_dir.mkdir(parents=True, exist_ok=True)

var_list = [
    "temp",
    "rh",
    "ws",
    "precip",
]


# Get the first row of each DataFrame
def loc_df(var):
    df = pd.read_csv(str(data_dir) + f"/intercomp/02/{model}/{var}-stats.csv")
    df["domain"] = df["domain"].str.replace(" ", "")
    df["domain"] = df["domain"].str.replace("-noon", "")
    df["domain"] = df["domain"].str.replace("d02", "12km")
    df["domain"] = df["domain"].str.replace("d03", "4km")
    # df = df.set_index('domain')
    df = df[df["domain"].isin(["12km", "4km"])]
    df.insert(0, "var", [var, var])

    return df


url = (
    "https://raw.githubusercontent.com/thepolicylab"
    "/ZenTables/main/tests/fixtures/superstore.csv?raw=true"
)
super_store = pd.read_csv(url)
df = super_store.pivot_table(
    index=["Segment", "Region"],
    columns=["Category"],
    values="Order ID",
    aggfunc="count",
    margins=True,
)
df
df.to_dict()
df.zen.pretty()


first_rows = pd.concat([loc_df(var) for var in var_list])

# Create a new DataFrame with the merged first rows
merged_df = pd.DataFrame(first_rows)
# # merged_df['var'] = var_list
merged_df = merged_df.drop(["Unnamed: 0", "std_dev", "rms"], axis=1)
merged_df.reset_index(drop=True, inplace=True)
merged_df = merged_df.round(2)
# grouped_df = merged_df.groupby('var')
pivot_df = merged_df.pivot_table(
    index=["var", "domain"],
    # columns=["domain"],
    # values="Order ID",
    # aggfunc="count",
    margins=False,
)
pivot_df.to_dict()

pivot_df = pivot_df.reindex(index=var_list, level=0)

pivot_df.zen.pretty(
    font_size=14,
).format(precision=2)


# # # Read the CSV file into a DataFrame
# # data = pd.read_csv('data.csv')
# data = merged_df
# # Create a figure and axis
# fig, ax = plt.subplots()

# # Hide axiss
# ax.axis('off')

# # Create the table
# table = ax.table(cellText=data.values, colLabels=data.columns, loc='center')
# # Set table properties

# # Set cell colors for pairs of rows
# colors = ['lightblue', 'lightgreen']
# num_rows = len(data['var'])
# for i, key in enumerate(table.get_celld().keys()):
#     if i <= num_rows:
#         continue  # Skip coloring the first row
#     elif (i - num_rows - 1) % 2 == 0:
#         row_num = (i - num_rows - 1) // 2
#         table[key].set_facecolor(colors[row_num % 2])

# # Save the figure as a PDF file
# # plt.savefig('table.pdf', format='pdf')

# # Show the table (optional)
# plt.show()


# %%
