import pandas as pd

src = "/sessions/clever-nifty-noether/mnt/uploads/programs_detailed_boostcamp_kaggle_LABELLED.csv"
df = pd.read_csv(src)

group_keys = ["title", "week", "day"]

# count exercise_label frequency within each day-group
counts = df.groupby(group_keys + ["exercise_label"]).size().reset_index(name="n")

# for each group, find the max count, then keep all labels tied at that max
max_n = counts.groupby(group_keys)["n"].transform("max")
top_labels = counts[counts["n"] == max_n]

day_label = (
    top_labels.sort_values("exercise_label")
    .groupby(group_keys)["exercise_label"]
    .apply(lambda s: ", ".join(s))
    .reset_index(name="day_label")
)

out = df.merge(day_label, on=group_keys, how="left")
out.to_csv("/sessions/clever-nifty-noether/mnt/outputs/programs_detailed_boostcamp_kaggle_LABELLED_with_day_label.csv", index=False)

summary = day_label.copy()
summary.to_csv("/sessions/clever-nifty-noether/mnt/outputs/day_labels_summary.csv", index=False)

print("rows:", len(out))
print("day-groups:", len(day_label))
print("groups with ties:", (day_label["day_label"].str.contains(",")).sum())
print(day_label.head(10).to_string())
