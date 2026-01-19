POSTECH - Tech Challenge - Fase 4

Sistema de Previsão de Tendência B3

Este projeto é uma ferramenta de análise preditiva desenvolvida para prever a tendência (Alta ou Baixa) do índice B3 para o próximo pregão, utilizando o algoritmo KNN (K-Nearest Neighbors).

O projeto utiliza os seguintes programas:

1.  API (Flask): Responsável por carregar o modelo treinado, processar os dados recebidos e retornar a predição e as métricas de performance (Acurácia, F1-Score, etc).
2.  Streamlit: Interface de usuário que consome a API, exibe gráficos históricos com tendências futuras e permite o upload de novas bases de dados.
3.  Docker & Docker Compose: Para orquestração e compartilhamento de Dados, permitindo que atualizações na base de dados via interface reflitam instantaneamente nos cálculos da API.