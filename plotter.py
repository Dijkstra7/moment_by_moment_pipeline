from matplotlib import pyplot as plt
import os

class Plotter:

    def __init__(self, dir_name="plots"):
        self.dir_ = dir_name
        self.color_dict = {"pre": 'royalblue',
                           "gui": 'darkorange',
                           "nap": 'silver',
                           "ap": 'gold',
                           "rap": 'mediumblue',
                           "post": 'olivedrab',
                           "day0": 'lightgray',
                           "day1": 'xkcd:bright yellow',
                           "day2": 'xkcd:sunshine yellow',
                           "day3": 'xkcd:canary yellow',
                           "day4": 'mediumblue',
                           "day5": "lightgray",
                           "": "lightgray",
                           "out of school": "red"}
        if not os.path.exists(self.dir_):
            os.mkdir(self.dir_)

    def plot_save(self, y_data, x_data=None, f_name="_", phase_data=None,
                  use_legend=True):
        plt.gca().set_ylim(-1.15, 1.1)
        phases = []
        if isinstance(y_data[0], list) is False:
            y_data = [y_data]
        if x_data is None:
            x_data = range(1, max([len(y) for y in y_data]) + 4)
        for j, y in enumerate(y_data):
            plt.plot(x_data[:len(y)], y, color=["cyan", "red", "black",
                                                "orangered"][j])
        if phase_data is not None:
            for j in range(len(phase_data)):
                phase = phase_data[j]
                if not phase in phases:
                    plt.broken_barh([(j, 1)], (-0.5, 1),
                                    facecolors=self.color_dict[phase],
                                    label=phase)
                    phases.append(phase)
                else:
                    plt.broken_barh([(j, 1)], (-0.5, 1),
                                    facecolors=self.color_dict[phase])
            if use_legend is True:
                plt.legend()
        plt.gcf().savefig(f"{self.dir_}/{f_name}.png", dpi=300)
        plt.gcf().clear()

    def plot_show(self, y_data, x_data=None):
        if x_data is None:
            plt.plot(y_data)
        else:
            plt.plot(x_data[:len(y_data)], y_data)
        plt.pause(.01)
        plt.gcf().clear()


# for b1, b2, c in zip(boundary_list[:-1], boundary_list[1:],
#                      color_list):
#     a.broken_barh([(b1, b2 - b1)],
#                   (low + .25 * (height - low),
#                    .5 * (height - low)),
#                   facecolors=c)