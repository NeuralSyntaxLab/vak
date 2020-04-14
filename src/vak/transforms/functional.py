import numpy as np
import torch

__all__ = [
    'pad_to_window',
    'reshape_to_window',
    'standardize_spect',
    'to_floattensor',
    'to_longtensor',
]


def standardize_spect(spect, mean_freqs, std_freqs, non_zero_std):
    """standardize spectrogram by subtracting off mean and dividing by standard deviation.

    Parameters
    ----------
    spect : numpy.ndarray
        with shape (frequencies, time bins)
    mean_freqs : numpy.ndarray
        vector of mean values for each frequency bin across the fit set of spectrograms
    std_freqs : numpy.ndarray
        vector of standard deviations for each frequency bin across the fit set of spectrograms
    non_zero_std : numpy.ndarray
        boolean, indicates where std_freqs has non-zero values. Used to avoid divide-by-zero errors.

    Returns
    -------
    transformed : numpy.ndarray
        with same shape as spect but with (approximately) zero mean and unit standard deviation
        (mean and standard devation will still vary by batch).
    """
    tfm = spect - mean_freqs[:, np.newaxis]  # need axis for broadcasting
    # keep any stds that are zero from causing NaNs
    tfm[non_zero_std, :] = tfm[non_zero_std, :] / std_freqs[non_zero_std, np.newaxis]
    return tfm


def pad_to_window(arr, window_size, padval=0., return_padding_mask=True):
    """pad a 1d or 2d array so that it can be reshaped
    into consecutive windows of specified size

    Parameters
    ----------
    arr : numpy.ndarray
        with 1 or 2 dimensions, e.g. a vector of labeled timebins
        or a spectrogram.
    window_size : int
        width of window in number of elements.
    padval : float
        value to pad with. Added to end of array, the
        "right side" if 2-dimensional.
    return_padding_mask : bool
        if True, return a boolean vector to use for cropping
        back down to size before padding. padding_mask has size
        equal to width of padded array, i.e. original size
        plus padding at the end, and has values of 1 where
        columns in padded are from the original array,
        and values of 0 where columns were added for padding.

    Returns
    -------
    padded : numpy.ndarray
        padded with padval
    padding_mask : np.bool
        has size equal to width of padded, i.e. original size
        plus padding at the end. Has values of 1 where
        columns in padded are from the original array,
        and values of 0 where columns were added for padding.
        Only returned if return_padding_mask is True.
    """
    if arr.ndim == 1:
        width = arr.shape[0]
    elif arr.ndim == 2:
        height, width = arr.shape
    else:
        raise ValueError(
            f'input array must be 1d or 2d but number of dimensions was: {arr.ndim}'
        )

    target_width = int(
        np.ceil(width / window_size) * window_size
    )

    if arr.ndim == 1:
        padded = np.ones((target_width,)) * padval
        padded[:width] = arr
    elif arr.ndim == 2:
        padded = np.ones((height, target_width)) * padval
        padded[:, :width] = arr

    if return_padding_mask:
        padding_mask = np.zeros((target_width,), dtype=np.bool)
        padding_mask[:width] = True
        return padded, padding_mask
    else:
        return padded


def reshape_to_window(arr, window_size):
    """reshape a 1d or 2d array into consecutive
    windows of specified size.

    Parameters
    ----------
    arr : numpy.ndarray
        with 1 or 2 dimensions, e.g. a vector of labeled timebins
        or a spectrogram.
    window_size : int
        width of window in number of elements.

    Returns
    -------
    windows : numpy.ndarray
        with shape (-1, window_size) if array is 1d,
        or with shape (-1, height, window_size) if array is 2d
    """
    if arr.ndim == 1:
        return arr.reshape((-1, window_size))
    elif arr.ndim == 2:
        height, _ = arr.shape
        return arr.reshape((-1, height, window_size))
    else:
        raise ValueError(
            f'input array must be 1d or 2d but number of dimensions was: {arr.ndim}'
        )


def to_floattensor(arr):
    """convert Numpy array to torch.FloatTensor.

    Parameters
    ----------
    arr : numpy.ndarray

    Returns
    -------
    float_tensor
        with dtype 'float32'
    """
    return torch.from_numpy(arr).float()


def to_longtensor(arr):
    """convert Numpy array to torch.LongTensor.

    Parameters
    ----------
    arr : numpy.ndarray

    Returns
    -------
    long_tensor : torch.Tensor
        with dtype 'float64'
    """
    return torch.from_numpy(arr).long()


def add_channel(input, channel_dim=0):
    """add a channel dimension to a tensor.
    Transform that makes it easy to treat a spectrogram as an image,
    by adding a dimension with a single 'channel', analogous to grayscale.
    In this way the tensor can be fed to e.g. convolutional layers.

    Parameters
    ----------
    input : torch.Tensor
    channel_dim : int
        dimension where "channel" is added. Default is 0.
    """
    return torch.unsqueeze(input, dim=channel_dim)
