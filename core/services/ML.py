from time import sleep
from huey.contrib.djhuey import db_task
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import LinearSVC

# from sklearn.mode
# from core.models import MLModel
# TODO: Maybe try PyCaret
classification_models = {
    "LR": LogisticRegression,
}


@db_task()
def get_best_model(model):
    df = model.dataset.df
    features = [col.name for col in model.features.all()]
    target = model.target
    X = df[features]
    Y = df[target]

    sleep(10)
    print("ASDF")
