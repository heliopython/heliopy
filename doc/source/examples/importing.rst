Importing data
==============

heliopy has data import modules for many different missions. For a list of data
that can be imported, see the :mod:`heliopy.data` module. In this example,
we'll have a look at importing and viewing some magnetic field data from WIND.

First, import the modules for use later

.. literalinclude:: /scripts/importing_data.py
   :lines: 1-3

Next, define the start time and end time of the data to import

.. literalinclude:: /scripts/importing_data.py
   :lines: 5-6

Next, import the data. If the data isn't downloaded locally heliopy will
automatically download the data.

.. literalinclude:: /scripts/importing_data.py
   :lines: 8

heliopy uses pandas DataFrames throughout when dealing with data. To see the
different columns in our data set use data.keys()

.. literalinclude:: /scripts/importing_data.py
   :lines: 10-11

The 'Time' column gives a timestamp for each datum, and we also have the
magnetic field in a GSE co-ordinate system. Each column can be accessed using
`data[key]`.

Now we've imported the data, lets plot it. To do this we can use matplotlib:

.. literalinclude:: /scripts/importing_data.py
   :lines: 13-17

This should show a 3-component plot of the magnetic field.
