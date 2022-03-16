"""Test the assembling"""
# pylint: disable=missing-docstring


from robotsline import commands, handlers, models


def test_asking_a_robot_to_assemble_foo_and_bar():
    # Given a factory with enough stock
    # And a robot at assembly line
    robot = models.Robot(id_=1, location=models.Location.ASSEMBLY_LINE)
    stock = models.Stock(foos_nb=1, bars_nb=1)
    factory = models.RoboticFactory(robots=[robot], stock=stock)

    # When I ask her to assemble
    assemble = commands.Assemble(robot_id=robot.id_)
    handlers.execute(assemble, on_factory=factory)

    # the robot is assembling
    assert robot.status == "Assembling a foobar..."
    # and stock is lower
    assert factory.stock.foos == 0
    assert factory.stock.bars == 0


def test_asking_a_robot_to_assemble_but_she_is_busy():
    # Given a robot in a factory with enough stock, and a robot moving to the cafeteria
    robot = models.Robot(id_=1, location=models.Location.ASSEMBLY_LINE)
    stock = models.Stock(foos_nb=1, bars_nb=1)
    factory = models.RoboticFactory(robots=[robot], stock=stock)
    factory.move(robot.id_, destination="cafeteria")

    # When I ask her to assemble
    assemble = commands.Assemble(robot_id=robot.id_)
    handlers.execute(assemble, on_factory=factory)

    # Then the robot is still moving
    assert robot.status == "Moving"
    # And stock didn't changed
    assert factory.stock.foos == 1
    assert factory.stock.bars == 1
    # And foobar is not yet produced
    assert factory.stock.foobars == []

# def test_it_always_takes_2_seconds_to_assemble_a_foobar():
#     # Given a factory with a foo and a bar in stock, and 100% chance of assembling success
#     # And a robot at assembly line
#     factory = robotic_factory(assembly_success_rate=1)
#     robot = models.Robot(id_=1, location=models.Location.ASSEMBLY_LINE)
#     factory.robots.append(robot)

#     # When I ask her to assemble a foobar
#     assemble = commands.Assemble(robot_id=robot.id_)
#     handlers.execute(assemble, on_factory=factory)
#     pass
