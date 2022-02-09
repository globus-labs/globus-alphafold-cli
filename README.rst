Globus Alphafold CLI
====================

This CLI uses Globus Flows to run Alphafold at Argonne's Leadership Computing Facility using funcX. 
The CLI accepts the path to a FASTA file as input before uploading the file to ALCF's Eagle file system.
The Alphafold job is dispatched to ALCF resources using funcX and the results are written to Eagle for the user to collect.

To run this example you will need to be a member of the `Globus AlphaFold Group`. 
This group restricts access to both the Globus endpoint to read and write data and the funcX endpoint deployed at ALCF. 

You can request access `here <https://app.globus.org/groups/2f76ac1f-3e68-11ec-976c-89c391007df5/about>`_ 


Quickstart
==========

To run Alphafold against a FASTA file you can::
    
    $ python cli.py run --fasta /path/to/file.fasta

This will describe the preprocessing steps and upload the file to ALCF. A flow will then be started and the run id will be printed.

.. note:: The first time you use the CLI's run function you will be prompted to login and grant permission to the use the flow and access your email address to send notifications.

You can check the status of a run via the flows webapp or using the CLI's status command::

    $ python cli.py status --run_id <run_id>


Reference
=========

The Alphafold tool is executed within a Singularity container. The container used is available `here <https://github.com/hyoo/alphafold_singularity>`_

Complete documentation for funcX is available `here <https://funcx.readthedocs.io>`_

