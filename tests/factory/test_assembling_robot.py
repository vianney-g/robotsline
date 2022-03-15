"""Test the assembling"""
# pylint: disable=missing-docstring


from robotsline import commands, handlers, models


def test_asking_a_robot_to_assemble_foo_and_bar(robotic_factory):
    # Given a factory with enough stock
    factory = robotic_factory()
    factory.stock.foos = 1
    factory.stock.bars = 1

    # And a robot at assembly line
    robot = models.Robot(id_=1, location=models.Location.ASSEMBLY_LINE)
    factory.robots.append(robot)

    # When I ask it to assemble
    assemble = commands.Assemble(robot_id=robot.id_)
    handlers.execute(assemble, on_factory=factory)

    # the robot is assembling
    assert robot.status == "Assembling a foobar..."
    # and stock is lower
    assert factory.stock.foos == 0
    assert factory.stock.bars == 0


def test_asking_a_robot_to_assemble_but_she_is_busy(robotic_factory):
    # Given a robot in a factory with enough stock, but robot is moving to cafeteria
    factory = robotic_factory(1)
    factory.stock.foos = 1
    factory.stock.bars = 1
    factory.stock.foobars = []
    robot = factory.robots[0]
    factory.move(robot.id_, destination="cafeteria")

    # When I ask it to assemble
    assemble = commands.Assemble(robot_id=robot.id_)
    handlers.execute(assemble, on_factory=factory)

    # Then the robot is still moving
    assert robot.status == "Moving"
    # And stock didn't changed
    assert factory.stock.foos == 1
    assert factory.stock.bars == 1
    # And foobar is not yet produced
    assert factory.stock.foobars == []
