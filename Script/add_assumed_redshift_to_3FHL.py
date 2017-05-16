import matplotlib.pyplot as plt
import numpy as np
from astropy.table import Table

filename = "gll_psch_v11.fit.gz"
output_filename = "gll_psch_v11_with_assumed_redshifts.fits"
number_of_random_redshifts = 100


def get_random_distrib_from_histogram(hist, bins, num):
    bin_midpoints = bins[:-1] + np.diff(bins) / 2
    cdf = np.cumsum(hist)
    cdf = cdf / cdf[-1]
    values = np.random.rand(num)
    value_bins = np.searchsorted(cdf, values)
    return bin_midpoints[value_bins]


def get_blazar_redshifts(blazar_type):
    table = Table.read(filename, hdu='LAT_Point_Source_Catalog')
    known_redshift_mask = np.isfinite(table['Redshift'])
    known_redshift_table = table[known_redshift_mask]
    if blazar_type == "bll":
        class_1 = known_redshift_table['CLASS'] == "bll    "
        class_2 = known_redshift_table['CLASS'] == "BLL    "
    if blazar_type == "fsrq":
        class_1 = known_redshift_table['CLASS'] == "fsrq   "
        class_2 = known_redshift_table['CLASS'] == "FSRQ   "
    if blazar_type == "bcu":
        class_1 = known_redshift_table['CLASS'] == "bcu    "
        class_2 = known_redshift_table['CLASS'] == "BCU    "
    class_type_mask = np.logical_or.reduce((class_1, class_2))
    sub_table = known_redshift_table[class_type_mask]
    return sub_table["Redshift"]


def get_blazar_random_distribution(blazar_type, num):
    data = get_blazar_redshifts(blazar_type)
    hist, bins = np.histogram(data, bins=50)
    return get_random_distrib_from_histogram(hist, bins, num)


def get_blazar_median_redshift(blazar_type):
    data = get_blazar_redshifts(blazar_type)
    return np.median(data)


def test_random_distribution(blazar_type):
    data = get_blazar_redshifts(blazar_type)
    hist, bins = np.histogram(data, bins=50)
    random_from_cdf = get_random_distrib_from_histogram(hist, bins, 2000)
    plt.subplot(121)
    plt.hist(data, 50)
    plt.subplot(122)
    plt.hist(random_from_cdf, 50)
    plt.show()


if __name__ == '__main__':
    point_source_table = Table.read(filename, hdu='LAT_Point_Source_Catalog')
    length = len(point_source_table)
    # Add first a column with the median redshift
    bll_median_redshift = get_blazar_median_redshift("bll")
    fsrq_median_redshifts = get_blazar_median_redshift("fsrq")
    bcu_median_redshifts = get_blazar_median_redshift("bcu")
    redshifts = point_source_table['Redshift'].copy()
    for row, redshift in enumerate(redshifts):
        if not np.isfinite(redshift):
            if point_source_table['CLASS'][row] == "bll    " or point_source_table['CLASS'][row] == "BLL    ":
                redshifts[row] = bll_median_redshift
            if point_source_table['CLASS'][row] == "fsrq   " or point_source_table['CLASS'][row] == "FSRQ   ":
                redshifts[row] = fsrq_median_redshifts
            if point_source_table['CLASS'][row] == "bcu    " or point_source_table['CLASS'][row] == "BCU    ":
                redshifts[row] = bcu_median_redshifts
    point_source_table["Assumed_redshift_median"] = redshifts

    # And now "number_of_random_redshifts" columns with random redshifts
    for i in range(number_of_random_redshifts):
        bll_random_redshifts = get_blazar_random_distribution("bll", length)
        fsrq_random_redshifts = get_blazar_random_distribution("fsrq", length)
        bcu_random_redshifts = get_blazar_random_distribution("bcu", length)
        redshifts = point_source_table['Redshift'].copy()
        for row, redshift in enumerate(redshifts):
            if not np.isfinite(redshift):
                if point_source_table['CLASS'][row] == "bll    " or point_source_table['CLASS'][row] == "BLL    ":
                    redshifts[row] = bll_random_redshifts[row]
                if point_source_table['CLASS'][row] == "fsrq   " or point_source_table['CLASS'][row] == "FSRQ   ":
                    redshifts[row] = fsrq_random_redshifts[row]
                if point_source_table['CLASS'][row] == "bcu    " or point_source_table['CLASS'][row] == "BCU    ":
                    redshifts[row] = bcu_random_redshifts[row]
        point_source_table["Assumed_redshift_%s" % (i+1)] = redshifts
    print("Creating the file: %s" % output_filename)
    point_source_table.write(output_filename, overwrite=True)
    exit()
