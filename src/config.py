import numpy as np
import random
import os

SEED = 42

def set_seed():

    random.seed(SEED)
    np.random.seed(SEED)

    os.environ["PYTHONHASHSEED"] = str(SEED)