
.. contents::

1 librusapi - A Librus Synergia scraper
---------------------------------------

Goal of this project is to free students from the limitations of Librus Synergia software
mainly: giving the user **fresh** information unlike their mobile app that can only
refresh every **3h** or so.

2 Install
---------

.. code:: sh

    pip install librusapi

3 Tech used
-----------

- written in ``python`` developed with ``3.9`` in mind

- ``requests`` library for fetching data, mainly html

- ``BeautifulSoup4`` library for parsing the data

3.1 Development specific
~~~~~~~~~~~~~~~~~~~~~~~~

- ``mypy`` for type checking

- ``pytest`` for running tests

- ``pdoc`` for creating html documentation

4 Quick start
-------------

Example usage of the API

4.1 Getting the timetable
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from librusapi.token import get_token
    from librusapi import timetable

    token = get_token('username', 'password')
    lesson_units = timetable.lesson_units(token)

    for lu in lesson_units:
        print(lu)

5 Working on the project
------------------------

.. code:: sh

    git clone https://github.com/ravensiris/librusapi
    cd librusapi
    python -m venv venv
    # This may be different depending on your operating system and shell
    source ./venv/bin/activate
    pip install -r requirements.txt
    # Installing as an editable library
    pip install -e .

Now you can import ``librusapi`` in your project

5.1 Generating docs
~~~~~~~~~~~~~~~~~~~

.. code:: sh

    pdoc --html librusapi

6 Status
--------

Currenty you can:

- Authenticate and get a token

- List all lessons in a timetable
