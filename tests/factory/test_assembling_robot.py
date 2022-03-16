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


def test_it_always_takes_2_seconds_to_assemble_a_foobar():
    # Given a factory with a foo and a bar in stock
    # And 100% chance of assembling success
    # And a robot at assembly line
    robot = models.Robot(id_=1, location=models.Location.ASSEMBLY_LINE)
    stock = models.Stock(foos_nb=1, bars_nb=1, foobars=[])
    factory = models.RoboticFactory([robot], stock=stock, assembly_success_rate=1)

    # When I ask her to assemble a foobar
    # And I wait 2 seconds
    assemble = commands.Assemble(robot_id=robot.id_)
    handlers.execute(assemble, on_factory=factory)
    handlers.execute(commands.Wait(2), on_factory=factory)

    # the robot is idling at the assembly line
    assert robot.status == "Idle"
    assert robot.state.location == models.Location.ASSEMBLY_LINE
    # and stock is lower
    assert factory.stock.foos == 0
    assert factory.stock.bars == 0
    # but a foobar has been created
    assert len(stock.foobars) == 1


def test_assembling_a_foobar_may_fail():
    # Given a factory with a foo and a bar in stock
    # And no chance at all of assembling success
    # And a robot at assembly line
    robot = models.Robot(id_=1, location=models.Location.ASSEMBLY_LINE)
    stock = models.Stock(foos_nb=1, bars_nb=1, foobars=[])
    factory = models.RoboticFactory([robot], stock=stock, assembly_success_rate=0)

    # When I ask her to assemble a foobar
    # And I wait 2 seconds
    assemble = commands.Assemble(robot_id=robot.id_)
    handlers.execute(assemble, on_factory=factory)
    handlers.execute(commands.Wait(2), on_factory=factory)

    # the robot is idling at the assembly line
    assert robot.status == "Idle"
    assert robot.state.location == models.Location.ASSEMBLY_LINE
    # and stock of foos is lower but the bar can be reused
    assert factory.stock.foos == 0
    assert factory.stock.bars == 1
    # And foobar has not been created
    assert len(stock.foobars) == 0
