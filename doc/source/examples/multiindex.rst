##############################################
A brief guide to pandas multi-index dataframes
##############################################

************
Introduction
************
The data sets imported by heliopy are returned in a
:class:`pandas.DataFrame`. Most data sets have a
single variable for the :class:`DataFrame` index. In this case DataFrame can be thought of as
storing multiple variables, each of which depend on the same dependent
variable. For example the x component of magnetic field depends only on time
ie. :math:`B_{x} \left (t \right )`.

Particle distribution functions have more than one dependent variable however.
Typically the distribution is measured as a function of time, energy, and two
angles, ie. :math:`f \left ( t, E, \theta, \phi \right )`.

*****************************
Making multi-index dataframes
*****************************
As a simple example, lets make a multi-index DataFrame to imitate a particle
distribution function. First, set the index values

.. literalinclude:: /scripts/multiindex.py
   :lines: 1-11

The index values can then be created from
:meth:`pandas.MultiIndex.from_product`, and the complete DataFrame created
from :meth:`pandas.DataFrame`:

.. literalinclude:: /scripts/multiindex.py
   :lines: 12-25

The distribution function is sorted first by energy, then by theta, and then by
phi.

***********************************
Working with multi-index dataframes
***********************************

Looping through an index level
==============================
To loop through the energy levels with the index label ``'theta'``:

.. literalinclude:: /scripts/multiindex.py
   :lines: 27-34

``theta`` will give the value of the current index, and ``theta_dist`` will
give the reduced DataFrame at each value of ``theta``.

Adding an extra index level
===========================
Suppose we have two data frames, ``df1`` and ``df2``, and want to put these in
together with a new multiindex level::

    df1['newlevel'] = 1
    df2['newlevel'] = 2
    df = pd.concat([df1, df2])
    df = df.set_index('newlevel', append=True)

Re-ordering index levels
========================
Suppose we have a data frame with the index column labels
``['E', 'Theta', 'Phi']``, and we want to change the order of the levels.
This can be done with ``reorder_levels``::

    df = df.reorder_levels(['Theta', 'Phi', 'E'], axis=0)

Getting index values
====================
Sometimes it is useful to extract the index values as a standard numpy array.
This can be done with ``get_level_values()``::

    values = df.index.get_level_values('index_label')
    values = np.array(values)
