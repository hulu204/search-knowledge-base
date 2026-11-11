---
title: 'https://eugeneyan.com//writing/testing-ml/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/testing-ml/
account: 
origin: en-rss
---
# [eugeneyan](/)

* [Start Here](/start-here/ "Start Here")
* [Writing](/writing/ "Writing")
* [Speaking](/speaking/ "Speaking")
* [Prototyping](/prototyping/ "Prototyping")
* [About](/about/ "About")
* [![](/assets/icon-search.svg)](/search/ "Search")

# How to Test Machine Learning Code and Systems

[
[machinelearning](/tag/machinelearning/)
[engineering](/tag/engineering/)
[python](/tag/python/)
]
 · 14 min read

Two weeks ago, [Jeremy](https://twitter.com/jeremyjordan) wrote a great post on [Effective Testing for Machine Learning Systems](https://www.jeremyjordan.me/testing-ml/). He distinguished between traditional software tests and machine learning (ML) tests; software tests check the **written logic** while ML tests check the **learned logic**.

ML tests can be further split into **testing** and **evaluation**. We’re familiar with ML **evaluation** where we train a model and evaluate its performance on an unseen validation set; this is done via metrics (e.g., accuracy, [Area under Curve of Receiver Operating Characteristic (AUC ROC)](https://en.wikipedia.org/wiki/Receiver_operating_characteristic#Area_under_the_curve)) and visuals (e.g., [precision-recall curve](/writing/recommender-systems-baseline-pytorch/#implementation-2-matrix-factorization-with-bias)).

On the other hand, ML **testing** involves checks on model behaviour. **Pre-train tests**—which can be run without trained parameters—check if our *written logic* is correct. For example, is classification probability between 0 to 1? **Post-train tests** check if the *learned logic* is expected. For example, on the [Titanic dataset](https://www.kaggle.com/c/titanic/data), we should expect females to have a higher survival probability (relative to males).

![Workflow for testing machine learning](/assets/testing-ml-flow.webp "Workflow for testing machine learning")

Workflow for testing machine learning ([source](https://www.jeremyjordan.me/testing-ml/))

Taken together, here’s how the workflow might look like. To complement this, we’ll implement a machine learning model and run the following tests on it:

* [Pre-train tests to ensure correct implementation](#pre-train-tests-to-ensure-correct-implementation)
* [Post-train tests to ensure expected learned behaviour](#post-train-tests-to-ensure-expected-learned-behaviour)
* [Evaluation to ensure satisfactory model performance](#model-evaluation-to-ensure-satisfactory-performance)

> Follow along with the code in this Github repository: [`testing-ml`](https://github.com/eugeneyan/testing-ml)

## Setting up the context (algorithm and data)

Before we can do ML testing, we’ll need an **algorithm and some data**. Our algorithm will be a [`numpy`](https://numpy.org) implementation of [`DecisionTree`](https://github.com/eugeneyan/testing-ml/blob/master/src/tree/decision_tree.py) which predicts a probability for binary classification. ([Extensions to make it support regression welcome!](#try-it-for-yourself-and-break-something)).

To run our tests, we’ll use the [Titanic dataset](https://www.kaggle.com/c/titanic/data). This tiny data set (~900 rows, 10 features) makes for fast testing (when model training is involved) and allows us to iterate quickly. (As part of performance evaluation, we run `fit()` and `predict()` hundreds of times to get the 99th percentile timing.) The simplicity and familiarity of the data also makes it easier to discuss the post-train (i.e., learned logic) tests.

```
+ ------------+----------+--------+-----------------------------------------+--------+-----+-------+-------+-----------+---------+-------+----------+
| PassengerId | Survived | Pclass | Name                                    | Sex    | Age | SibSp | Parch | Ticket    |    Fare | Cabin | Embarked |
+ ------------+----------+--------+-----------------------------------------+--------+-----+-------+-------+-----------+---------+-------+----------|
|           1 |        0 |      3 | Braund, Mr. Owen Harris                 | male   |  22 |     1 |     0 | A/5 21171 |    7.25 | nan   | S        |
|           2 |        1 |      1 | Cumings, Mrs. John Bradley (Florence... | female |  38 |     1 |     0 | PC 17599  | 71.2833 | C85   | C        |
|           3 |        1 |      3 | Heikkinen, Miss. Laina                  | female |  26 |     0 |     0 | STON/O2.  |   7.925 | nan   | S        |
|           4 |        1 |      1 | Futrelle, Mrs. Jacques Heath (Lily M... | female |  35 |     1 |     0 | 113803    |    53.1 | C123  | S        |
|           5 |        0 |      3 | Allen, Mr. William Henry                | male   |  35 |     0 |     0 | 373450    |    8.05 | nan   | S        |
|           6 |        0 |      3 | Moran, Mr. James                        | male   | nan |     0 |     0 | 330877    |  8.4583 | nan   | Q        |
|           7 |        0 |      1 | McCarthy, Mr. Timothy J                 | male   |  54 |     0 |     0 | 17463     | 51.8625 | E46   | S        |
|           8 |        0 |      3 | Palsson, Master. Gosta Leonard          | male   |   2 |     3 |     1 | 349909    |  21.075 | nan   | S        |
|           9 |        1 |      3 | Johnson, Mrs. Oscar W (Elisabeth Vil... | female |  27 |     0 |     2 | 347742    | 11.1333 | nan   | S        |
|          10 |        1 |      2 | Nasser, Mrs. Nicholas (Adele Achem)     | female |  14 |     1 |     0 | 237736    | 30.0708 | nan   | C        |
+ ------------+----------+--------+-----------------------------------------+--------+-----+-------+-------+-----------+---------+-------+----------+
```

If you're unfamiliar with the Titanic dataset, here's how it looks like (scroll to the right).

## Adopting testing habits from software engineering

We’ll adopt some good habits from software engineering. We won’t go through them in detail here though it was previously covered in another [post](/writing/setting-up-python-project-for-automation-and-collaboration/):

* [Unit test](/writing/setting-up-python-project-for-automation-and-collaboration/#write-some-unit-tests-theyre-our-safety-harness) fixture reuse, exceptions testing, etc with [`pytest`](https://docs.pytest.org/en/latest/)
* [Code coverage](/writing/setting-up-python-project-for-automation-and-collaboration/#check-for-coverage-how-extensive-are-our-tests) with [`Coverage.py`](https://coverage.readthedocs.io/en/coverage-5.2.1/) and [`pytest-cov`](https://pytest-cov.readthedocs.io/en/latest/)
* [Linting](/writing/setting-up-python-project-for-automation-and-collaboration/#lint-to-ensure-consistency-across-projects) to ensure code consistency with [`pylint`](https://www.pylint.org)
* [Type checking](/writing/setting-up-python-project-for-automation-and-collaboration/#check-for-type-errors-to-prevent-them) to verify type correctness with [`mypy`](http://mypy-lang.org)

(Note: The tests below won’t include type hints though the [implementation code](https://github.com/eugeneyan/testing-ml/blob/master/src/tree/decision_tree.py#L16) does.)

## Pre-train tests to ensure correct implementation

In pre-train tests, we want to **catch errors in our implementation** (i.e., written logic) before training an erroneous model. We can run these tests without a fully trained model.

First, we’ll test our functions of [Gini impurity](https://en.wikipedia.org/wiki/Decision_tree_learning#Gini_impurity) and [Gini gain](https://en.wikipedia.org/wiki/Decision_tree_learning#Information_gain). These will be used to [split the data](https://en.wikipedia.org/wiki/Decision_tree_learning#General) and grow our decision tree.

```
def test_gini_impurity():
    assert round(gini_impurity([1, 1, 1, 1, 1, 1, 1, 1]), 3) == 0
    assert round(gini_impurity([1, 1, 1, 1, 1, 1, 1, 0]), 3) == 0.219
    assert round(gini_impurity([1, 1, 1, 1, 1, 1, 0, 0]), 3) == 0.375
    assert round(gini_impurity([1, 1, 1, 1, 1, 0, 0, 0]), 3) == 0.469
    assert round(gini_impurity([1, 1, 1, 1, 0, 0, 0, 0]), 3) == 0.500

def test_gini_gain():
    assert round(gini_gain([1, 1, 1, 1, 0, 0, 0, 0], [[1, 1, 1, 1], [0, 0, 0, 0]]), 3) == 0.5
    assert round(gini_gain([1, 1, 1, 1, 0, 0, 0, 0], [[1, 1, 1, 0], [0, 0, 0, 1]]), 3) == 0.125
    assert round(gini_gain([1, 1, 1, 1, 0, 0, 0, 0], [[1, 0, 0, 0], [0, 1, 1, 1]]), 3) == 0.125
    assert round(gini_gain([1, 1, 1, 1, 0, 0, 0, 0], [[1, 1, 0, 0], [0, 0, 1, 1]]), 3) == 0.0
```

Next, we’ll check if the model prediction shape is expected. We should have the same number of rows as the input features.

```
def test_dt_output_shape(dummy_titanic):
    X_train, y_train, X_test, y_test = dummy_titanic
    dt = DecisionTree()
    dt.fit(X_train, y_train)
    pred_train = dt.predict(X_train)
    pred_test = dt.predict(X_test)

    assert pred_train.shape == (X_train.shape[0],), 'DecisionTree output should be same as training labels.'
    assert pred_test.shape == (X_test.shape[0],), 'DecisionTree output should be same as testing labels.'
```

We’ll also want to check the output ranges. Given that we’re predicting probabilities, we should expect the output to range from 0 to 1 inclusive.

```
def test_dt_output_range(dummy_titanic):
    X_train, y_train, X_test, y_test = dummy_titanic
    dt = DecisionTree()
    dt.fit(X_train, y_train)
    pred_train = dt.predict(X_train)
    pred_test = dt.predict(X_test)

    assert (pred_train <= 1).all() & (pred_train >= 0).all(), 'Decision tree output should range from 0 to 1 inclusive'
    assert (pred_test <= 1).all() & (pred_test >= 0).all(), 'Decision tree output should range from 0 to 1 inclusive'
```

Here, we’ll check for test set leakage (i.e., duplicate rows in train/test splits) by concatenating train and test data, dropping duplicates, and checking the number of rows. (Note: Other leakages include [temporal leaks](https://www.fast.ai/2017/11/13/validation-sets/#time-series) and [feature leaks](https://en.wikipedia.org/wiki/Leakage_(machine_learning)#Feature_leakage); we won’t cover them here.)

```
def test_data_leak_in_test_data(dummy_titanic_df):
    train, test = dummy_titanic_df

    concat_df = pd.concat([train, test])
    concat_df.drop_duplicates(inplace=True)

    assert concat_df.shape[0] == train.shape[0] + test.shape[0]
```

Given perfectly separable data and unlimited depth, our decision tree should be able to “memorise” the training data and *[overfit](https://en.wikipedia.org/wiki/Overfitting) completely*. In other words, if we train *and* evaluate on the training data, we should get 100% accuracy. (Note: the Titanic data isn’t perfectly separable so we’ll create a small data sample for this.)

```
@pytest.fixture
def dummy_feats_and_labels():
    feats = np.array([[0.7057, -5.4981, 8.3368, -2.8715],
                      [2.4391, 6.4417, -0.80743, -0.69139],
                      [-0.2062, 9.2207, -3.7044, -6.8103],
                      [4.2586, 11.2962, -4.0943, -4.3457],
                      [-2.343, 12.9516, 3.3285, -5.9426],
                      [-2.0545, -10.8679, 9.4926, -1.4116],
                      [2.2279, 4.0951, -4.8037, -2.1112],
                      [-6.1632, 8.7096, -0.21621, -3.6345],
                      [0.52374, 3.644, -4.0746, -1.9909],
                      [1.5077, 1.9596, -3.0584, -0.12243]
                      ])
    labels = np.array([1, 1, 1, 1, 1, 0, 0, 0, 0, 0])
    return feats, labels

def test_dt_overfit(dummy_feats_and_labels):
    feats, labels = dummy_feats_and_labels
    dt = DecisionTree()
    dt.fit(feats, labels)
    pred = np.round(dt.predict(feats))

    assert np.array_equal(labels, pred), 'DecisionTree should fit data perfectly and prediction should == labels.'
```

Lastly, we check if increasing tree depth leads to increased accuracy and AUC ROC on *training* data (though it’ll overfit and perform poorly on *validation* data). In the test below, we fit trees of depth one to 10 and ensure training accuracy and AUC increases consistently.

```
def test_dt_increase_acc(dummy_titanic):
    X_train, y_train, _, _ = dummy_titanic

    acc_list = []
    auc_list = []
    for depth in range(1, 10):
        dt = DecisionTree(depth_limit=depth)
        dt.fit(X_train, y_train)
        pred = dt.predict(X_train)
        pred_binary = np.round(pred)
        acc_list.append(accuracy_score(y_train, pred_binary))
        auc_list.append(roc_auc_score(y_train, pred))

    assert sorted(acc_list) == acc_list, 'Accuracy should increase as tree depth increases.'
    assert sorted(auc_list) == auc_list, 'AUC ROC should increase as tree depth increases.'
```

## Post-train tests to ensure expected learned behaviour

In post-train tests, we want to **check if the model is behaving correctly**. Thus, we test our trained models for their **learned logic**. I’m unaware of any frameworks for doing this so here’s my take on it (suggestions welcome!). I took inspiration from the excellent paper [Beyond Accuracy: Behavioral Testing of NLP Models with CheckList](https://arxiv.org/abs/2005.04118).

First, we check for **invariance**. Keeping everything constant and tweaking one feature at a time, how would model predictions change? We should not expect survival probability to change due to the passenger’s name, ticket number, or port of embarkation.

```
@pytest.fixture
def dummy_passengers():
    # Based on passenger 2 (high passenger class female)
    passenger2 = {'PassengerId': 2,
                  'Pclass': 1,
                  'Name': ' Mrs. John',
                  'Sex': 'female',
                  'Age': 38.0,
                  'SibSp': 1,
                  'Parch': 0,
                  'Ticket': 'PC 17599',
                  'Fare': 71.2833,
                  'Embarked': 'C'}

    return passenger2

def test_dt_invariance(dummy_titanic_dt, dummy_passengers):
    model = dummy_titanic_dt
    _, p2 = dummy_passengers

    # Get original survival probability of passenger 2
    test_df = pd.DataFrame.from_dict([p2], orient='columns')
    X, y = get_feats_and_labels(prep_df(test_df))
    p2_prob = model.predict(X)[0]  # 1.0

    # Change name from John to Berns (without changing gender or title)
    p2_name = p2.copy()
    p2_name['Name'] = ' Mrs. Berns'
    test_df = pd.DataFrame.from_dict([p2_name], orient='columns')
    X, y = get_feats_and_labels(prep_df(test_df))
    p2_name_prob = model.predict(X)[0]  # 1.0 

    # Change ticket number from 'PC 17599' to 'A/5 21171'
    p2_ticket = p2.copy()
    p2_ticket['ticket'] = 'A/5 21171'
    test_df = pd.DataFrame.from_dict([p2_ticket], orient='columns')
    X, y = get_feats_and_labels(prep_df(test_df))
    p2_ticket_prob = model.predict(X)[0]  # 1.0

    assert p2_prob == p2_name_prob == p2_ticket_prob
```

On the other hand, we have **directional expectations** such as:

* Females having higher survival probability (than males)
* Higher passenger class having higher survival probability (than lower classes)
* Higher fare having higher survival probability (than lower fare)

```
def test_dt_directional_expectation(dummy_titanic_dt, dummy_passengers):
    model = dummy_titanic_dt
    _, p2 = dummy_passengers

    # Get original survival probability of passenger 2
    test_df = pd.DataFrame.from_dict([p2], orient='columns')
    X, y = get_feats_and_labels(prep_df(test_df))
    p2_prob = model.predict(X)[0]  # 1.0

    # Change gender from female to male
    p2_male = p2.copy()
    p2_male['Name'] = ' Mr. John'
    p2_male['Sex'] = 'male'
    test_df = pd.DataFrame.from_dict([p2_male], orient='columns')
    X, y = get_feats_and_labels(prep_df(test_df))
    p2_male_prob = model.predict(X)[0]  # 0.56

    # Change class from 1 to 3
    p2_class = p2.copy()
    p2_class['Pclass'] = 3
    test_df = pd.DataFrame.from_dict([p2_class], orient='columns')
    X, y = get_feats_and_labels(prep_df(test_df))
    p2_class_prob = model.predict(X)[0]  # 0.0

    # Lower fare from 71.2833 to 5
    p2_fare = p2.copy()
    p2_fare['Fare'] = 5
    test_df = pd.DataFrame.from_dict([p2_fare], orient='columns')
    X, y = get_feats_and_labels(prep_df(test_df))
    p2_fare_prob = model.predict(X)[0]  # 0.85

    assert p2_prob > p2_male_prob, 'Changing gender from female to male should decrease survival probability.'
    assert p2_prob > p2_class_prob, 'Changing class from 1 to 3 should decrease survival probability.'
    assert p2_prob > p2_fare_prob, 'Changing fare from 72 to 5 should decrease survival probability.'
```

## Model evaluation to ensure satisfactory performance

Last, we **evaluate** our model to ensure performance does not degrade, whether due to new data or updated implementation. Here, we assess model performance on *accuracy* and *AUC*.

```
def test_dt_evaluation(dummy_titanic_dt, dummy_titanic):
    model = dummy_titanic_dt
    X_train, y_train, X_test, y_test = dummy_titanic
    pred_test = model.predict(X_test)
    pred_test_binary = np.round(pred_test)
    acc_test = accuracy_score(y_test, pred_test_binary)
    auc_test = roc_auc_score(y_test, pred_test)

    assert acc_test > 0.82, 'Accuracy on test should be > 0.82'
    assert auc_test > 0.84, 'AUC ROC on test should be > 0.84'
```

As part of evaluation, we’ll also assess *training and inference times*. We should not expect algorithm updates to change these times greatly. Consumers of our predictions might have strict latency requirements. Here, we call `fit()` and `predict()` multiple times and check the 99th percentile.

```
def test_dt_training_time(dummy_titanic):
    X_train, y_train, X_test, y_test = dummy_titanic

    # Standardize to use depth = 10
    dt = DecisionTree(depth_limit=10)
    latency_array = np.array([train_with_time(dt, X_train, y_train)[1] for i in range(100)])
    time_p95 = np.quantile(latency_array, 0.95)
    assert time_p95 < 1.0, 'Training time at 95th percentile should be < 1.0 sec'

def test_dt_serving_latency(dummy_titanic):
    X_train, y_train, X_test, y_test = dummy_titanic

    # Standardize to use depth = 10
    dt = DecisionTree(depth_limit=10)
    dt.fit(X_train, y_train)

    latency_array = np.array([predict_with_time(dt, X_test)[1] for i in range(500)])
    latency_p99 = np.quantile(latency_array, 0.99)
    assert latency_p99 < 0.004, 'Serving latency at 99th percentile should be < 0.004 sec'
```

Model testing vs. evaluation; similar to white box vs black box?

As I write this, I’m seeing parallels with white box and black box testing. Here’s a brief comparison.

* White box testing: We test the **logic** of an application with **full knowledge of the internals** (i.e., structure, implementation).
* Black box testing: We test the **outcomes and behaviour** of an application **without knowledge** about internal code and implementation.

Here, our pre-train tests are similar to white box testing. We have tests cases to check our written logic and implementation (e.g., Gini gain, output shape/range, etc.). On the other hand, our post-train tests and model evaluation are akin to black box tests. We **check the model’s learned behaviour** and **evaluate performance**.

Here’s an [excellent comparison of white box vs black box testing](https://www.geeksforgeeks.org/differences-between-black-box-testing-vs-white-box-testing/).

## Testing `RandomForest`—does it improve accuracy/AUC?

Next, we want to improve on `DecisionTree` by adding bagging and making it a [`RandomForest`](https://github.com/eugeneyan/testing-ml/blob/master/src/tree/random_forest.py). We can do this by inheriting from `DecisionTree` and overriding the `fit()` and `predict()` methods.

For pre-train tests, we should make sure that additional trees improve accuracy and AUC. In the example below, we train `RandomForest` models with 1, 3, 7, and 15 bagged trees and check if accuracy and AUC increases.

```
def test_dt_increase_acc(dummy_titanic):
    X_train, y_train, X_test, y_test = dummy_titanic

    acc_list = []
    auc_list = []
    for num_trees in [1, 3, 7, 15]:
        rf = RandomForest(num_trees=num_trees, depth_limit=7, col_subsampling=0.7, row_subsampling=0.7)
        rf.fit(X_train, y_train)
        pred = rf.predict(X_test)
        pred_binary = np.round(pred)
        acc_list.append(accuracy_score(y_test, pred_binary))
        auc_list.append(roc_auc_score(y_test, pred))

    assert sorted(acc_list) == acc_list, 'Accuracy should increase as number of trees increases.'
    assert sorted(auc_list) == auc_list, 'AUC ROC should increase as number of trees increases.'
```

We’ll also want to check that, given the same tree depth, `RandomForest` outperforms `DecisionTree` on a validation data set.

```
def test_rf_better_than_dt(dummy_titanic):
    X_train, y_train, X_test, y_test = dummy_titanic

    dt = DecisionTree(depth_limit=10)
    dt.fit(X_train, y_train)

    rf = RandomForest(depth_limit=10, num_trees=7, col_subsampling=0.8, row_subsampling=0.8)
    rf.fit(X_train, y_train)

    pred_test_dt = dt.predict(X_test)
    pred_test_binary_dt = np.round(pred_test_dt)
    acc_test_dt = accuracy_score(y_test, pred_test_binary_dt)
    auc_test_dt = roc_auc_score(y_test, pred_test_dt)

    pred_test_rf = rf.predict(X_test)
    pred_test_binary_rf = np.round(pred_test_rf)
    acc_test_rf = accuracy_score(y_test, pred_test_binary_rf)
    auc_test_rf = roc_auc_score(y_test, pred_test_rf)

    assert acc_test_rf > acc_test_dt, 'RandomForest should have higher accuracy than DecisionTree on test set.'
    assert auc_test_rf > auc_test_dt, 'RandomForest should have higher AUC ROC than DecisionTree on test set.'
```

Similar to `DecisionTree`, we run [invariance](https://github.com/eugeneyan/testing-ml/blob/master/tests/tree/test_random_forest_2post.py#L8) and [directional expectation](https://github.com/eugeneyan/testing-ml/blob/master/tests/tree/test_random_forest_2post.py#L69) tests. We also do model evaluation on [accuracy and AUC](https://github.com/eugeneyan/testing-ml/blob/master/tests/tree/test_random_forest_3eval.py#L10), [training time](https://github.com/eugeneyan/testing-ml/blob/master/tests/tree/test_random_forest_3eval.py#L31), and [inference time](https://github.com/eugeneyan/testing-ml/blob/master/tests/tree/test_random_forest_3eval.py#L41). (Note: Given a `RandomForest` of five trees, we should expect our training and inference time to be ~5x of `DecisionTree` as training and inference is not parallelized.)

## Try it for yourself and break something

Alright enough reading; I urge you to clone the [GitHub repository](https://github.com/eugeneyan/testing-ml) and try it for yourself. It’s as simple as:

```
# Clone and setup environment
git clone https://github.com/eugeneyan/testing-ml.git
cd testing-ml
make setup

# Run test suite
make check
```

Mess around with the implementation and tests. Break something! If you’re feeling adventurous, update `DecisionTree` to also do regression. You’ll need to:

* Add an `__init__()` argument for `classification` or `regression`. Alternatively, create it a new `DecisionTree` class (via inheritance perhaps?) solely for regression.
* Add a function to check for [RMSE](https://en.wikipedia.org/wiki/Root-mean-square_deviation) or [MSE](https://en.wikipedia.org/wiki/Mean_squared_error) improvement (instead of [Gini gain](https://github.com/eugeneyan/testing-ml/blob/master/src/tree/decision_tree.py#L71)).
* Add a test data set (perhaps [Boston](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_boston.html)?) and basic data prep steps.
* Add test cases and model evaluation checks.

Do you know of (i) other frameworks for **machine learning tests on learned behaviour**, or (ii) examples of **behaviour failures in machine learning applications**?

I would love to hear from you—please leave a comment below. Alternatively, here’s a [survey](https://forms.gle/gDdQPTMiQNhyiN1N9) on machine learning checks and failures.

> Previously, Jeremy shared how to test machine learning systems. He differentiated:  
> • Testing vs. Evaluation  
> • Implementation vs. learned behaviour tests  
>   
> To follow-up, here are example test cases on a NumPy version of DecisionTree & RandomForest<https://t.co/iXqyD2afJz>
>
> — Eugene Yan (@eugeneyan) [September 9, 2020](https://twitter.com/eugeneyan/status/1303500014635810816?ref_src=twsrc%5Etfw)

**Thanks** to Yang Xinyi, [Jeremy Jordan](https://twitter.com/jeremyjordan), [David Vargas](https://twitter.com/dvargas92495), and [Joel Christiansen](https://joelc.io/) for reading drafts of this.

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Sep 2020). How to Test Machine Learning Code and Systems. eugeneyan.com.
> https://eugeneyan.com/writing/testing-ml/.

or

```
@article{yan2020testing,
  title   = {How to Test Machine Learning Code and Systems},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2020},
  month   = {Sep},
  url     = {https://eugeneyan.com/writing/testing-ml/}
}
```

  
Share on: 

![](/assets/icon-twitter.svg)

![](/assets/icon-linkedin.svg)

![](/assets/bluesky.svg)

![](/assets/icon-facebook.svg)

![](/assets/icon-mail.svg)

---

  

Browse related tags: [
[machinelearning](/tag/machinelearning/)
[engineering](/tag/engineering/)
[python](/tag/python/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« Mailbag: Parsing Fields from PDFs—When to Use Machine Learning?](/writing/mailbag-pdf-fields/)
[Migrating Site Comments to Utterances »](/writing/migrating-to-utterances/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---