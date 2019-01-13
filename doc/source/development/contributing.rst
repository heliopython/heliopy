Contributing to HelioPy
=======================

HelioPy aims to be a comprehensive Python package for downloading and working
with data from heliospheric and planetary missions. The people who help
develop or contribute to HelioPy are varied in ability and experience, with
everyone being volunteers who work on in in their spare time. We pride ourselves
on being a welcoming community and we would love you to contribute!

If you have any questions, comments or just want to say hello,
we have online chat on `Matrix`_ which requires no registration or a bit more
old school, a `Google Group`_ which you can email.

.. _Matrix: https://riot.im/app/#/room/#heliopy:matrix.org
.. _Google Group: https://groups.google.com/forum/#!forum/heliopy

How To Contribute
-----------------

Documentation
#############

Most of the items within HelioPy are documented `online here`_.
This documentation is not only for the code, but contains setup
instructions, quick start guides, and worked examples. However, documentation
is never complete; there are always areas that could be expanded upon or could
do with some proof reading to check whether what is written is easy to follow
and understandable. If parts are confusing or difficult to follow, we would
love suggestions or improvements!

.. _online here: https://docs.heliopy.org/en/stable/

Code
####

There are a list of open issues on Github `issues`_ where all the known
bugs and suggestions for improvement are kept. Some issues have
the `Good first issue`_ label, which is a good place to start. These are issues
that can be tackled with a minimum understanding of the HelioPy codebase.

.. _issues: https://github.com/heliopython/HelioPy/issues
.. _Good first issue: https://github.com/heliopython/heliopy/issues?q=is%3Aissue+is%3Aopen+label%3A%22Good+first+issue%22

How to setup a work environment
-------------------------------

We recommend using miniconda or Anaconda instead of native operating
system Python packages as it makes installing and debugging HelioPy much easier.
To create a miniconda environment, follow the installation `instructions here`_.

Next, setup the conda environment:

.. code:: bash

    conda create -n heliopy-dev python
    source activate heliopy-dev

This will create a new conda environment called heliopy-dev. The next step is
to install a development version of HelioPy.

If you have a `GitHub`_ account, you can `fork`_ the `HelioPy repository`_
(the fork button is to the top right) and use that url for the ``git clone``.
This will make submitting changes easier in the long term for you:

.. code:: bash

    git clone https://github.com/heliopython/heliopy.git heliopy
    cd heliopy
    pip install -r requirements/test.txt
    pip install -e .

Edit the code
--------------

Now you have the latest version of HelioPy installed and are ready to work on
it! When you start making changes you will want to create a new git branch
to work on:

.. code:: bash

    git checkout -b my_fix

You can change ``my_fix`` to anything you prefer. If you get stuck or want
help, just `ask here`_!

.. _miniconda: https://conda.io/miniconda.html
.. _instructions here: https://conda.io/docs/user-guide/install/index.html
.. _git: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git
.. _GitHub: https://github.com/
.. _fork: https://guides.github.com/activities/forking/
.. _HelioPy repository: https://github.com/heliopython/heliopy
.. _ask here: https://groups.google.com/forum/#!forum/heliopy

Submit the code
---------------

Once you have made some changes, you need to commit the changes:

.. code:: bash

    git commit -a -m '<message>'

where ``<message>`` is replaced with a short message explaining the changes
you have made.

The next step is to submit the changes back to HelioPy by submitting a
Pull Request (PR) using GitHub.  If you are new to pull requests,
here is a `friendly guide`_. Your pull request will then be checked over by
someone else for bugs/any suggestions for improvement, before being merged
into the main code base of HelioPy.

If you do not have time to finish what you started on or ran out of time and
do not want to submit a pull request, you can create a git patch and send it
to the `Google Group`_. This way, you still get acknowledged for the work you
did and this can be viewed within the HelioPy git history.

.. code:: bash

    git format-patch master --stdout > my_fix.patch

Just remember, if you hit any problems get in touch!

.. _friendly guide: https://guides.github.com/activities/hello-world/
.. _Google Group: https://groups.google.com/forum/#!forum/heliopy
