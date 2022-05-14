"""MultipleIfConditions"""

from typing import Text, Iterable

from launch.conditions import evaluate_condition_expression
from launch.condition import Condition
from launch.launch_context import LaunchContext
from launch.some_substitutions_type import SomeSubstitutionsType
from launch.utilities import normalize_to_list_of_substitutions


class MultipleIfConditions(Condition):
    """
    Encapsulates multiple if conditions to be evaluated when launching.
    These conditions take a string expression that is lexically evaluated as a
    boolean, but the expressions may consist of :py:class:`launch.Substitution`
    instances. Each expression must be true for the entire condition to be true.
    See :py:func:`evaluate_condition_expression` to understand what constitutes
    a valid condition expression.
    """

    def __init__(self, predicate_expressions: Iterable[SomeSubstitutionsType]) -> None:
        self.__predicate_expressions = [normalize_to_list_of_substitutions(
            expr) for expr in predicate_expressions]
        super().__init__(predicate=self._predicate_func)

    def _predicate_func(self, context: LaunchContext) -> bool:
        return all(evaluate_condition_expression(context, expr) for expr in self.__predicate_expressions)

    def describe(self) -> Text:
        """Return a description of this Condition."""
        return self.__repr__()
