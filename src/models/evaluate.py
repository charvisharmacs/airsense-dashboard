import pandas as pd


def show_model_comparison():
    df = pd.read_csv("results/model_comparison.csv")
    print(df)