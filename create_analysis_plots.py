import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

import ast

# FUNCTIONS
def plot_hist(series, bins, filename, rwidth=0.8, xlabel=None, title=None):
    """Histogram a series with consistent styling and save it to disk."""
    ax = series.hist(bins=bins, rwidth=rwidth)
    ax.set_xticks(bins)
    if xlabel:
        ax.set_xlabel(xlabel)
    if title:
        ax.set_title(title)
    ax.figure.savefig(filename)
    plt.close(ax.figure)  # avoid leaking open figures across the loop
    return ax

# One entry per plot: (column, bins, filename, title)
PLOT_CONFIG = [
    (
        "program_length_weeks",
        np.arange(1, 19),
        "program_length_weeks.png",
        "Program Length (Weeks)",
    ),
    (
        "program_length_days",
        np.arange(1, 110, 10),
        "program_length_days.png",
        "Program Length (Days)",
    ),
    (
        "average_intensity",
        np.arange(4.5, 10.5, 0.5),
        "average_intensity.png",
        "Average Intensity",
    ),
    (
        "avg_days_per_week",
        np.arange(1, 9),
        "average_days_per_week.png",
        "Average Days per Week",
    ),
]

def plot_grid(df, config=PLOT_CONFIG, filename="summary_grid.png", ncols=2, figsize=(12, 8)):
    """Render each (column, bins, _, title) entry in config as one panel of
    a grid (2x2 by default) and save the whole grid as a single figure."""
    nrows = -(-len(config) // ncols)  # ceil division
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    axes = axes.flatten()

    for ax, (column, bins, _filename, title) in zip(axes, config):
        df[column].hist(bins=bins, rwidth=0.8, ax=ax)
        ax.set_xticks(bins)
        ax.set_title(title)

    # hide any leftover empty panels (e.g. 3 plots in a 2x2 grid)
    for ax in axes[len(config):]:
        ax.axis("off")

    fig.tight_layout()
    fig.savefig(filename)
    plt.close(fig)
    return fig

# Define the results folder path
results_path = Path("results")

# Create the folder safely
results_path.mkdir(parents=True, exist_ok=True)

# Load the key files (program and exercise summaries)
# 1. Define the base directory generically
DATA_DIR = Path('C:/Users/iamph/OneDrive/Documents/Datasets/Kaggle_Fitness_Workout_Dataset')

# 2. Safely join the path to the file
file_path = DATA_DIR / 'program_summary_CLEAN_260728.csv'
df = pd.read_csv(file_path)

# 3. Safely join the path to the file
file_path = DATA_DIR / 'programs_detailed_boostcamp_kaggle_260812_day_label.csv'

ex = pd.read_csv(file_path)
# Clean/Reorganise values
df['level'] = df['level'].apply(ast.literal_eval)
df['goal'] = df['goal'].apply(ast.literal_eval)
df.level = df.level.apply(set)
df.goal = df.goal.apply(set)

ex['level'] = ex['level'].apply(ast.literal_eval)
ex['goal'] = ex['goal'].apply(ast.literal_eval)
ex.level = ex.level.apply(set)
ex.goal = ex.goal.apply(set)

# New Variables
## Average Days Per week
df['avg_days_per_week'] = df['program_length_days'] / df['program_length_weeks']

# Insert all value_count tables here to write into an excel sheet
tables = {}

# General Statistics
## Level
tables['level'] = df['level'].value_counts()
tables['level_expanded'] = df.level.explode().value_counts()

## Goal
tables['goal'] = df['goal'].value_counts()
tables['goal_expanded'] = df['goal'].explode().value_counts()

## Equipment
tables['equipment'] = df['equipment'].value_counts()

## Time per workout
tables['time_per_workout'] = df['time_per_workout'].value_counts()

## Weeks
tables['program_length_weeks'] = df['program_length_weeks'].value_counts()

## Plots (according to plotting config)
plot_grid(df, filename=results_path / f"summary_grid.png")

## Analyse Workout day type
ex2 = ex.copy(deep = True)
ex2.drop_duplicates(subset=['title','week','day'], inplace = True)
ex2['day_label'] = ex2['day_label'].str.split(", ")
tables['day_label'] = ex2.day_label.value_counts()
tables['day_label_expanded'] = ex2.day_label.explode().value_counts()

## Plot all results
with pd.ExcelWriter(results_path / 'overall_results.xlsx', engine='openpyxl') as writer:
    for key in tables.keys():
        tables[key].to_excel(writer, sheet_name=f'{key}')

# Statistics by Workout Level [including/excluding mixed]
levels = df.level.explode().unique()

# Define the results folder path
results_path2 = results_path / Path('levels')

# Create the folder safely
results_path2.mkdir(parents=True, exist_ok=True)

for level in levels:
    level_title = f'lvl_{level}'
    test = df.level.explode() == level

    df2 = df.loc[test[test == 1].index, :]
    ## Goal
    tables['goal'] = df['goal'].value_counts()
    tables['goal_expanded'] = df['goal'].explode().value_counts()

    ## Equipment
    tables['equipment'] = df['equipment'].value_counts()

    ## Time per workout
    tables['time_per_workout'] = df['time_per_workout'].value_counts()

    ## Weeks
    tables['program_length_weeks'] = df['program_length_weeks'].value_counts()

    ## Plots
    plot_grid(df2, filename=results_path2 / f"summary_grid_{level}.png")

    ## Analyse Workout day type
    ex2 = ex.copy(deep=True)
    ex2.drop_duplicates(subset=['title', 'week', 'day'], inplace=True)
    ex2['day_label'] = ex2['day_label'].str.split(", ")
    tables['day_label'] = ex2.day_label.value_counts()
    tables['day_label_expanded'] = ex2.day_label.explode().value_counts()

    ## Plot all results
    with pd.ExcelWriter(results_path2 /f'overall_results_{level_title}.xlsx', engine='openpyxl') as writer:
        for key in tables.keys():
            tables[key].to_excel(writer, sheet_name=f'{key}')


# Statistics by Workout Goals [including/excluding mixed]
goals = df.goal.explode().unique()

# Define the results folder path
results_path2 = results_path / Path('goals')

# Create the folder safely
results_path2.mkdir(parents=True, exist_ok=True)

for goal in goals:
    goal_title = f'lvl_{goal}'
    test = df.goal.explode() == goal

    df2 = df.loc[test[test == 1].index, :]
    ## Level
    tables['level'] = df['level'].value_counts()
    tables['level_expanded'] = df.level.explode().value_counts()

    ## Equipment
    tables['equipment'] = df['equipment'].value_counts()

    ## Time per workout
    tables['time_per_workout'] = df['time_per_workout'].value_counts()

    ## Weeks
    tables['program_length_weeks'] = df['program_length_weeks'].value_counts()

    ## Plots
    plot_grid(df2, filename=results_path2 / f"summary_grid_{goal}.png")

    ## Analyse Workout day type
    ex2 = ex.copy(deep=True)
    ex2.drop_duplicates(subset=['title', 'week', 'day'], inplace=True)
    ex2['day_label'] = ex2['day_label'].str.split(", ")
    tables['day_label'] = ex2.day_label.value_counts()
    tables['day_label_expanded'] = ex2.day_label.explode().value_counts()

    ## Plot all results
    with pd.ExcelWriter(results_path2 /f'overall_results_{goal_title}.xlsx', engine='openpyxl') as writer:
        for key in tables.keys():
            tables[key].to_excel(writer, sheet_name=f'{key}')


# Statistics by Equipment
equipments = df['equipment'].unique()

# Define the results folder path
results_path2 = results_path / Path('equipments')

# Create the folder safely
results_path2.mkdir(parents=True, exist_ok=True)

for eq in equipments:
    eq_title = f'lvl_{eq}'
    df2 = df[df.equipment == eq]
    ## Level
    tables['level'] = df['level'].value_counts()
    tables['level_expanded'] = df.level.explode().value_counts()

    ## Goal
    tables['goal'] = df['goal'].value_counts()
    tables['goal_expanded'] = df['goal'].explode().value_counts()

    ## Time per workout
    tables['time_per_workout'] = df['time_per_workout'].value_counts()

    ## Weeks
    tables['program_length_weeks'] = df['program_length_weeks'].value_counts()

    ## Plots
    plot_grid(df2, filename=results_path2 / f"summary_grid_{eq}.png")

    ## Analyse Workout day type
    ex2 = ex.copy(deep=True)
    ex2.drop_duplicates(subset=['title', 'week', 'day'], inplace=True)
    ex2['day_label'] = ex2['day_label'].str.split(", ")
    tables['day_label'] = ex2.day_label.value_counts()
    tables['day_label_expanded'] = ex2.day_label.explode().value_counts()

    ## Plot all results
    with pd.ExcelWriter(results_path2 /f'overall_results_{eq_title}.xlsx', engine='openpyxl') as writer:
        for key in tables.keys():
            tables[key].to_excel(writer, sheet_name=f'{key}')