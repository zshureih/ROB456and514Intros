#!/usr/bin/env python3

import numpy as np

from world_state import WorldState
from robot_state import RobotState


# A generic Gaussian - note that this is *not* a normalized probability distribution function
def normal_dist(x, mu, standard_deviation):
    exp_value = np.exp(-np.power(x - mu, 2.0) / (2 * np.power(standard_deviation, 2.0)))
    scl_value = standard_deviation * np.sqrt(2 * np.pi)
    return exp_value / scl_value


# Door sensor - needs to now the world state to answer questions
class DoorSensor:
    def __init__(self):
        self.prob_see_door_if_door = 0.8
        self.prob_see_door_if_no_door = 0.2
        self.prob_not_see_door_if_door = 1 - self.prob_see_door_if_door
        self.prob_not_see_door_if_no_door = 1 - self.prob_see_door_if_no_door

    # ground truth
    @staticmethod
    def is_in_front_of_door(ws, rs):
        """
        return ground truth
        :param ws: world state (has doors)
        :param rs: robot state (has robot location)
        :return:
        """
        # Just call world state function with robot_loc
        return ws.is_in_front_of_door(rs.robot_loc)

    # Roll the dice and return sensor value
    def sensor_reading(self, ws: object, rs: object) -> object:
        """
        Generate a sensor reading using probabilities
        :param ws: world state (has doors)
        :param rs: robot state (has robot location)
        :return:
        """
        # begin homework 2 : problem 1
        # Flip the coin...
        coin = np.random.uniform(0, 1)
        sensor_reading = 0
        # print(coin)
        if coin < self.prob_see_door_if_no_door:
            sensor_reading = 0 
        else:
            sensor_reading = 1
        ground_truth = self.is_in_front_of_door(ws, rs)
        # print(sensor_reading)
        # print(ground_truth)

        # Determine percentage in front of door
        # prob(truth | sensor) = p(sensor | truth) * p(truth) / (p(sensor | truth) * p(truth) + p(sensor | ~truth) * p(~truth))
        pst = 0  # prob(sensor | truth)
        not_pst = 0
        if ground_truth and sensor_reading: 
            pst = self.prob_see_door_if_door  # P(z|door)
            not_pst = self.prob_see_door_if_no_door #P(z|~door)
        if ground_truth and not sensor_reading: 
            pst = self.prob_not_see_door_if_door #P(~z|door) 
            not_pst = self.prob_not_see_door_if_no_door #P(~z|~door)
        if not ground_truth and sensor_reading:
            pst = self.prob_see_door_if_no_door #P(z|~door)
            not_pst = self.prob_not_see_door_if_no_door #P(~z|~door)
        if not ground_truth and not sensor_reading: 
            pst = self.prob_not_see_door_if_no_door  # p(~z|~door)
            not_pst = self.prob_not_see_door_if_door # p(~z|door)

        p_truth = (len(ws.doors) * ws.door_width) / ws.n_bins  # probability that there is a door
        not_p_truth = 1 - p_truth
        prob = (pst * p_truth) / ((pst * p_truth) + (not_pst * not_p_truth))
        n_prob = 1 - prob
        print(prob)
        print(n_prob)
        # end homework 2 : problem 1

        return True

    # set the probabilities based on the gui
    def set_probabilities(self, in_prob_see_door_if_door, in_prob_see_door_if_not_door):
        self.prob_see_door_if_door = in_prob_see_door_if_door
        self.prob_see_door_if_no_door = in_prob_see_door_if_not_door


if __name__ == '__main__':
    ws_global = WorldState()

    ds_global = DoorSensor()

    rs_global = RobotState()

    # Robot should be at 0.5, no door at 0.5, so this should be false
    print("Testing probabilities for robot NOT in front of door")
    rs_global.robot_loc = ws_global.place_robot_not_in_front_of_door()
    if ds_global.is_in_front_of_door(ws_global, rs_global):
        raise ValueError("The robot should NOT be in front of a door")

    # Check that we get our probabilites back (mostly)
    count_returned_true = 0
    for i in range(0, 1000):
        if ds_global.sensor_reading(ws_global, rs_global):
            count_returned_true += 1

    prob_count = count_returned_true / 1000
    if abs(prob_count - ds_global.prob_see_door_if_no_door) > 0.1:
        raise ValueError("Probability should be close to {}, is {}".format(ds_global.prob_see_door_if_no_door, prob_count))

    print("Testing probabilities for robot in front of door")
    rs_global.robot_loc = ws_global.place_robot_in_front_of_door()
    if not ds_global.is_in_front_of_door(ws_global, rs_global):
        raise ValueError("The robot SHOULD be in front of a door")

    # Check that we get our probabilities back (mostly) when in front of the door
    count_returned_true = 0
    for i in range(0, 1000):
        if ds_global.sensor_reading(ws_global, rs_global):
            count_returned_true += 1

    prob_count = count_returned_true / 1000
    if abs(prob_count - ds_global.prob_see_door_if_door) > 0.1:
        raise ValueError("Probability should be close to {}, is {}".format(ds_global.prob_see_door_if_door, prob_count))

    print("Passed tests")
