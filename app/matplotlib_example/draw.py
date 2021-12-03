import matplotlib.pyplot as plt

if __name__ == "__main__":
    # create a 2x2 figure
    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(8.0, 6.0))  # fig : Figure, ax: 2x2 numpy array of Axes
    # set title to figure
    fig.canvas.manager.set_window_title("window title")
    fig.suptitle("figure title")

    # data
    data = {
        "top left": {
            "coord": (0, 0),
            "data": ([0, -1], [0, 1]),
        },
        "bottom left": {
            "coord": (0, 1),
            "data": ([0, -1], [0, -1]),
        },
        "top right": {
            "coord": (1, 0),
            "data": ([0, 1], [0, 1]),
        },
        "bottom right": {
            "coord": (1, 1),
            "data": ([0, 1], [0, -1]),
        },
    }

    # draw on axes
    for name, value in data.items():
        coord, data = value.values()
        ax[coord].set_title(name)
        ax[coord].set_xlabel(f"x {name}")
        ax[coord].set_ylabel(f"y {name}")
        ax[coord].plot(*data)

    # set title layout
    plt.tight_layout()
    # call plt.show() at the end of the program
    plt.show()
