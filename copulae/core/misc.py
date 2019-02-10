import numpy as np
from scipy import stats
import warnings

__all__ = ['EPS', 'valid_rows_in_u', 'pseudo_obs', 'rank_data', 'tri_indices']

EPS = 6.06e-6


def pseudo_obs(data: np.ndarray, ties='average'):
    """
    Compute the pseudo-observations for the given data matrix

    :param data: numpy array
        n x d-matrix (or d-vector) of random variates to be converted to pseudo-observations

    :param ties: str
        string specifying how ranks should be computed if there are ties in any of the coordinate samples
        The options are 'average', 'min', 'max', 'dense' and 'ordinal'. Passed to scipy.stats.rankdata

    :return: numpy array
        matrix or vector of the same dimension as X containing the pseudo observations
    """
    return rank_data(data, ties) / (len(data) + 1)


def rank_data(obs: np.ndarray, ties='average'):
    """
    Assign ranks to data, dealing with ties appropriately. This function works on core as well as vectors

    :param obs: numpy array
        n x d-matrix (or d-vector) of random variates to be converted to pseudo-observations

    :param ties: str, default 'average'
        The method used to assign ranks to tied elements. The options are 'average', 'min', 'max', 'dense' and
        'ordinal'.
        'average': The average of the ranks that would have been assigned to all the tied values is assigned to each
            value.
        'min': The minimum of the ranks that would have been assigned to all the tied values is assigned to each
            value. (This is also referred to as "competition" ranking.)
        'max': The maximum of the ranks that would have been assigned to all the tied values is assigned to each value.
        'dense': Like 'min', but the rank of the next highest element is assigned the rank immediately after those
            assigned to the tied elements. 'ordinal': All values are given a distinct rank, corresponding to
            the order that the values occur in `a`.

    :return: numpy array
        matrix or vector of the same dimension as X containing the pseudo observations
    """
    obs = np.asarray(obs)

    if obs.ndim == 1:
        return stats.rankdata(obs, ties)
    elif obs.ndim == 2:
        return np.array([stats.rankdata(obs[:, i], ties) for i in range(obs.shape[1])]).T
    else:
        raise ValueError('Can only rank data which is 1 or 2 dimensions')


def tri_indices(n: int, m=0, side='both'):
    """
    Return the indices for the triangle of an (n, n) array

    :param n: int
        dimension of square matrix
    :param m: int
        offset
    :param side: str, default 'both'
        Side of triangle to return. Supported values are 'lower', 'upper', 'both'
    :return: Tuple[numpy array, numpy array]
        Tuple of row indices and column indices

    Examples
    --------
    >>> from copulae.core import tri_indices
    >>> x = np.arange(9).reshape(3, 3)

    To get lower indices of matrix
    >>> x[tri_indices(3, 1, 'lower')]

    # To form covariance matrix
    >>> c = np.eye(3)
    >>> c[tri_indices(3, 1)] = np.tile([0.1, 0.2, 0.3], 2)
    """

    side = side.lower()

    if side not in {'lower', 'upper', 'both'}:
        raise ValueError("side option must be one of 'lower', 'upper' or 'both'")

    l_i = [[], []]  # lower indices
    if side in {'lower', 'both'}:
        for i in range(n - m):
            for j in range(i + m, n):
                l_i[1].append(i)
                l_i[0].append(j)

        if side == 'lower':
            return tuple(np.array(x) for x in l_i)

    u_i = [[], []]  # upper indices
    if side in {'upper', 'both'}:
        for i in range(n - m):
            for j in range(i + m, n):
                u_i[0].append(i)
                u_i[1].append(j)
        if side == 'upper':
            return tuple(np.array(x) for x in u_i)

    return tuple(np.array([*u_i[i], *l_i[i]]) for i in range(2))


def valid_rows_in_u(U: np.ndarray) -> np.ndarray:
    """
    Checks that the matrix U supplied has elements between 0 and 1 inclusive.

    :param U: ndarray, matrix
        matrix where rows is the number of data points and columns is the dimension
    :return: ndarray
        a boolean vector that indicates which rows are okay
    """

    warnings.filterwarnings("ignore", category=RuntimeWarning)
    return (~np.isnan(U) & (0 <= U) & (U <= 1)).all(1)
