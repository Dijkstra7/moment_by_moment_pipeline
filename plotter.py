from matplotlib import pyplot as plt
import os

class Plotter:

    def __init__(self, dir_name="plots"):
        self.dir_ = dir_name
        if not os.path.exists(self.dir_):
            os.mkdir(self.dir_)

    def plot_save(self, y_data, x_data=None, f_name="_"):
        if isinstance(y_data[0], list) is False:
            y_data = [y_data]
        if x_data is None:
            x_data = range(max([len(y) for y in y_data]))
        for y in y_data:
            plt.plot(x_data[:len(y)], y)
        plt.gcf().savefig(f"{self.dir_}/{f_name}.png")
        plt.gcf().clear()

    def plot_show(self, y_data, x_data=None):
        if x_data is None:
            plt.plot(y_data)
        else:
            plt.plot(x_data, y_data)
        plt.pause(.01)
        plt.gcf().clear()

