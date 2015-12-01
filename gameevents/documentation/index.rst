.. gameevents documentation master file, created by
   sphinx-quickstart on Wed Oct 28 10:12:39 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to gameevents's documentation!
######################################


**********
Components
**********

==============
Gameevents App
==============

.. automodule:: gameevents_app
   :members:

========
REST API
========
   
.. autoflask:: gameevents_app:create_app(testing=False)
   :undoc-static:
   
=====
Views
=====
   
.. automodule:: gameevents_app.views
   :members:

==========
Controller
==========
   
.. automodule:: gameevents_app.controller
   :members:

======
Models
======

Client
------
   
.. automodule:: gameevents_app.models.client
   :members:


Sessions
--------

.. automodule:: gameevents_app.models.session
   :members:


Game Events
-----------

.. automodule:: gameevents_app.models.gameevent
   :members:
   
      
======
Errors
======
   
.. automodule:: gameevents_app.errors
   :members:


Indices and tables
##################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

