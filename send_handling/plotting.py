import matplotlib.pyplot as plt
import matplotlib.dates as dates
import pandas as pd
import numpy as np


def vert_subplots_2df(df1, df2, ks, c1, c2, fname, trim=False, ylab=['', '', '', '', ''], no_show=False, no_minor=True):
    n_plots = len(ks)
    fig, axes = plt.subplots(n_plots, 1, figsize=(6, n_plots * 1.5), sharex=True)
    for i in range(len(ks)):
        key = ks[i]
        ax = axes[i]
        x_arr = df1['DATE_TIME'].values
        y_arr_scat = df1[key].values
        y_arr_line = df2[key].values
        ax.scatter(x_arr, y_arr_scat, color=c1, marker='.')
        ax.plot(x_arr, y_arr_line, color=c2, linewidth=1)
        set_x_date_lims(trim, ax, x_arr)
        sort_date_ticks(ax, plt, no_minor)
        ax.set_ylabel(ylab[i])
    axes[-1].set_xlabel('Date')
    plt.tight_layout()
    if no_show:
        return fig, axes
    else:
        plt.savefig(fname, format='png', dpi=600)
        plt.show()

    return


def sort_date_ticks(axis, plot, no_minor=False):
    if no_minor:
        axis.xaxis.set_major_locator(dates.YearLocator())
        axis.xaxis.set_major_formatter(dates.DateFormatter('%b\n%Y'))
        axis.xaxis.set_minor_locator(dates.MonthLocator())
        axis.xaxis.set_minor_formatter(dates.DateFormatter('%b'))
    else:
        axis.xaxis.set_major_locator(dates.MonthLocator(bymonthday=12))
        axis.xaxis.set_minor_locator(dates.DayLocator())
        axis.xaxis.set_major_formatter(dates.DateFormatter('%d\n%b\n%Y'))
        axis.xaxis.set_minor_formatter(dates.DateFormatter('%d'))
    plot.xticks(rotation=0)
    return


def set_x_date_lims(trimmed, axis, x_array):
    if trimmed:
        axis.set_xlim([pd.to_datetime("2021-03-11 16:35:00"), x_array[-1]])
    else:
        axis.set_xlim([x_array[0], x_array[-1]])

    return


def vert_subplots_1df_compare(df, k1, k2, c1, c2, fname, trim=False, ylab=['', '', '', '', '']):

    n_plots = len(k1)
    fig, axes = plt.subplots(n_plots, 1, figsize=(6, n_plots * 1.5), sharex=True)
    i: int
    for i in range(len(k1)):
        x_arr = df.index
        y_arr1 = df[k1[i]].values
        y_arr2 = df[k2[i]].values
        ax = axes[i]
        ax.plot(x_arr, y_arr1, color=c1)
        ax.plot(x_arr, y_arr2, color=c2)

        set_x_date_lims(trim, ax, x_arr)

        sort_date_ticks(ax, plt, no_minor=True)
        ax.set_ylabel(ylab[i])
        ax.set_xlabel('Date')

    plt.tight_layout()
    plt.savefig(fname, format='png', dpi=600)
    plt.show()
    return


def vert_subplots_1df(df, keys, colours, fname, trim=False, ylab=['','','','',''], no_minor=False):
    # TODO generalise subplot routine
    n_plots = len(keys)
    fig, axes = plt.subplots(n_plots, 1, figsize=(6, n_plots * 1.5), sharex=True)
    i: int
    for i in range(len(keys)):
        x_arr = df.index
        y_arr1 = df[keys[i]].values
        ax = axes[i]
        ax.scatter(x_arr, y_arr1, color=colours, marker='.')
        set_x_date_lims(trim, ax, x_arr)

        sort_date_ticks(ax, plt, no_minor)
        ax.set_ylabel(ylab[i])

    axes[-1].set_xlabel('Date')

    plt.tight_layout()
    plt.savefig(fname, format='png', dpi=600)
    plt.show()
    return


def one_plot_2_dfs(df1, df2, keys1, keys2, log_y, labels, limits, fname):
    axis = df1.plot(y=keys1, logy=log_y, zorder=10, figsize=(6, 4))
    df2.plot(y=keys2, logy=log_y, ax=axis)

    axis.set_xlim(limits[0])
    axis.set_ylabel(labels[0])
    axis.set_xlabel(labels[1])
    axis.set_ylim(limits[1])
    axis.legend([])
    plt.tight_layout()
    plt.savefig(fname, format='png', dpi=600)
    plt.show()
    return


def hist(df, keys, labels, filename):
    colours = ['#66CDAA', '#C09BD8', '#F2D591', '#70DEFF', '#FF5C5C']
    fig, axes = plt.subplots(1, len(keys), sharey=True, figsize=(3 * len(keys), 4))
    bins = dict()
    for key in keys:
        bins[key] = get_bins(df, key)

    for i in range(len(keys)):
        axes[i].hist(df[keys[i]].values, bins=bins[keys[i]], color=colours[i], density=True)
        axes[i].set_xlabel(labels[i])

    axes[0].set_ylabel('Probability')
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()


def get_bins(df, key):
    left_of_first_bin = df[key].min() - 0.5
    right_of_last_bin = df[key].max() + 0.5
    return np.arange(left_of_first_bin, right_of_last_bin + 1, 1)
