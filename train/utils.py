import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

class FeatureEngineeringTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, modo="treino"):

        self.modo = modo

    def fit(self, df, y=None):
        return self

    def transform(self, df):
        df = df.copy()

        # Renomear colunas
        df.rename(columns={'Último': 'Ultimo',
                           'Máxima': 'Maxima',
                           'Mínima': 'Minima'}, inplace=True)

        # Coluna Ultimo_Ontem
        df['Ultimo_Ontem'] = df['Ultimo'].shift(1)
        df = df.iloc[1:].reset_index(drop=True) if self.modo == "treino" else df

        # Target: 1 se subir, 0 se cair (apenas no treino)
        if self.modo == "treino":
            df['Target'] = (df['Ultimo_Ontem'] > df['Ultimo']).astype(int)

        # Features derivadas
        df['Fechamento_ontem'] = df['Ultimo'].shift(-1)
        df['Variacao_Abertura'] = df['Abertura'] - df['Fechamento_ontem']
        df['Rel_max_min'] = df['Maxima'] / df['Minima']
        df['Forca'] = (df['Ultimo'] - df['Minima']) / (df['Maxima'] - df['Minima'])
        df['Variacao_ontem'] = df['Maxima'].shift(1) - df['Minima'].shift(1)
        df['max_diff_1d'] = df['Maxima'] - df['Maxima'].shift(1)
        df['min_diff_1d'] = df['Minima'] - df['Minima'].shift(1)
        df['max_diff_2d'] = df['Maxima'] - df['Maxima'].shift(2)
        df['min_diff_2d'] = df['Minima'] - df['Minima'].shift(2)
        df['Rel_aber_ult'] = df['Abertura'] - df['Ultimo'].shift(1)
        df['Forca_1d'] = (df['Ultimo'] - df['Minima']) / (df['Maxima'] - df['Minima']).shift(1)
        df['Aber_Fech_1d'] = (df['Abertura'] - df['Ultimo'].shift(1)) / df['Ultimo'].shift(1) * 100
        df['Aber_Fech_2d'] = (df['Abertura'] - df['Ultimo'].shift(2)) / df['Ultimo'].shift(2) * 100

        # Remover NaN apenas no treino
        if self.modo == "treino":
            df.dropna(subset=[
                'Variacao_Abertura', 'Variacao_ontem', 'max_diff_1d', 'min_diff_1d',
                'max_diff_2d', 'min_diff_2d', 'Rel_aber_ult', 'Forca_1d',
                'Aber_Fech_1d', 'Aber_Fech_2d'
            ], inplace=True)

        return df
