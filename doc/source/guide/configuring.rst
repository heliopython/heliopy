Configuring
===========

HelioPy comes with a sample 'heliopyrc' file. In order to customise the file
make a copy of it at ``~/.heliopy/heliopyrc`` and edit that copy.
The default contents of the file are:

.. literalinclude:: ../../../heliopy/heliopyrc

Alternatively the copy included with HelioPy can be directly edited.
To get the location of the configuration file in a python session run

.. code-block:: python

   from heliopy.util import config
   print(config.get_config_file())

This will print the location of the configuration file that HelioPy is reading
in.
