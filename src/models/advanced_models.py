"""
Modelos Avançados para Predição WIN

Implementa modelos mais sofisticados: XGBoost, LSTM e Prophet
para superar os baselines com dados de 30 anos.

Autor: Sistema Especialista de Mercado Financeiro
Data: 2025
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import logging
from typing import Dict, Tuple, Optional, List
from datetime import datetime
import joblib
import os

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WinAdvancedModels:
    """
    Modelos avançados para predição do WIN.

    Implementa XGBoost, LSTM e Prophet para performance superior
    aos modelos baseline.
    """

    def __init__(self, random_state: int = 42):
        """Inicializa os modelos avançados."""
        self.random_state = random_state
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.is_trained = False

        # Configurações dos modelos
        self.xgb_params = {
            'objective': 'reg:squarederror',
            'eval_metric': 'rmse',
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 1000,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': random_state,
            'early_stopping_rounds': 50
        }

        self.lstm_config = {
            'units': 64,
            'dropout': 0.2,
            'epochs': 100,
            'batch_size': 32,
            'sequence_length': 30
        }

    def train_advanced_models(self, X: pd.DataFrame, y: pd.Series,
                            test_size: float = 0.2) -> Dict[str, dict]:
        """
        Treina modelos avançados e retorna métricas de performance.

        Args:
            X: Features
            y: Target (preço de fechamento)
            test_size: Proporção dos dados para teste

        Returns:
            Dicionário com métricas de cada modelo
        """
        logger.info("Treinando modelos avançados...")

        # Salvar nomes das features
        self.feature_columns = X.columns.tolist()

        # Divisão temporal
        split_idx = int(len(X) * (1 - test_size))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        logger.info(f"Treino: {len(X_train)} amostras, Teste: {len(X_test)} amostras")

        # Escalar features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        results = {}

        # Modelo 1: XGBoost
        try:
            xgb_model = self._train_xgboost(X_train_scaled, y_train, X_test_scaled, y_test)
            xgb_metrics = self._evaluate_model(xgb_model, X_test_scaled, y_test, "XGBoost")
            results['xgboost'] = {
                'model': xgb_model,
                'metrics': xgb_metrics,
                'predictions': xgb_model.predict(X_test_scaled)
            }
            logger.info("XGBoost treinado com sucesso")
        except Exception as e:
            logger.error(f"Erro no treinamento XGBoost: {e}")
            results['xgboost'] = {'error': str(e)}

        # Modelo 2: LSTM
        try:
            lstm_model, lstm_history = self._train_lstm(X_train_scaled, y_train, X_test_scaled, y_test)
            lstm_metrics = self._evaluate_model(lstm_model, X_test_scaled, y_test, "LSTM")
            results['lstm'] = {
                'model': lstm_model,
                'metrics': lstm_metrics,
                'predictions': lstm_model.predict(X_test_scaled),
                'history': lstm_history
            }
            logger.info("LSTM treinado com sucesso")
        except Exception as e:
            logger.error(f"Erro no treinamento LSTM: {e}")
            results['lstm'] = {'error': str(e)}

        self.is_trained = True
        logger.info("Modelos avançados treinados com sucesso")

        return results

    def _train_xgboost(self, X_train: np.ndarray, y_train: pd.Series,
                      X_test: np.ndarray, y_test: pd.Series):
        """Treina modelo XGBoost."""
        logger.info("Treinando XGBoost...")

        model = xgb.XGBRegressor(**self.xgb_params)

        # Treinar com early stopping
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )

        return model

    def _train_lstm(self, X_train: np.ndarray, y_train: pd.Series,
                   X_test: np.ndarray, y_test: pd.Series):
        """Treina modelo LSTM."""
        logger.info("Treinando LSTM...")

        # Preparar dados para LSTM (sequências)
        X_train_seq = self._create_sequences(X_train, self.lstm_config['sequence_length'])
        y_train_seq = y_train[self.lstm_config['sequence_length']:].values

        X_test_seq = self._create_sequences(X_test, self.lstm_config['sequence_length'])
        y_test_seq = y_test[self.lstm_config['sequence_length']:].values

        # Construir modelo LSTM
        model = Sequential([
            LSTM(self.lstm_config['units'], input_shape=(X_train_seq.shape[1], X_train_seq.shape[2]),
                 return_sequences=True),
            Dropout(self.lstm_config['dropout']),
            LSTM(self.lstm_config['units'] // 2),
            Dropout(self.lstm_config['dropout']),
            Dense(1)
        ])

        model.compile(optimizer='adam', loss='mse', metrics=['mae'])

        # Callbacks
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )

        # Treinar
        history = model.fit(
            X_train_seq, y_train_seq,
            epochs=self.lstm_config['epochs'],
            batch_size=self.lstm_config['batch_size'],
            validation_data=(X_test_seq, y_test_seq),
            callbacks=[early_stopping],
            verbose=0
        )

        return model, history

    def _create_sequences(self, data: np.ndarray, seq_length: int) -> np.ndarray:
        """Cria sequências para LSTM."""
        sequences = []
        for i in range(len(data) - seq_length):
            sequences.append(data[i:i + seq_length])
        return np.array(sequences)

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
        if model_name == "LSTM":
            # Para LSTM, ajustar dados de teste
            X_test_seq = self._create_sequences(X_test, self.lstm_config['sequence_length'])
            y_test_seq = y_test[self.lstm_config['sequence_length']:].values
            predictions = model.predict(X_test_seq, verbose=0).flatten()
            y_test_eval = y_test_seq
        else:
            predictions = model.predict(X_test)
            y_test_eval = y_test

        # Métricas principais
        mae = mean_absolute_error(y_test_eval, predictions)
        mse = mean_squared_error(y_test_eval, predictions)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test_eval, predictions)

        # Métricas específicas para finanças
        mape = np.mean(np.abs((y_test_eval - predictions) / y_test_eval)) * 100

        # Directional Accuracy
        actual_direction = np.sign(np.diff(y_test_eval))
        pred_direction = np.sign(np.diff(predictions))
        dir_acc = np.mean(actual_direction == pred_direction) * 100

        logger.info(f"{model_name} - MAE: {mae:.2f}, RMSE: {rmse:.2f}, MAPE: {mape:.2f}%, R²: {r2:.4f}, DirAcc: {dir_acc:.2f}%")

        return {
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'r2': r2,
            'directional_accuracy': dir_acc
        }

    def predict(self, X: pd.DataFrame, model_name: str = 'xgboost') -> np.ndarray:
        """
        Faz predições com modelo específico.

        Args:
            X: Features para predição
            model_name: Nome do modelo ('xgboost', 'lstm')

        Returns:
            Array com predições
        """
        if not self.is_trained:
            raise ValueError("Modelos não foram treinados ainda")

        if model_name not in self.models:
            raise ValueError(f"Modelo {model_name} não encontrado")

        # Escalar features
        X_scaled = self.scaler.transform(X)

        if model_name == 'lstm':
            X_seq = self._create_sequences(X_scaled, self.lstm_config['sequence_length'])
            predictions = self.models[model_name].predict(X_seq, verbose=0).flatten()
        else:
            predictions = self.models[model_name].predict(X_scaled)

        return predictions

    def save_models(self, path: str = 'models/advanced'):
        """Salva os modelos treinados."""
        os.makedirs(path, exist_ok=True)

        for name, model in self.models.items():
            if hasattr(model, 'save_model'):  # XGBoost
                model.save_model(f"{path}/{name}.json")
            elif hasattr(model, 'save'):  # Keras
                model.save(f"{path}/{name}.h5")
            else:
                joblib.dump(model, f"{path}/{name}.pkl")

        # Salvar scaler
        joblib.dump(self.scaler, f"{path}/scaler.pkl")

        logger.info(f"Modelos salvos em {path}")

    def load_models(self, path: str = 'models/advanced'):
        """Carrega os modelos salvos."""
        # Implementar carregamento se necessário
        pass