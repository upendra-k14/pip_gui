A short intro of pip_tkinter
============================

.. toctree::
    :maxdepth: 4

The `pip` GUI in intended to provide a simple and minimalistic GUI application
for installing and managing Python packages. This application is specifically
targeted towards people using Python, but not familiar with command line in
linux, Mac OS or Windows OS.

In order to make the design of `pip` GUI consistent, following a set of design
philosophies is a good practice.

.. Note::

    Before going through the design philosophies, if you are not familiar with
    process of designing a GUI application, you can refer to some excellent UI
    design resources available :

    1. Don't design like a Programmer series : `[Part1] <http://www.uxdesignedge.com/2010/03/dont-design-like-a-programmer>`_,`[Part2] <http://www.uxdesignedge.com/2011/06/don%E2%80%99t-design-like-a-programmer-part-2>`_ ,`[Part3] <http://www.uxdesignedge.com/2011/11/don%E2%80%99t-design-like-a-programmer-part-3>`_
        These three series describe UI design concisely with a lot of
        summarized points about UI design.

    2. `User Interface Design for Programmers ( by Joel Spolsky) <http://dbmanagement.info/Books/Others/User_Interface_Design_For_Programmers_(Joel_Spolsky,_2001).pdf>`_
        This book contains one of the excellent ideas of UI design explained
        with very simple and practical examples.

    3. `Designing Interfaces (by Jenifer Tidwell) <http://internativa.com.br/mobile/Livro%20-%20Designing%20Interfaces,%202nd%20Edition,%202010.pdf>`_
        It explains UI design in technical depth and explains some concepts like
        affordances, visual hierarchy, navigational distance and use of color.
        In addition to it, use case of almost all UI elements like selector,
        pagination, cancellability, button groups, geometry managers etc. are
        thoroughly explained.

        Most importantly almost all chapters are followed by a Patterns section
        which includes all requirements to be achieved by a good software.
        I think this is one of the best resources to learn UI design in a
        technical manner. This book explains almost everything from organizing
        the content, navigation, organizing a page, using different UI elements
        to fulfill tasks, handling “verbs” of a interface ( i.e how to present
        actions and commands), discussing cognitive effects of data
        representation ( information graphics ) and finally tells how to use
        graphic design patterns to improve aesthetics and look & feel of UI.


    4. A collection of many UI design resources
        https://whitneyhess.com/blog/2009/06/30/so-you-wanna-be-a-user-experience-designer-step-1-resources/

    5. UX Design Concepts
        http://www.usability.gov/what-and-why/user-experience.html
