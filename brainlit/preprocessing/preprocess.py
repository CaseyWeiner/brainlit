import numpy as np


def center(data):
    """Centers data by subtracting the mean

    Parameters
    -------
    data : array-like
        data to be centered

    Returns
    -------
    data_centered : array-like
        centered-data

    """
    data_centered = data - np.mean(data)
    return data_centered


def contrast_normalize(data, centered=False):
    """Normalizes image data to have variance of 1

    Parameters
    -------
    data : array-like
        data to be normalized

    centered : boolean
        When False (the default), centers the data first

    Returns
    -------
    data : array-like
        normalized data

    """
    if not centered:
        data = center(data)
    data = np.divide(data, np.sqrt(np.var(data)))
    return data


def whiten(data, window_size, step_size, centered=False):
    """Performs PCA whitening on an array. This preprocessing step is described
    in _[1].

    Parameters
    -------
    img : array-like
        image to be vectorized

    window_size : array-like
        window size dictating the neighborhood to be vectorized, same number of
        dimensions as img, based on the top-left corner

    step_size : array-like
        step size in each of direction of window, same number of
        dimensions as img

    Returns
    -------
    data-whitened : array-like
        whitened data

    S : 2D array
        Singular value array of covariance of vectorized image

    References
    ----------

    .. [1] FILL IN REFERENCE

    """
    if not centered:
        data = center(data)

    data_padded, pad_size = window_pad(data, window_size, step_size)
    data_vectorized = vectorize_img(data_padded, window_size, step_size)

    c = np.cov(data_vectorized)
    U, S, V = np.linalg.svd(c)
    eps = 1e-5

    whiten_matrix = np.dot(np.diag(1.0 / np.sqrt(S + eps)), U.T)
    whitened = np.dot(whiten_matrix, data_vectorized)

    data_whitened = imagize_vector(whitened, data_padded.shape, window_size, step_size)
    data_whitened = undo_pad(data_whitened, pad_size)

    return data_whitened, S


def undo_pad(data, pad_size):
    """Pad image at edges so the window can convolve evenly.
    Padding will be a copy of the edges.

    Parameters
    -------
    img : array-like
        image to be padded

    window_size : array-like
        window size that will be convolved, same number of dimensions as img

    step_size : array-like
        step size in each of direction of window convolution, same number of
        dimensions as img

    Returns
    -------
    img_padded : array-like
        padded image

    pad_size : array-like
        amount of padding in every direction of the image

    """
    start = pad_size[:, 0].astype(int)
    end = (data.shape - pad_size[:, 1]).astype(int)
    coords = list(zip(start, end))
    slices = tuple(slice(coord[0], coord[1]) for coord in coords)
    data = data[slices]

    return data


def window_pad(img, window_size, step_size):
    """Pad image at edges so the window can convolve evenly.
    Padding will be a copy of the edges.

    Parameters
    -------
    img : array-like
        image to be padded

    window_size : array-like
        window size that will be convolved, same number of dimensions as img

    step_size : array-like
        step size in each of direction of window convolution, same number of
        dimensions as img

    Returns
    -------
    img_padded : array-like
        padded image

    pad_size : array-like
        amount of padding in every direction of the image

    """
    shp = img.shape
    d = len(shp)

    pad_size = np.zeros([d, 2])
    pad_size[:, 0] = window_size - 1

    num_steps = np.floor(np.divide(shp + window_size - 2, step_size))
    final_loc = np.multiply(num_steps, step_size)

    pad_size[:, 1] = final_loc - shp + 1
    pad_width = [pad_size[dim, :].astype(int).tolist() for dim in range(d)]

    img_padded = np.pad(img, pad_width, mode="edge")
    # Why does the padding add so much to the edge?
    return img_padded, pad_size


def vectorize_img(img, window_size, step_size):
    """Reshapes an image by vectorizing different neighborhoods of the image.

    Parameters
    -------
    img : array-like
        image to be vectorized

    window_size : array-like
        window size dictating the neighborhood to be vectorized, same number of
        dimensions as img, based on the top-left corner

    step_size : array-like
        step size in each of direction of window, same number of
        dimensions as img

    Returns
    -------
    vectorized : array-like
        vectorized image

    """

    shp = img.shape

    num_steps = (np.floor(np.divide(shp - window_size, step_size)) + 1).astype(int)
    vectorized = np.zeros([np.product(window_size), np.product(num_steps)])

    for step_num, step_coord in enumerate(np.ndindex(*num_steps)):
        start = np.multiply(step_coord, step_size)
        end = start + window_size

        coords = list(zip(start, end))
        slices = tuple(slice(coord[0], coord[1]) for coord in coords)
        vectorized[:, step_num] = img[slices].flatten()

    return vectorized


def imagize_vector(data, orig_shape, window_size, step_size):
    """Reshapes a vectorized image back to its original shape.

    Parameters
    -------
    data : array-like
        vectorized image

    orig_shape : tuple
        dimensions of original image

    window_size : array-like
        window size dictating the neighborhood to be vectorized, same number of
        dimensions as img, based on the top-left corner

    step_size : array-like
        step size in each of direction of window, same number of
        dimensions as img

    Returns
    -------
    imagized : array-like
        original image 

    """
    imagized = np.zeros(orig_shape)
    d = len(orig_shape)

    shp = orig_shape

    num_steps = (np.floor(np.divide(shp - window_size, step_size)) + 1).astype(int)
    vectorized = np.zeros([np.product(window_size), np.product(num_steps)])

    for step_num, step_coord in enumerate(np.ndindex(*num_steps)):
        start = np.multiply(step_coord, step_size)
        end = start + window_size

        coords = list(zip(start, end))
        slices = tuple(slice(coord[0], coord[1]) for coord in coords)

        imagized_temp = np.zeros(orig_shape)
        imagized_temp = data[:, step_num].reshape(window_size)
        stacked = np.stack((imagized[slices], imagized_temp), axis=-1)
        imagized[slices] = np.true_divide(stacked.sum(d), (stacked != 0).sum(d))

    return imagized
