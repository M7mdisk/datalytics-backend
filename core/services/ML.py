import numpy as np
import pandas as pd
from core.models import MLModel, Dataset, Column
from sklearn.linear_model import LogisticRegression, LinearRegression, BayesianRidge
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.svm import SVC, SVR
from sklearn.naive_bayes import GaussianNB

regression_models = {
    "LINREG": LinearRegression,
    "BR": BayesianRidge,
    "SVR": SVR,  # Support Vector Regression
    "DTR": DecisionTreeRegressor,
}

classification_models = {
    "LOGREG": LogisticRegression,
    "SVC": SVC,  # Support Vector classifier
    "DTC": DecisionTreeClassifier,
    "RFC": RandomForestClassifier,
}


class MLModelService:
    def __init__(
        self, df: pd.DataFrame, target: Column, features: list[Column]
    ) -> None:
        self.df = df
        self.features = features
        self.target = target
        self.feature_names = [x.name for x in self.features]
        self.target_name = self.target.name
        self.x = self.df[self.feature_names]
        self.y = self.df[self.target_name]

    @staticmethod
    def get_field_type(df: pd.DataFrame, target: str):
        model_type = MLModel.REGERSSION
        df_categorical_features = df.select_dtypes(include="object")
        if target in df_categorical_features.columns:
            model_type = MLModel.CLASSIFICATION
        return model_type

    def find_best_model(self):

        model_type = MLModelService.get_field_type(self.df, self.target.name)
        if model_type == MLModel.CLASSIFICATION:
            models_dict = classification_models
        else:
            models_dict = regression_models

        target_name = self.target_name
        x = self.x
        y = self.y

        categorical_cols = set(self.df.select_dtypes(exclude=np.number).columns)

        for col in self.features:
            if col.name in categorical_cols:
                x[col.name] = col.encoder.transform(x[col.name])
        if target_name in categorical_cols:
            y = self.target.encoder.transform(y)

        results = {}
        for model_name, model in models_dict.items():
            estimator = model()
            scores = cross_val_score(estimator, x, y)
            score = scores.mean()
            results[model_name] = score

        return max(results, key=results.get), max(results.values())

    def generate_model(
        self,
        model_name,
    ):
        all_models = {**classification_models, **regression_models}
        model = all_models[model_name]()
        model.fit(self.x, self.y)
        if model_name in ["DTR", "DTC", "RFC"]:
            feature_importance = model.feature_importances_
        else:
            feature_importance = model.coef_

        return model, feature_importance
