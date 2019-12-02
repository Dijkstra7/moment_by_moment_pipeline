import random
import pandas as pd
from matplotlib import pyplot as plt
from tqdm import tqdm


class DifficultyPlots:
    def __init__(self, f_path=None):
        if f_path is None:
            f_path = "C:/Users/Rick Dijkstra/Downloads/studydata (2).csv"
        self.file = pd.read_csv(f_path, index_col=0)
        self.file.difficulty_level = (self.file.difficulty_level - .65)*3000
        self.file["submit_time"] = [date[11:] for date in
                                    self.file.submit_date.values]

    def get_plot_student_loid_diff(self, student, loid):
        plot_data = self.file.loc[(self.file.user_id == student) &
                                  (self.file.learning_objective_id == loid)]
        plot_range = list(range(len(plot_data)))
        # plot_range = plot_data.submit_time
        plt.plot(plot_range, plot_data.ability_after_answer,
                 label="Ability")
        plt.plot(plot_range, plot_data.difficulty_level,
                 label="Difficulty")
        day_changes = self.get_day_change_tuples(plot_data.submit_date.values)
        for change in day_changes:
            plt.plot([change[0], change[0]], [-10, 610],
                     label=f"{change[1]} Nov")
        plt.title(f"student: {student} - leerdoel: {loid}")
        plt.legend()
        plt.gcf().autofmt_xdate()

    def get_day_change_tuples(self, plot_data):
        day_changes = [(0, plot_data[0][8:10])]
        for pd_id, pd in enumerate(plot_data):
            pd_day = pd[8:10]
            if pd_day != day_changes[-1][1]:
                day_changes.append((pd_id, pd_day))
        return day_changes

    def plot_student_loid_diff(self, student, loid):
        self.get_plot_student_loid_diff(student, loid)
        plt.show()

    def save_student_loid_diff(self, student, loid):
        plt.gcf().clear()
        self.get_plot_student_loid_diff(student, loid)
        plt.gcf().savefig(f"./plots/diff_plots/{student}_{loid}.png")

    def get_random_student(self):
        return random.choice(self.file.user_id.unique())

    def get_random_loid(self):
        return random.choice(self.file.learning_objective_id.unique()[2:])

    def plot_random(self, seed=None):
        if seed is not None:
            random.seed(seed)
        student = self.get_random_student()
        loid = self.get_random_loid()
        self.plot_student_loid_diff(student, loid)

    def save_all_plots(self):
        for loid in self.file.learning_objective_id.unique():
            for student in tqdm(self.file.user_id.unique()):
                self.save_student_loid_diff(student, loid)


if __name__ == "__main__":
    plt.gca().set_ylim(-10, 610)
    diff_plots = DifficultyPlots()
    # diff_plots.save_all_plots()
    diff_plots.plot_student_loid_diff(9749122, 8234)
