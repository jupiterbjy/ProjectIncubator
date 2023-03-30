"""
Olympic rings demo
"""

import turtle


# Create instance of Turtle class, and set shape to Turtle shape.
turtle_instance = turtle.Turtle()
turtle_instance.shape("turtle")

# Turtle is initially 'Pen Down' mode, which means line will be drawn
# whenever Turtle moves.


# Draw blue circle, with radius 50
turtle_instance.pencolor("blue")
turtle_instance.circle(50)


# Turtle is still in 'Pen Down' state.
# To prevent Turtle drawing lines while moving we need to pull pen up.
turtle_instance.up()


# Move up a bit so that we can draw another ring bit away.
# This is *ABSOLUTE* coordinate, not relative.
turtle_instance.goto(100, 0)


# Put Turtle back on 'Pen Down' mode.
turtle_instance.down()


# Draw black circle - but this time with 5 pen thickness.
turtle_instance.width(5)
turtle_instance.pencolor("black")
turtle_instance.circle(50)


# Pen up, move again, pen down, same as before
turtle_instance.up()
turtle_instance.goto(200, 0)
turtle_instance.down()


# Draw red circle - also with 5 pen thickness. Why the heck blue one aren't tho...
turtle_instance.width(5)
turtle_instance.pencolor("red")
turtle_instance.circle(50)


# Pen up, move again, pen down
turtle_instance.up()
turtle_instance.goto(50, -50)
turtle_instance.down()


# Draw yellow circle
turtle_instance.width(5)
turtle_instance.pencolor("yellow")
turtle_instance.circle(50)


# Pen up, move again, pen down
turtle_instance.up()
turtle_instance.goto(150, -50)
turtle_instance.down()


# Draw green circle
turtle_instance.width(5)
turtle_instance.pencolor("green")
turtle_instance.circle(50)


# hold screen from closing so that you can take screenshot of it.
# Pretty sure not required on interactive python shell.
input("Press enter to exit: ")
