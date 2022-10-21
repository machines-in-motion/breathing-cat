#.rst:
#
# .. cmake:command:: FOO
#
#    Simply outputs a "Foo!" warning.
#
macro(FOO)

    message(WARNING, "Foo!)

endmacro(FOO)
