Sublime Regexp Replace Plugin
=============================

This plugin is an attempt to have a find/replace tool that uses regular expressions.

Instructions
============

Install this repository in your Packages/ directory, or using the package control plugin.

Configure a keyboard shortcut to the command `regexp_replace_window`.

When run, the command will display an input window. Start typing your regexp. You will see
the matches displayed on the screen as you type.

When you type enter, the window disappears and a new input window appears ; you can type
here your replacement expression.

You can use grouping with parentheses : to have what you matched in the replacement, use
python's groups: {1}, {2}, ...

Right now, there is no support for named groups, but if there is demand, it might just
be done.