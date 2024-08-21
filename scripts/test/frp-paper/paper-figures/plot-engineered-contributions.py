#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import numpy as np
import xarray as xr
import matplotlib
import matplotlib.pyplot as plt

from context import data_dir, root_dir

mlp_test_case = "MLP_64U-Dense_64U-Dense_1U-Dense"
method = "averaged-v14"
ml_pack = "tf"
target_vars = "FRP"
model_dir = str(data_dir) + f"/mlp/{ml_pack}/{method}/{target_vars}/{mlp_test_case}"

feature_info = np.loadtxt(
    f"{model_dir}/feature_contribution.txt", delimiter=",", dtype=str
)

# Plot the feature contributions
feature_contributions = feature_info[0].astype(float)
remove_hyphen = np.vectorize(lambda x: x.replace("-", " "))
feature_names = remove_hyphen(feature_info[1])

plt.figure(figsize=(10, 6))
plt.bar(feature_names, feature_contributions, color="skyblue")
plt.xlabel("Input Variable")
plt.ylabel("Relative Contribution")
plt.title("Feature Importance using Feature-Reduction Method")
plt.xticks(rotation=20)
plt.tight_layout()
plt.show()
