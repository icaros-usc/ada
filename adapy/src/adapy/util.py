from prpy.exceptions import PrPyException


class AdaPyException(PrPyException):
    pass


def find_adapy_resource(relative_path, package='adapy'):
    from catkin.find_in_workspaces import find_in_workspaces

    paths = find_in_workspaces(project=package, search_dirs=['share'],
                               path=relative_path, first_match_only=True)

    if paths and len(paths) == 1:
        return paths[0]
    else:
        raise IOError('Loading AdaPy resource "{:s}" failed.'.format(
                      relative_path))


def or_to_ros_trajectory(robot, traj):
    """ Convert an OpenRAVE trajectory to a ROS trajectory.

    @param robot: OpenRAVE robot
    @type  robot: openravepy.Robot
    @param traj: input trajectory
    @type  traj: openravepy.Trajectory
    """
    from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

    if traj.GetEnv() != robot.GetEnv():
        raise ValueError(
            'Robot and trajectory are not in the same environment.')

    cspec = traj.GetConfigurationSpecification()
    dof_indices = cspec.ExtractUsedIndices(robot)
    time_from_start = 0.

    traj_msg = JointTrajectory(
        joint_names=[ robot.GetJointFromDOFIndex(dof_index).GetName()
                      for dof_index in dof_indices ]
    )
    
    for iwaypoint in xrange(traj.GetNumWaypoints()):
        waypoint = traj.GetWaypoint(iwaypoint)

        time_from_start += cspec.ExtractDeltaTime(waypoint)
        q = cspec.ExtractJointValues(waypoint, robot, dof_indices, 0)
        qd = cspec.ExtractJointValues(waypoint, robot, dof_indices, 1)
        qdd = cspec.ExtractJointValues(waypoint, robot, dof_indices, 2)

        if q is None:
            raise ValueError('Trajectory does not contain joint values')
        elif qdd is not None and qd is None:
            raise ValueError('Trajectory contains accelerations,'
                             ' but not velocities.')

        traj_msgs.points.append(
            JointTrajectoryPoint(
                positions=q,
                velocities=qd or [],
                accelerations=qdd or [],
                time_from_start=time_from_start
            )
        )

    assert numpy.isclose(time_from_start, traj.GetDuration())

    return traj_msg
