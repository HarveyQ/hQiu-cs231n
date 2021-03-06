import numpy as np

"""
This file implements various first-order update rules that are commonly used
for training neural networks. Each update rule accepts current weights and the
gradient of the loss with respect to those weights and produces the next set of
weights. Each update rule has the same interface:

def update(w, dw, config=None):

Inputs:
  - w: A numpy array giving the current weights.
  - dw: A numpy array of the same shape as w giving the gradient of the
    loss with respect to w.
  - config: A dictionary containing hyperparameter values such as learning
    rate, momentum, etc. If the update rule requires caching values over many
    iterations, then config will also hold these cached values.

Returns:
  - next_w: The next point after the update.
  - config: The config dictionary to be passed to the next iteration of the
    update rule.

NOTE: For most update rules, the default learning rate will probably not
perform well; however the default values of the other hyperparameters should
work well for a variety of different problems.

For efficiency, update rules may perform in-place updates, mutating w and
setting next_w equal to w.
"""


def sgd(w, dw, config=None):
    """
    Performs vanilla stochastic gradient descent.

    config format:
    - learning_rate: Scalar learning rate.
    """
    if config is None: config = {}
    config.setdefault('learning_rate', 1e-2)

    w -= config['learning_rate'] * dw
    return w, config


def sgd_momentum(w, dw, config=None):
    """
    Performs stochastic gradient descent with momentum.

    config format:
    - learning_rate: Scalar learning rate.
    - momentum: Scalar between 0 and 1 giving the momentum value.
      Setting momentum = 0 reduces to sgd.
    - velocity: A numpy array of the same shape as w and dw used to store a
      moving average of the gradients.
    """
    if config is None:
        config = {}

    config.setdefault('learning_rate', 1e-2)
    config.setdefault('momentum', 0.9)
    config.setdefault('velocity', np.zeros_like(w))

    # HQ: original code for velocity, made change for better consistency
    # v = config.get('velocity', np.zeros_like(w))  # returns all zeros if key 'velocity does not exist
    #  next_w = None
    ###########################################################################
    # TODO: Implement the momentum update formula. Store the updated value in #
    # the next_w variable. You should also use and update the velocity v.     #
    ###########################################################################
    mu = config['momentum']
    lr = config['learning_rate']
    v = config['velocity']

    v = mu * v - lr * dw  # update velocity
    next_w = w + v

    config['velocity'] = v  # update v in config for next iteration
    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################
    return next_w, config


# todo (me): test Nesterov Momentum
def nesterov_momentum(w, dw, config=None):
    """
    Uses the Nesterov Momentum update rule, which uses MA of gradient at
    the position after momentum part update ("look-ahead") to update

    config format:
    - learning_rate: Scalar learning rate.
    - momentum: Scalar between 0 and 1 giving the momentum value.
      Setting momentum = 0 reduces to sgd.
    - velocity: A numpy array of the same shape as w and dw used to store a
      moving average of the gradients.
    """

    if config is None:
        config = {}

    # set default
    config.setdefault('learning_rate', 1e-2)
    config.setdefault('momentum', 0.9)
    config.setdefault('velocity', np.zeros_like(w))

    # unpack config
    mu = config['momentum']
    lr = config['learning_rate']
    v = config['velocity']

    # update parameters
    prev_v = v.copy()
    v = mu * prev_v - lr * dw
    next_w = w - mu * prev_v + (1 + mu) * v

    # # alternative expression
    # prev_v = v.copy()
    # v = mu * prev_v - lr * dw
    # next_w = w - lr * dw + mu * v

    # update config
    config['velocity'] = v

    return next_w, config


def rmsprop(w, dw, config=None):
    """
    Uses the RMSProp update rule, which uses a moving average of squared
    gradient values to set adaptive per-parameter learning rates.

    config format:
    - learning_rate: Scalar learning rate.
    - decay_rate: Scalar between 0 and 1 giving the decay rate for the squared
      gradient cache.
    - epsilon: Small scalar used for smoothing to avoid dividing by zero.
    - cache: Moving average of second moments of gradients.
    """
    if config is None: config = {}
    config.setdefault('learning_rate', 1e-2)
    config.setdefault('decay_rate', 0.99)
    config.setdefault('epsilon', 1e-8)
    config.setdefault('cache', np.zeros_like(w))

    # next_w = None
    ###########################################################################
    # TODO: Implement the RMSprop update formula, storing the next value of x #
    # in the next_w variable. Don't forget to update cache value stored in    #
    # config['cache'].                                                        #
    ###########################################################################
    # unpack config
    eps = config['epsilon']
    lr = config['learning_rate']
    beta = config['decay_rate']
    cache = config['cache']  # old cache

    cache = beta * cache + (1-beta) * np.power(dw, 2)  # update cache
    w -= lr * dw / (np.sqrt(cache) + eps)  # update parameters
    next_w = w

    # update config
    config['cache'] = cache
    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################
    return next_w, config


def adam(w, dw, config=None):
    """
    Uses the Adam update rule, which incorporates moving averages of both the
    gradient and its square and a bias correction term.

    config format:
    - learning_rate: Scalar learning rate.
    - beta1: Decay rate for moving average of first moment of gradient.
    - beta2: Decay rate for moving average of second moment of gradient.
    - epsilon: Small scalar used for smoothing to avoid dividing by zero.
    - m: Moving average of gradient.
    - v: Moving average of squared gradient.
    - t: Iteration number.
    """
    if config is None: config = {}
    config.setdefault('learning_rate', 1e-3)
    config.setdefault('beta1', 0.9)
    config.setdefault('beta2', 0.999)
    config.setdefault('epsilon', 1e-8)
    config.setdefault('m', np.zeros_like(w))
    config.setdefault('v', np.zeros_like(w))
    config.setdefault('t', 1)

    # next_w = None
    ###########################################################################
    # TODO: Implement the Adam update formula, storing the next value of x in #
    # the next_w variable. Don't forget to update the m, v, and t variables   #
    # stored in config.                                                       #
    ###########################################################################
    # unpack config
    lr = config['learning_rate']
    beta1 = config['beta1']
    beta2 = config['beta2']
    m = config['m']
    v = config['v']
    t = config['t']
    eps = config['epsilon']

    m = beta1 * m + (1-beta1) * dw  # update m
    v = beta2 * v + (1-beta2) * np.power(dw, 2)  # update v

    mt = m / (1 - beta1 ** t)  # bias correction m
    vt = v / (1 - beta2 ** t)  # bias correction v

    w -= lr * mt / (np.sqrt(vt) + eps)  # update parameters
    next_w = w

    # update config
    config['m'] = m
    config['v'] = v
    config['t'] += 1
    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################
    return next_w, config
