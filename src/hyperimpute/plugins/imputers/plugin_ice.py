# stdlib
import time
from typing import Any, List, Union

# third party
import pandas as pd

# hyperimpute absolute
import hyperimpute.plugins.core.params as params
import hyperimpute.plugins.imputers.base as base
from hyperimpute.plugins.imputers.plugin_hyperimpute import plugin as base_model


class IterativeChainedEquationsPlugin(base.ImputerPlugin):
    """Imputation plugin for completing missing values using the Multivariate Iterative chained equations Imputation strategy.

    Method:
        Multivariate Iterative chained equations(MICE) methods model each feature with missing values as a function of other features in a round-robin fashion. For each step of the round-robin imputation, we use a BayesianRidge estimator, which does a regularized linear regression.

    Args:
        max_iter: int, default=500
            maximum number of imputation rounds to perform.
        random_state: int, default set to the current time.
            seed of the pseudo random number generator to use.

    Example:
        >>> import numpy as np
        >>> from hyperimpute.plugins.imputers import Imputers
        >>> plugin = Imputers().get("ice")
        >>> plugin.fit_transform([[1, 1, 1, 1], [np.nan, np.nan, np.nan, np.nan], [1, 2, 2, 1], [2, 2, 2, 2]])
                  0         1         2         3
        0  1.000000  1.000000  1.000000  1.000000
        1  1.333333  1.666667  1.666667  1.333333
        2  1.000000  2.000000  2.000000  1.000000
        3  2.000000  2.000000  2.000000  2.000000
    """

    def __init__(
        self,
        max_iter: int = 1000,
        initial_strategy: int = 0,
        imputation_order: int = 0,
        random_state: Union[int, None] = 0,
        model: Any = None,
    ) -> None:
        super().__init__()

        if model:
            self._model = model
            return

        if not random_state:
            random_state = int(time.time())

        self._model = base_model(
            classifier_seed=["logistic_regression"],
            regression_seed=["linear_regression"],
            imputation_order=imputation_order,
            baseline_imputer=initial_strategy,
            random_state=random_state,
            n_inner_iter=max_iter,
            n_outer_iter=1,
            class_threshold=5,
        )

    @staticmethod
    def name() -> str:
        return "ice"

    @staticmethod
    def hyperparameter_space(*args: Any, **kwargs: Any) -> List[params.Params]:
        return [
            params.Integer("max_iter", 100, 1000, 100),
            params.Integer(
                "initial_strategy",
                0,
                len(base_model.initial_strategy_vals) - 1,
            ),
            params.Integer(
                "imputation_order",
                0,
                len(base_model.imputation_order_vals) - 1,
            ),
        ]

    def _fit(
        self, X: pd.DataFrame, *args: Any, **kwargs: Any
    ) -> "IterativeChainedEquationsPlugin":
        self._model.fit(X, *args, **kwargs)

        return self

    def _transform(self, X: pd.DataFrame) -> pd.DataFrame:
        return self._model.transform(X)


plugin = IterativeChainedEquationsPlugin
