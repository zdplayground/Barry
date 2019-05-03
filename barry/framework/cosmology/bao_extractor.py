import numpy as np


def extract_bao(ks, pk, r_s, delta=0.5):
    """ Runs the BAO Extractor method and returns the extracted BAO signal.

    Warning that this is the estimator given in Eq5 Nishimichi et al 2018 (1708.00375)

    As such, make sure your k values are finely sampled and linearly spaced. Alas for
    our data, this isn't always possible to do because the window function wrecks us.

    Parameters
    ----------
    ks : np.array
        The k values for the BAO power spectrum
    pk : np.array
        The power spectrum at `ks`
    r_s : float
        The sound horizon distance. In units of Mpc/h
    delta : float, optional
        The window (in units of `r_s` to smooth)

    Returns
    -------

    """
    k_s = 2 * np.pi / r_s  # BAO Wavenumber
    k_range = delta * k_s  # Range of k to sum over

    result = []
    for k, p in zip(ks, pk):
        k_diff = np.abs(ks - k)
        mask = k_diff < k_range
        numerator = (1 - (pk[mask] / p)).sum()
        denominator = (1 - np.cos(r_s * (ks[mask] - k))).sum()
        result.append(numerator / denominator)

    return k_range, np.array(result)


if __name__ == "__main__":
    from barry.framework.cosmology.camb_generator import CambGenerator

    camb = CambGenerator(om_resolution=10, h0_resolution=1)
    ks = camb.ks
    print(ks.shape)
    r_s, pk_lin = camb.get_data(0.3, 0.70)

    from scipy.interpolate import splev, splrep
    rep = splrep(ks, pk_lin)
    # ks2 = np.linspace(ks.min(), 1, 1000)
    ks2 = np.linspace(0, 0.398, 100) # Matching the winfit_2 data binning
    pk_lin2 = splev(ks2, rep)

    print("Got pklin")
    k_range, pk_extract = extract_bao(ks2, pk_lin2, r_s)
    print("Got pk_extract")

    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(nrows=2, figsize=(5, 9), sharex=True)
    m1 = (ks2 > (ks2.min() + k_range)) & (ks2 < (ks2.max() - k_range))
    axes[0].plot(ks2[m1], pk_lin2[m1])
    axes[0].set_title("pk_lin")
    axes[1].plot(ks2[m1], pk_extract[m1])
    axes[1].set_title("Extracted BAO, using winfit_2 bins (0, 0.398, 100)")
    plt.show()

    # Whats with the odd limits