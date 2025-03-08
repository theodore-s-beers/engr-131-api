from typing import Any

total_points: float = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 2.0]

solutions: dict[str, Any] = {
    "q1-1-train-test-split": '`sklearn.model_selection`',
    "q1-2-standard-scaler": '`StandardScaler`',
    "q1-3-one-hot-encoder": '`OneHotEncoder`',
    "q1-4-linear-regression": '`sklearn.linear_model`',
    "q1-5-random-forest": 'Bagging',
    "q1-6-svc-default-kernel": 'RBF',
    "q1-7-model-evaluation": '`confusion_matrix`',
    "q1-8-pipeline-usage": 'To chain multiple transformers and estimators.',
    "q1-1-scikit-learn-import": 'False',
    "q1-2-train-test-split": 'True',
    "q1-3-standard-scaler": 'True',
    "q1-4-feature-selection": 'True',
    "q1-5-knn-classifier": 'True',
    "q1-6-random-forest": 'True',
    "q1-7-svc-kernel": 'False',
    "q1-8-cross-validation": 'True',
    "q1-9-pipeline": 'True',
    "q2-1-supervised-learning": ['`LinearRegression`', '`KNeighborsClassifier`', '`RandomForestClassifier`'],
    "q2-2-feature-scaling": ['`MinMaxScaler`', '`StandardScaler`', '`Normalizer`'],
    "q2-3-model-selection": ['`sklearn.model_selection`', '`sklearn.metrics`'],
    "q2-4-dimensionality-reduction": ['`PCA`', '`TruncatedSVD`', '`LinearDiscriminantAnalysis`'],
}
