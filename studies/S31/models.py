"""Exposure-weighted frequency, event-weighted severity and direct pure premium."""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import GammaRegressor, PoissonRegressor, TweedieRegressor
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, SplineTransformer, StandardScaler

NUMERIC = ['DrivAge', 'VehAge', 'log_bonus', 'log_density']
CATEGORICAL = ['Area', 'VehPower', 'VehBrand', 'VehGas', 'Region']


def features(frame, geography=True):
    result = frame[['DrivAge', 'VehAge']].astype(float).copy()
    result['log_bonus'] = np.log(frame.BonusMalus.to_numpy(float))
    result['log_density'] = np.log1p(frame.Density.to_numpy(float))
    for col in CATEGORICAL if geography else CATEGORICAL[:-1]:
        result[col] = frame[col].astype(str)
    result.columns = [str(name) for name in result.columns]
    return result


def transformer(boosting=False, geography=True):
    cats = CATEGORICAL if geography else CATEGORICAL[:-1]
    if boosting:
        return ColumnTransformer([('numeric', 'passthrough', NUMERIC), ('categories', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=np.nan), cats)], sparse_threshold=0)
    return ColumnTransformer([
        ('age_splines', SplineTransformer(n_knots=5, degree=3, knots='quantile', extrapolation='linear', include_bias=False), ['DrivAge', 'VehAge']),
        ('scaled', StandardScaler(), ['log_bonus', 'log_density']),
        ('categories', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cats),
    ], sparse_threshold=0)


class PremiumModel:
    def __init__(self, family, setting=None, geography=True):
        self.family, self.setting, self.geography = family, setting, geography

    def fit(self, frame, loss_column='Loss'):
        exposure = frame.Exposure.to_numpy(float)
        counts = frame.ClaimNb.to_numpy(float)
        loss = frame[loss_column].to_numpy(float)
        self.frequency_mean = counts.sum() / exposure.sum()
        self.severity_mean = loss.sum() / counts.sum()
        if self.family == 'constant':
            return self
        self.pre = transformer(self.family == 'boosting', self.geography)
        x = self.pre.fit_transform(features(frame, self.geography))
        if self.family == 'tweedie':
            self.direct = TweedieRegressor(power=1.5, alpha=self.setting, link='log', solver='newton-cholesky', max_iter=300, tol=1e-7).fit(x, loss / exposure, sample_weight=exposure)
            return self
        positive = counts > 0
        if self.family == 'glm':
            self.frequency = PoissonRegressor(alpha=self.setting, solver='newton-cholesky', max_iter=300, tol=1e-7)
            self.severity = GammaRegressor(alpha=self.setting, solver='newton-cholesky', max_iter=300, tol=1e-7)
        elif self.family == 'boosting':
            cats = [False] * 4 + [True] * (5 if self.geography else 4)
            common = dict(max_iter=150, learning_rate=.05, l2_regularization=1, max_leaf_nodes=self.setting, early_stopping=False, categorical_features=cats, random_state=310927)
            self.frequency = HistGradientBoostingRegressor(loss='poisson', min_samples_leaf=200, **common)
            self.severity = HistGradientBoostingRegressor(loss='gamma', min_samples_leaf=50, **common)
        else:
            raise ValueError('Unknown model family')
        self.frequency.fit(x, counts / exposure, sample_weight=exposure)
        self.severity.fit(x[positive], loss[positive] / counts[positive], sample_weight=counts[positive])
        return self

    def predict(self, frame):
        if self.family == 'constant':
            f, s = np.full(len(frame), self.frequency_mean), np.full(len(frame), self.severity_mean)
        else:
            x = self.pre.transform(features(frame, self.geography))
            if self.family == 'tweedie':
                p = self.direct.predict(x)
                if not np.isfinite(p).all() or (p <= 0).any():
                    raise ValueError('Invalid pure premium prediction')
                return {'premium': p}
            f, s = self.frequency.predict(x), self.severity.predict(x)
        if not np.isfinite(f * s).all() or (f <= 0).any() or (s <= 0).any():
            raise ValueError('Invalid frequency/severity prediction')
        return {'frequency': f, 'severity': s, 'premium': f * s}


def deviance_rows(y, prediction):
    if (y < 0).any() or (prediction <= 0).any():
        raise ValueError('Invalid Tweedie domain')
    return 4 * (y / np.sqrt(prediction) + np.sqrt(prediction) - 2 * np.sqrt(y))


def measures(exposure, loss, prediction):
    y, p = loss / exposure, prediction['premium']
    return {'tweedie_deviance': np.average(deviance_rows(y, p), weights=exposure),
            'absolute_error': np.sum(np.abs(loss - p * exposure)) / exposure.sum(),
            'predicted_observed_loss_ratio': np.sum(p * exposure) / loss.sum()}


def expense_premium(pure_premium, loading):
    if not 0 <= loading <= .5 or pure_premium < 0:
        raise ValueError('Scenario outside supported range')
    return pure_premium / (1 - loading)


def segment_masks(frame, minimum=500):
    yield 'portfolio', 'All policies', np.ones(len(frame), dtype=bool)
    for name in ['Region', 'Area']:
        values = frame[name].astype(str).to_numpy()
        for group in sorted(np.unique(values)):
            mask = values == group
            if mask.sum() >= minimum:
                yield name, str(group), mask
    ages = frame.DrivAge.to_numpy(float)
    for group, mask in [('Under 25', ages < 25), ('25–39', (ages >= 25) & (ages < 40)), ('40–59', (ages >= 40) & (ages < 60)), ('60+', ages >= 60)]:
        if mask.sum() >= minimum:
            yield 'driver_age', group, mask
