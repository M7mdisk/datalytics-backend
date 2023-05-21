import numpy as np
import pandas as pd
from core.models import MLModel, Column
from sklearn.linear_model import (
    LogisticRegression,
    LinearRegression,
    BayesianRidge,
    Lasso,
    ElasticNet,
)
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.svm import SVR, LinearSVC
from sklearn.model_selection import GridSearchCV
from sklearn.base import BaseEstimator
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, OrdinalEncoder
from category_encoders import TargetEncoder
from sklearn.compose import TransformedTargetRegressor
from collections import namedtuple

from sklearn import set_config

set_config(transform_output="pandas")

BestModel = namedtuple(
    "Model", ["model_name", "score", "estimator", "feature_importance"]
)

regression_models = {
    "LINREG": LinearRegression,
    "BR": BayesianRidge,
    "LSO": Lasso,
    "EN": ElasticNet,
    "SVR": SVR,  # Support Vector Regression
    "DTR": DecisionTreeRegressor,
    "GBR": GradientBoostingRegressor,
}

classification_models = {
    "LOGREG": LogisticRegression,
    # "SVC": LinearSVC,  # Support Vector classifier
    "DTC": DecisionTreeClassifier,
    "RFC": RandomForestClassifier,
    "GBC": GradientBoostingClassifier,
}

all_models = {**classification_models, **regression_models}


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

    def make_best_model(self):
        model_type = MLModelService.get_field_type(self.df, self.target.name)
        if model_type == MLModel.CLASSIFICATION:
            models_dict = classification_models
        else:
            models_dict = regression_models

        target_name = self.target_name
        x = self.x
        y = self.y

        categorical_cols = list(self.x.select_dtypes(exclude=np.number).columns)
        numerical_cols = list(self.x.select_dtypes(include=np.number).columns)

        ONEHOT_THRESHHOLD = 4

        target_encoding_cols = [
            col for col in categorical_cols if x[col].nunique() > ONEHOT_THRESHHOLD
        ]
        onehot_encoding_cols = [
            col for col in categorical_cols if x[col].nunique() <= ONEHOT_THRESHHOLD
        ]

        # if model_type == MLModel.CLASSIFICATION:
        #     y = self.target.encoder.transform(y)

        # TODO: Try target encoder
        onehot_transformer = OneHotEncoder(handle_unknown="ignore", drop="if_binary")

        target_transformer = TargetEncoder()

        numerical_transformer = StandardScaler()

        # TODO: DO NOT USE ONEHOT FOR EVERYTHING, SUCKS FOR HIGH CARDINALITY
        preprocessor = ColumnTransformer(
            transformers=[
                ("onehot", onehot_transformer, categorical_cols),
                # ("target", OrdinalEncoder(), target_encoding_cols),
                ("numerical", numerical_transformer, numerical_cols),
            ],
            verbose_feature_names_out=False,
        )

        results: dict[str, tuple[float, BaseEstimator]] = {}
        for model_name, model in models_dict.items():
            try:
                print(model_name)
                if model_name == "SVC":
                    model = model()
                elif model_name == "SVR":
                    model = model(kernel="linear")
                else:
                    model = model()

                # TODO: Gridsearch adding polynomial terms
                steps = [("preprocessor", preprocessor), ("model", model)]

                estimator = Pipeline(steps)
                scores = cross_val_score(estimator, x, y)
                print(model_name, scores, scores.mean(), "done")
                score = scores.mean()
                results[model_name] = (score, estimator)
            except:
                pass

        best_model_name = max(results, key=lambda x: results.get(x)[0])
        best_estimator_score, best_estimator = results.get(best_model_name)

        best_estimator.fit(x, y)

        encoded_feature_names: list[str] = best_estimator.named_steps[
            "preprocessor"
        ].get_feature_names_out()
        feature_importance = self.get_feature_importance(
            best_model_name, best_estimator.named_steps["model"]
        )
        assert len(encoded_feature_names) == len(feature_importance)

        importances = {}
        for feature in x.columns:
            importances[feature] = 0
            for i, col in enumerate(encoded_feature_names):
                if col.startswith(feature):
                    importances[feature] += abs(feature_importance[i])

        return BestModel(
            best_model_name, best_estimator_score, best_estimator, importances
        )

    @staticmethod
    def get_feature_importance(model_name, model):
        if hasattr(model,"coef_"):
            if len(model.coef_) == 1:
                return model.coef_[0]
            return model.coef_
        if model_name == 'LSO':
            return model.coef_
        if model_name in ["DTR", "DTC", "RFC", "GBC", "GBR"]:
            return model.feature_importances_
        else:
            return model.coef_[0]

    def get_batch_predictions(self, x: pd.DataFrame, sklearn_model: BaseEstimator):
        model_type = MLModelService.get_field_type(self.df, self.target.name)
        if model_type == MLModel.CLASSIFICATION:
            return sklearn_model.predict_proba(x)
        else:
            return sklearn_model.predict(x)


import random


def calc_percentage(mx):
    return min(mx, mx - (random.randrange(0, 13) / 100))


def normalize_accuracy(x):
    return x


from sklearn.base import TransformerMixin, BaseEstimator


class Debug(BaseEstimator, TransformerMixin):
    def transform(self, X):
        print(X)
        print(X.shape)
        return X

    def fit(self, X, y=None, **fit_params):
        return self
