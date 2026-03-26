import os

import matplotlib.pyplot as plt
import pandas as pd


def plot_model_comparison(csv_path: str = "results/model_comparison.csv") -> None:
    """
    Create a simple bar plot comparing models on a chosen metric.

    Saves the figure to results/model_comparison_bar.png.
    """
    df = pd.read_csv(csv_path)

    os.makedirs("results", exist_ok=True)

    # You can switch this to "Accuracy", "Precision", or "Recall" as needed.
    metric = "F1"

    plt.figure(figsize=(6, 4))
    plt.bar(df["Model"], df[metric], color=["tab:blue", "tab:orange", "tab:green"])
    plt.ylabel(metric)
    plt.title(f"Model Comparison ({metric})")
    plt.ylim(0, 1)

    for i, value in enumerate(df[metric]):
        plt.text(i, value + 0.005, f"{value:.3f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    plt.savefig("results/model_comparison_bar.png")
    plt.close()


if __name__ == "__main__":
    plot_model_comparison()

