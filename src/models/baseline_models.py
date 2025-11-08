"""
Modelos Baseline para Predição WIN

Implementa modelos baseline simples (Regressão Linear, Random Forest)
para estabelecer baseline de performance antes de modelos mais complexos.

Autor: Sistema Especialista de Mercado Financeiro
Data: 2025
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
import logging
from typing import Dict, Tuple, Optional
from datetime import datetime

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WinBaselineModels:
    """
    Modelos baseline para predição do WIN.

    Implementa Regressão Linear e Random Forest como baselines
    para comparação com modelos mais avançados.
    """

    def __init__(self, random_state: int = 42):
        """Inicializa os modelos baseline."""
        self.random_state = random_state
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.is_trained = False

    def train_baseline_models(self, X: pd.DataFrame, y: pd.Series,
                            test_size: float = 0.2) -> Dict[str, dict]:
        """
        Treina modelos baseline e retorna métricas de performance.

        Args:
            X: Features
            y: Target (preço de fechamento)
            test_size: Proporção dos dados para teste

        Returns:
            Dicionário com métricas de cada modelo
        """
        logger.info("Treinando modelos baseline...")

        # Salvar nomes das features
        self.feature_columns = X.columns.tolist()

        # Divisão temporal (mais apropriada para séries temporais)
        split_idx = int(len(X) * (1 - test_size))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        logger.info(f"Treino: {len(X_train)} amostras, Teste: {len(X_test)} amostras")

        # Escalar features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        results = {}

        # Modelo 1: Regressão Linear
        lr_model = self._train_linear_regression(X_train_scaled, y_train)
        lr_metrics = self._evaluate_model(lr_model, X_test_scaled, y_test, "Linear Regression")
        results['linear_regression'] = {
            'model': lr_model,
            'metrics': lr_metrics,
            'predictions': lr_model.predict(X_test_scaled)
        }

        # Modelo 2: Random Forest
        rf_model = self._train_random_forest(X_train_scaled, y_train)
        rf_metrics = self._evaluate_model(rf_model, X_test_scaled, y_test, "Random Forest")
        results['random_forest'] = {
            'model': rf_model,
            'metrics': rf_metrics,
            'predictions': rf_model.predict(X_test_scaled)
        }

        # Modelo 3: XGBoost
        try:
            xgb_model = self._train_xgboost(X_train_scaled, y_train, X_test_scaled, y_test)
            xgb_metrics = self._evaluate_model(xgb_model, X_test_scaled, y_test, "XGBoost")
            results['xgboost'] = {
                'model': xgb_model,
                'metrics': xgb_metrics,
                'predictions': xgb_model.predict(X_test_scaled)
            }
        except ImportError:
            logger.warning("XGBoost não disponível, pulando treinamento")
        except Exception as e:
            logger.error(f"Erro no treinamento XGBoost: {e}")

        self.models = results
        self.is_trained = True

        logger.info("Modelos baseline treinados com sucesso")
        return results

    def _train_linear_regression(self, X_train: np.ndarray, y_train: pd.Series):
        """Treina modelo de Regressão Linear."""
        logger.info("Treinando Regressão Linear...")

        model = LinearRegression()
        model.fit(X_train, y_train)

        return model

    def _train_random_forest(self, X_train: np.ndarray, y_train: pd.Series):
        """Treina modelo Random Forest."""
        logger.info("Treinando Random Forest...")

        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=self.random_state,
            n_jobs=-1
        )
        model.fit(X_train, y_train)

        return model

    def _train_xgboost(self, X_train: np.ndarray, y_train: pd.Series,
                      X_test: np.ndarray, y_test: pd.Series):
        """Treina modelo XGBoost."""
        try:
            import xgboost as xgb
        except ImportError:
            raise ImportError("XGBoost não está instalado")

        logger.info("Treinando XGBoost...")

        model = xgb.XGBRegressor(
            objective='reg:squarederror',
            eval_metric='rmse',
            max_depth=6,
            learning_rate=0.1,
            n_estimators=500,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=self.random_state,
            early_stopping_rounds=50
        )

        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )

        return model

    def _evaluate_model(self, model, X_test: np.ndarray, y_test: pd.Series,
                       model_name: str) -> Dict[str, float]:
        """
        Avalia performance do modelo.

        Args:
            model: Modelo treinado
            X_test: Features de teste
            y_test: Target de teste
            model_name: Nome do modelo

        Returns:
            Dicionário com métricas
        """
        predictions = model.predict(X_test)

        # Métricas principais
        mae = mean_absolute_error(y_test, predictions)
        mse = mean_squared_error(y_test, predictions)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, predictions)

        # Métricas específicas para finanças
        mape = np.mean(np.abs((y_test - predictions) / y_test)) * 100

        # Directional Accuracy (acertos na direção)
        actual_direction = np.sign(np.diff(y_test.values))
        pred_direction = np.sign(np.diff(predictions))
        directional_accuracy = np.mean(actual_direction == pred_direction) * 100

        metrics = {
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'r2': r2,
            'directional_accuracy': directional_accuracy,
            'mean_actual': y_test.mean(),
            'std_actual': y_test.std(),
            'mean_predicted': predictions.mean(),
            'std_predicted': predictions.std()
        }

        logger.info(f"{model_name} - MAE: {mae:.2f}, RMSE: {rmse:.2f}, MAPE: {mape:.2f}%, R²: {r2:.4f}, DirAcc: {directional_accuracy:.2f}%")

        return metrics

    def predict(self, X: pd.DataFrame, model_name: str = 'random_forest') -> np.ndarray:
        """
        Faz predições com modelo treinado.

        Args:
            X: Features para predição
            model_name: Nome do modelo ('linear_regression' ou 'random_forest')

        Returns:
            Array com predições
        """
        if not self.is_trained:
            raise ValueError("Modelos não foram treinados ainda")

        if model_name not in self.models:
            raise ValueError(f"Modelo {model_name} não encontrado")

        # Garantir que X tem as mesmas features
        if isinstance(X, pd.DataFrame):
            X = X[self.feature_columns]

        # Escalar features
        X_scaled = self.scaler.transform(X)

        predictions = self.models[model_name]['model'].predict(X_scaled)
        return predictions

    def get_feature_importance(self, model_name: str = 'random_forest') -> pd.DataFrame:
        """
        Retorna importância das features (apenas para Random Forest).

        Args:
            model_name: Nome do modelo

        Returns:
            DataFrame com importância das features
        """
        if model_name != 'random_forest':
            logger.warning("Importância de features disponível apenas para Random Forest")
            return None

        model = self.models[model_name]['model']
        importance = model.feature_importances_

        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': importance
        }).sort_values('importance', ascending=False)

        return feature_importance

    def save_models(self, output_dir: str = "models/win_predictor_v1.0"):
        """
        Salva modelos treinados e scaler.

        Args:
            output_dir: Diretório para salvar modelos
        """
        import os
        os.makedirs(output_dir, exist_ok=True)

        # Salvar modelos
        for model_name, model_data in self.models.items():
            model_path = f"{output_dir}/{model_name}.pkl"
            joblib.dump(model_data['model'], model_path)
            logger.info(f"Modelo {model_name} salvo em {model_path}")

        # Salvar scaler
        scaler_path = f"{output_dir}/feature_scaler.pkl"
        joblib.dump(self.scaler, scaler_path)

        # Salvar metadados
        metadata = {
            'feature_columns': self.feature_columns,
            'trained_at': datetime.now().isoformat(),
            'model_metrics': {name: data['metrics'] for name, data in self.models.items()}
        }

        metadata_path = f"{output_dir}/model_metadata.json"
        import json
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)

        logger.info(f"Metadados salvos em {metadata_path}")

    def load_models(self, input_dir: str = "models/win_predictor_v1.0"):
        """
        Carrega modelos treinados e scaler.

        Args:
            input_dir: Diretório com modelos salvos
        """
        import os

        # Carregar scaler
        scaler_path = f"{input_dir}/feature_scaler.pkl"
        if os.path.exists(scaler_path):
            self.scaler = joblib.load(scaler_path)

        # Carregar metadados
        metadata_path = f"{input_dir}/model_metadata.json"
        if os.path.exists(metadata_path):
            import json
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                self.feature_columns = metadata['feature_columns']

        # Carregar modelos
        for model_name in ['linear_regression', 'random_forest']:
            model_path = f"{input_dir}/{model_name}.pkl"
            if os.path.exists(model_path):
                model = joblib.load(model_path)
                self.models[model_name] = {'model': model}

        self.is_trained = len(self.models) > 0
        logger.info(f"Modelos carregados de {input_dir}")

    def cross_validate_temporal(self, X: pd.DataFrame, y: pd.Series,
                              n_splits: int = 5) -> Dict[str, list]:
        """
        Realiza validação cruzada temporal.

        Args:
            X: Features
            y: Target
            n_splits: Número de folds

        Returns:
            Dicionário com métricas de cada fold
        """
        logger.info(f"Executando validação cruzada temporal com {n_splits} folds...")

        tscv = TimeSeriesSplit(n_splits=n_splits)
        cv_results = {'mae': [], 'rmse': [], 'mape': [], 'r2': []}

        X_scaled = self.scaler.fit_transform(X)

        for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
            X_train_fold = X_scaled[train_idx]
            X_test_fold = X_scaled[test_idx]
            y_train_fold = y.iloc[train_idx]
            y_test_fold = y.iloc[test_idx]

            # Treinar modelo
            model = self._train_random_forest(X_train_fold, y_train_fold)

            # Avaliar
            predictions = model.predict(X_test_fold)
            mae = mean_absolute_error(y_test_fold, predictions)
            rmse = np.sqrt(mean_squared_error(y_test_fold, predictions))
            mape = np.mean(np.abs((y_test_fold - predictions) / y_test_fold)) * 100
            r2 = r2_score(y_test_fold, predictions)

            cv_results['mae'].append(mae)
            cv_results['rmse'].append(rmse)
            cv_results['mape'].append(mape)
            cv_results['r2'].append(r2)

            logger.info(f"Fold {fold+1}: MAE={mae:.2f}, RMSE={rmse:.2f}, MAPE={mape:.2f}%, R²={r2:.4f}")

        # Calcular médias
        cv_results['mae_mean'] = np.mean(cv_results['mae'])
        cv_results['rmse_mean'] = np.mean(cv_results['rmse'])
        cv_results['mape_mean'] = np.mean(cv_results['mape'])
        cv_results['r2_mean'] = np.mean(cv_results['r2'])

        logger.info(f"CV Médio: MAE={cv_results['mae_mean']:.2f}, RMSE={cv_results['rmse_mean']:.2f}, MAPE={cv_results['mape_mean']:.2f}%, R²={cv_results['r2_mean']:.4f}")

        return cv_results

def main():
    """Função principal para teste dos modelos baseline."""
    import sys
    import os

    # Adicionar src ao path para importar módulos
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

    from data.feature_engineering import WinFeatureEngineer
    from data.win_data_collector import WinDataCollector

    # Coletar e processar dados
    collector = WinDataCollector()
    data = collector.get_win_data()

    if not data.empty:
        # Criar features
        engineer = WinFeatureEngineer()
        data_with_features = engineer.create_all_features(data)

        # Preparar para modelagem
        X, y = engineer.prepare_for_modeling(data_with_features)

        # Treinar modelos baseline
        baseline = WinBaselineModels()
        results = baseline.train_baseline_models(X, y)

        # Mostrar resultados
        print("\n=== RESULTADOS MODELOS BASELINE ===")
        for model_name, model_data in results.items():
            metrics = model_data['metrics']
            print(f"\n{model_name.upper()}:")
            print(".2f")
            print(".2f")
            print(".2f")
            print(".4f")
            print(".2f")

        # Feature importance para Random Forest
        if 'random_forest' in results:
            feature_imp = baseline.get_feature_importance('random_forest')
            print("\n=== TOP 10 FEATURES MAIS IMPORTANTES (RANDOM FOREST) ===")
            print(feature_imp.head(10))

        # Validação cruzada
        print("\n=== VALIDAÇÃO CRUZADA TEMPORAL ===")
        cv_results = baseline.cross_validate_temporal(X, y)
        print(".2f")
        print(".2f")
        print(".2f")
        print(".4f")

        # Salvar modelos
        baseline.save_models()
        print("\nModelos salvos em: models/win_predictor_v1.0/")

    else:
        print("Erro: Não foi possível coletar dados")

if __name__ == "__main__":
    main()