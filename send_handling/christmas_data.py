from send_handling import live_data as send
import numpy as np
import matplotlib.pyplot as plt


def straight_line(x, m, c):
    return m * x + c


if __name__ == "__main__":
    filepath = "C:/Users/Fraser Baird/OneDrive - University of Surrey/Documents/data/SENDAuto/CR1000_Counts.dat"
    send_df = send.import_data(filepath, '1T')
    send_df = send.compute_counting_rate(send_df)
    data_col_keys = ['CT_RATE', 'TEMP', 'RH']

    for key in data_col_keys:
        average = send.nan_average(send_df[key].values)
        std_dev = np.nanstd(send_df[key].values)
        ax = send_df.rolling('180T').mean().plot(kind='line', y=key, zorder=200, color='red', linewidth=1)
        send_df.reset_index().plot(kind='scatter', x="DATE_TIME", y=key, ax=ax, color='black', zorder=100, marker='.')
        # ax.axhline(average, color='purple')
        # ax.axhspan(average-std_dev, average+std_dev, color='green', alpha=0.5)
        ax.set_xlim([send_df.index[0], send_df.index[-1]])
        ax.get_legend().remove()
        plt.tight_layout()

        plt.savefig('figures/%s.png' % key, dpi=600)
        plt.show()

    # perm_list = itt.permutations(data_col_keys, 2)
    #
    # for perm in perm_list:
    #     x_vals = send_df[perm[0]].values
    #     y_vals = send_df[perm[1]].values
    #     result = linregress(x_vals, y_vals)
    #     fit = straight_line(x_vals, result.slope, result.intercept)
    #     ax = send_df.plot(kind="scatter", x=perm[0], y=perm[1], color='black', marker='.')
    #     ax.plot(x_vals, fit, color='red')
    #     text_x = max(x_vals) * 0.95
    #     text_y = max(y_vals) * 0.95
    #     plt.text(text_x, text_y, "r = %s" % round(result.rvalue, 3))
    #     # plt.savefig('figures/%s-%s.png' % (perm[0], perm[1]), dpi=600)
    #     plt.show()


