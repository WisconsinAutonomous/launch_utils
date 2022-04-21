from launch import LaunchDescription


def AddLaunchArgument(
        ld: LaunchDescription, arg: "Any", default: "Any", **kwargs) -> "LaunchConfiguration":
    """Helper method to add a launch argument to a LaunchDescription"""
    from launch.actions import DeclareLaunchArgument

    ld.add_action(DeclareLaunchArgument(arg, default_value=default, **kwargs))
    return GetLaunchArgument(arg)


def SetLaunchArgument(ld: LaunchDescription, arg: "Any", value: "Any",  **kwargs) -> None:
    """Helper method to set a launch argument of a LaunchDescription"""
    from launch.actions import SetLaunchConfiguration

    ld.add_action(SetLaunchConfiguration(name=arg, value=value, **kwargs))


def GetLaunchArgument(name: str) -> "LaunchConfiguration":
    """Helper method to get a launch configuration value"""

    from launch.substitutions import LaunchConfiguration

    return LaunchConfiguration(name)


def AddComposableNode(
    ld: LaunchDescription,
    *,
    plugin: str,
    executable: str,
    composable_conditions: "List[List[SomeSubstitutionType]" = [],
    node_conditions: "List[List[SomeSubstitutionType]]" = [],
    container: str = "container",
    composable_node_kwargs: dict = {},
    load_composable_nodes_kwargs: dict = {},
    node_kwargs: dict = {},
    add_as_regular_node: bool = True,
    **kwargs
) -> None:
    """
    Conditionally add a node dependent on whether the LaunchConfiguration ``container`` is
    not "". If not "", it will load the node into the composable container using ``LoadComposableNodes``.
    In this case, "use_intra_process_comms" will be set to true. If ``container`` is "",
    it will simply load the node using ``Node`` without intraprocess comms.

    If ``add_as_regular_node`` is set to False (defaults to True), it will not create a ``Node`` if ``container`` is unset.
    """

    from launch_utils.launch.conditions import MultipleIfConditions
    from launch_utils.launch.substitutions import QuoteWrappedPythonExpression

    from launch_ros.actions import Node, LoadComposableNodes
    from launch_ros.descriptions import ComposableNode

    container = GetLaunchArgument(container)

    # Add a node the container only if the container launch argument is set
    composable_condition = QuoteWrappedPythonExpression([container, " != ''"])
    composable_nodes = [
        ComposableNode(
            plugin=plugin,
            extra_arguments=[{"use_intra_process_comms": True}],
            **composable_node_kwargs,
            **kwargs,
        )
    ]
    load_composable_nodes = LoadComposableNodes(
        condition=MultipleIfConditions(
            [composable_condition, *composable_conditions]),
        composable_node_descriptions=composable_nodes,
        target_container=container,
        **load_composable_nodes_kwargs,
    )
    ld.add_action(load_composable_nodes)

    # Add a regular nod if container is unset AND add_as_regular_node is true
    node_condition = QuoteWrappedPythonExpression([container, " == ''"])
    node = Node(
        condition=MultipleIfConditions([node_condition, *node_conditions]),
        executable=executable,
        **node_kwargs,
        **kwargs,
    )
    if add_as_regular_node:
        ld.add_action(node)
