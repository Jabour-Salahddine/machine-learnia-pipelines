
'''
import pandas as pd
from zenml import step
from typing_extensions import Annotated


@step
def step1() -> Annotated[pd.DataFrame, "ratings_df"]:
    ratings_df = pd.DataFrame({
    'userId':   [1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
    'movieId':  [10, 10, 20, 20, 30, 30, 40, 40, 50, 50],
    'rating':   [4.0, 3.5, 5.0, 2.0, 4.5, 3.0, 4.0, 2.5, 5.0, 4.0]
})
    return ratings_df
'''    