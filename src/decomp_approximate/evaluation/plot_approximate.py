import sys
import matplotlib.pyplot as plt
import numpy as np

from pathlib import Path
from dataclasses import dataclass
from statistics import median, mean

# ALGORITHMS = [
#     "ard-o0.out", 
#     "ard-o1.out", 
#     "ard-o2.out", 
#     "ard-o3.out", 
#     "ard-o4.out", 
#     "ard-o5.out"
# ]

# NUMBER_OF_RUNS = 100000

@dataclass
class Result:
    # metadata
    name: str
    path: Path

    # input parameters
    number_of_tokens: int
    depth: int
    while_depth: int

    # performance metrics
    number_of_bags: int
    pathwidth: int

    total_runs: int
    total_clocks: int # time in microseconds
    clocks_per_second: int # assuming this == 1000000

    all_times: list[int] # times in microseconds

def parseResults(file: Path):
    data = file.read_text().split('\n\n')[1:]

    # Read input parameters
    for row in data[0].split('\n'):
        if row.startswith("# of Nodes:"):
            number_of_tokens = int(row.split(": ")[1])

        elif row.startswith("Depth:"):
            depth = int(row.split(": ")[1])

        elif row.startswith("While Depth:"):
            while_depth = int(row.split(": ")[1])

    # Read performance metrics
    for row in data[1].split('\n'):
        if row.startswith("# of Bags:"):
            number_of_bags = int(row.split(": ")[1])

        elif row.startswith("Width:"):
            pathwidth = int(row.split(": ")[1])

        elif row.startswith("While Depth:"):
            while_depth = int(row.split(": ")[1])

    for row in data[2].split('\n'):
        if row.startswith("Clocks taken:"):
            total_clocks = int(row.split(": ")[1])

        elif row.startswith("Total runs:"):
            total_runs = int(row.split(": ")[1])

        elif row.startswith("CPS:"):
            clocks_per_second = int(row.split(": ")[1])

        elif row.startswith("Times:"):
            # all_times = [int(time) for time in row.split(": ")[1].split()]
            all_times = []



    return Result(
        name=file.name,
        path=file,
        number_of_tokens=number_of_tokens,
        depth=depth,
        while_depth=while_depth,
        number_of_bags=number_of_bags,
        pathwidth=pathwidth,
        total_clocks=total_clocks,
        total_runs=total_runs,
        clocks_per_second=clocks_per_second,
        all_times=all_times
    )

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {__file__.split('/')[-1]} <test_results_directory> <output_directory>\n"
              f"e.g. {__file__.split('/')[-1]} results_approximate/ results_approximate_plots/")
        return
    
    if not Path(sys.argv[1]).is_dir():
        print(f"{sys.argv[1]} is not a valid directory!")
        return
    
    if not Path(sys.argv[2]).is_dir():
        print(f"Making directory {sys.argv[2]}...")
        Path(sys.argv[2]).mkdir()

    dirs = [obj for obj in Path(sys.argv[1]).glob("*") if obj.is_dir()]

    results = {dir.name: [parseResults(res_file) for res_file in dir.glob("*.txt")] for dir in dirs}
    colours = ["#01BEFE", "#FFDD00","#FF7D00","#FF006D","#ADFF02", "#8F00FF"]

    # Plot width vs Number of Tokens, by algorithm
    fig, axs = plt.subplots(2, 3)
    fig.tight_layout(h_pad=2, w_pad=1)
    for i, alg in enumerate(results.keys()):
        #print(alg, i % 2, i % 3)
        widths = []
        num_tokens = []
        for result in results[alg]:
            widths.append(result.pathwidth)
            num_tokens.append(result.number_of_tokens)

        axs.flat[i].scatter(num_tokens, widths, c=colours[i], label=alg)
        axs.flat[i].set_title(f"Optimisation {i}")
        axs.flat[i].set(ylabel="Path-width", xlabel="Number of tokens", ylim=(0,26))
        axs.flat[i].legend()

    # plt.show()

    # Plot width vs Depth, by algorithm
    fig, axs = plt.subplots(2, 3)
    fig.tight_layout(h_pad=2, w_pad=1)
    for i, alg in enumerate(results.keys()):
        #print(alg, i % 2, i % 3)
        widths = []
        num_tokens = []
        for result in results[alg]: 
            widths.append(result.pathwidth)
            num_tokens.append(result.depth)

        axs.flat[i].scatter(num_tokens, widths, c=colours[i], label=alg)
        axs.flat[i].set_title(f"Optimisation {i}")
        axs.flat[i].set(ylabel="Path-width", xlabel="Nesting Depth", ylim=(0,26))
        axs.flat[i].legend()

    # Plot number of bags vs tokens, by algorithm
    # fig, axs = plt.subplots(2, 3)
    # fig.tight_layout(h_pad=2, w_pad=1)
    # for i, alg in enumerate(results.keys()):
    #     #print(alg, i % 2, i % 3)
    #     widths = []
    #     num_tokens = []
    #     for result in results[alg]:
    #         widths.append(result.number_of_bags)
    #         num_tokens.append(result.number_of_tokens)

    #     axs.flat[i].scatter(num_tokens, widths, c=colours[i], label=alg)
    #     axs.flat[i].set_title(f"Optimisation {i}")
    #     axs.flat[i].set(ylabel="Number of Bags", xlabel="Number of Tokens")
    #     axs.flat[i].legend()

    # Plot average and median number of bags vs optimisation
    fig, axs = plt.subplots()
    fig.tight_layout(h_pad=2, w_pad=1)
    averages = []
    medians = []
    num_tokens = []
    for i, alg in enumerate(results.keys()):
        #print(alg, i % 2, i % 3)
        medians.append(median([res.number_of_bags for res in results[alg]]))
        averages.append(mean([res.number_of_bags for res in results[alg]]))
        num_tokens.append(i)

    axs.plot(num_tokens, averages, c=colours[1], label="Average")
    axs.plot(num_tokens, medians, c=colours[0], label="Median")

    axs.set_title("Number of Bags vs Optimisation")
    axs.set(ylabel="Number of Bags")
    axs.set_xticks([0, 1, 2, 3, 4, 5], [f"Optimisation {i}" for i in range(0, 6)])
    #axs.set_xticklabels([f"Optimisation {i}" for i in range(0, 6)])
    axs.legend()

    # Plot average and median path-width vs optimisation
    fig, axs = plt.subplots()
    fig.tight_layout(h_pad=2, w_pad=1)
    averages = []
    medians = []
    num_tokens = []
    for i, alg in enumerate(results.keys()):
        #print(alg, i % 2, i % 3)
        medians.append(median([res.pathwidth for res in results[alg]]))
        averages.append(mean([res.pathwidth for res in results[alg]]))
        num_tokens.append(i)

    axs.plot(num_tokens, averages, c=colours[1], label="Average")
    axs.plot(num_tokens, medians, c=colours[0], label="Median")

    axs.set_title("Path-width vs Optimisation")
    axs.set(ylabel="Path-width")
    axs.set_xticks([0, 1, 2, 3, 4, 5], [f"Optimisation {i}" for i in range(0, 6)])
    #axs.set_xticklabels([f"Optimisation {i}" for i in range(0, 6)])
    axs.legend()

    # Plot number of bags vs tokens, by algorithm (boxplot)
    # fig, ax = plt.subplots()
    # num_bags_list = []
    # for i, alg in enumerate(results.keys()):
    #     num_bags = []
    #     for j, result in enumerate(results[alg]):
    #         num_bags.append(result.number_of_bags)
    #     num_bags_list.append(num_bags)

    # boxplot = ax.boxplot(num_bags_list, patch_artist=True)
    # ax.set_title(f"Distribution of Bags by Optimisation")
    # ax.set(ylabel="Number of Bags")
    # ax.set_xticklabels([f"Optimisation {i}" for i in range(0, 6)])
    # for patch, colour in zip(boxplot['boxes'], colours):
    #     patch.set_facecolor(colour)

    # for patch, colour in zip(boxplot['fliers'], colours):
    #     patch.set_markeredgecolor(colour)


    # Reduction of Bags compared to baseline optimisation
    # fig, ax = plt.subplots()
    # res_lists = list(results.values())
    # res_list = sorted(res_lists[0], key=lambda x: x.name)
    # diffs_list = []
    # for i, alg in enumerate(results.keys()):
    #     if i == 0:
    #         continue
    #     diffs = []
    #     for j, result in enumerate(sorted(results[alg], key=lambda x: x.name)):
    #         if result.pathwidth > res_list[j].number_of_bags:
    #             print(result.name, res_list[j].name)
    #         diffs.append(result.number_of_bags - res_list[j].number_of_bags)
    #     diffs_list.append(diffs)

    # boxplot = ax.boxplot(diffs_list, patch_artist=True, label=f"Optimisation {i}")
    # ax.set_title(f"Change in Number of Bags compared to no optimisation")
    # ax.set(ylabel="Change in Number of Bags")
    # ax.set_xticklabels([f"Optimisation {i}" for i in range(1, 6)])
    # for patch, colour in zip(boxplot['boxes'], colours[1:]):
    #     patch.set_facecolor(colour)

    # for patch, colour in zip(boxplot['fliers'], colours[1:]):
    #     patch.set_markeredgecolor(colour)
    #ax.legend()
    

    # plt.show()

    # Plot time vs number of tokens, by algorithm
    fig, ax = plt.subplots()
    fig.tight_layout(h_pad=2, w_pad=1)
    for i, alg in enumerate(results.keys()):
        #print(alg, i % 2, i % 3)
        widths = []
        num_tokens = []
        for result in results[alg]:
            widths.append(result.total_clocks / result.clocks_per_second)
            num_tokens.append(result.number_of_tokens)

        ax.scatter(num_tokens, widths, c=colours[i], label=f"Optimisation {i}")
        ax.plot(np.unique(num_tokens), np.poly1d(np.polyfit(num_tokens, widths, 1))(np.unique(num_tokens)), c=colours[i])
    ax.set_title(f"Running time by Optimisation")
    ax.set(ylabel="Running time (microseconds)", xlabel="Number of tokens")
    ax.legend()
    #plt.show()

    # Reduction of pathwidth compared to previous optimisation
    fig, ax = plt.subplots()
    res_lists = list(results.values())
    diffs_list = []
    for i, alg in enumerate(results.keys()):
        if i == 0:
            continue
        diffs = []
        res_list = sorted(res_lists[i - 1], key=lambda x: x.name)
        for j, result in enumerate(sorted(results[alg], key=lambda x: x.name)):
            if result.pathwidth > res_list[j].pathwidth:
                print(result.name, res_list[j].name)
            diffs.append(result.pathwidth - res_list[j].pathwidth)
        #print(diffs)
        diffs_list.append(diffs)
    boxplot = ax.boxplot(diffs_list, patch_artist=True, label=f"Optimisation {i}")
    ax.set_title(f"Reduction in Path-width compared to Previous Optimisation")
    ax.set(ylabel="Path-width reduction")
    ax.set_xticklabels([f"Optimisation {i}" for i in range(1, 6)])
    for patch, colour in zip(boxplot['boxes'], colours[1:]):
        patch.set_facecolor(colour)

    for patch, colour in zip(boxplot['fliers'], colours[1:]):
        patch.set_markeredgecolor(colour)
    #ax.legend()

    # Reduction of pathwidth compared to baseline optimisation
    fig, ax = plt.subplots()
    res_list = sorted(res_lists[0], key=lambda x: x.name)
    diffs_list = []
    for i, alg in enumerate(results.keys()):
        if i == 0:
            continue
        diffs = []
        for j, result in enumerate(sorted(results[alg], key=lambda x: x.name)):
            if result.pathwidth > res_list[j].pathwidth:
                print(result.name, res_list[j].name)
            diffs.append(result.pathwidth - res_list[j].pathwidth)
        diffs_list.append(diffs)

    boxplot = ax.boxplot(diffs_list, patch_artist=True, label=f"Optimisation {i}")
    ax.set_title(f"Reduction in Path-width compared to no optimisation")
    ax.set(ylabel="Path-width reduction")
    ax.set_xticklabels([f"Optimisation {i}" for i in range(1, 6)])
    for patch, colour in zip(boxplot['boxes'], colours[1:]):
        patch.set_facecolor(colour)

    for patch, colour in zip(boxplot['fliers'], colours[1:]):
        patch.set_markeredgecolor(colour)
    #ax.legend()
    plt.show()

if __name__ == "__main__":
    main()