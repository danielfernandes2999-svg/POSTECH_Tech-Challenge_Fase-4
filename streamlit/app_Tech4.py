import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
API_URL = os.getenv('API_URL', 'http://api:5000')

# Arquivo de log de consultas
LOG_FILE = "logs/consultas.csv"


os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

st.title("Previsão Índice B3")

# Bloco de Métricas em Destaque 
st.write("### 🏆 Desempenho do Modelo")
try:
    response_metrics = requests.get(f"{API_URL}/metrics", timeout=10)
    if response_metrics.status_code == 200:
        metrics = response_metrics.json()
        
        # Criando 4 colunas para as métricas principais
        m1, m2, m3, m4 = st.columns(4)
        
        # Estilizando com st.metric
        m1.metric("🎯 Acurácia", f"{metrics['accuracy']*100:.1f}%")
        m2.metric("📊 F1 Score", f"{metrics['f1']*100:.1f}%")
        m3.metric("✅ Precisão", f"{metrics['precision']*100:.1f}%")
        m4.metric("🔄 Recall", f"{metrics['recall']*100:.1f}%")
        
        # Uma linha fina para separar do resto do conteúdo
        st.markdown("---")
    else:
        st.warning("⚠️ Aguardando conexão com a API para carregar métricas...")
except Exception:
    st.error("❌ Erro ao conectar com o serviço de métricas.")

st.write("Insira os valores do ultimo pregão para obter a previsão do próximo dia:")

def formato_b3(valor: float, casas: int = 0) -> str:
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Garantir que o log existe
if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["ID", "DataConsulta", "Ultimo", "Abertura", "Maxima", "Minima", "Previsao"]).to_csv(LOG_FILE, index=False)

# Última data registrada no histórico original
df_hist = pd.read_csv("Dados/Dados Históricos - Ibovespa_ate_09_01.csv", dtype={'Último': str})
df_hist = df_hist.rename(columns={
    'Último': 'Ultimo',
    'Máxima': 'Maxima',
    'Mínima': 'Minima',
    'Abertura': 'Abertura',
    'Var%': 'VarPct',
    'Data': 'Data'
})

df_hist["Data"] = pd.to_datetime(df_hist["Data"], format="%d.%m.%Y", errors="coerce")
ultima_data_historico = df_hist["Data"].max().date()
st.info(f"📂 Último pregão registrado: {ultima_data_historico.strftime('%d/%m/%Y')}")

# =================================================================
# COMPONENTE DE ATUALIZAÇÃO DA BASE DE DADOS (CSV)
# =================================================================
st.sidebar.markdown("---")
st.sidebar.header("⚙️ Configurações de Dados")

# Instruções de uso
st.sidebar.info("""
**Instruções para atualização:**
1. Acesse o site [Investing.com](https://br.investing.com/indices/bovespa-historical-data).
2. Selecione o período desejado. Para melhor acurácia, o ideal é que a data do ultimo pregão seja até 2 dias antes da previsão.
3. Certifique-se de que o **Intervalo** está como **Diário**.
4. Baixe o CSV e faça o upload abaixo.
""")

arquivo_novo = st.sidebar.file_uploader("Subir nova base Ibovespa (CSV)", type=["csv"])

if arquivo_novo is not None:
    try:
        # 1. Lê o arquivo
        df_temp = pd.read_csv(arquivo_novo, dtype={'Último': str})
        
        # 2. PADRONIZAÇÃO AUTOMÁTICA 
        mapeamento = {
            'Data': 'Data', 'data': 'Data',
            'Último': 'Último', 'Ultimo': 'Último', 'ultimo': 'Último',
            'Abertura': 'Abertura', 'abertura': 'Abertura',
            'Máxima': 'Máxima', 'Maxima': 'Máxima', 'maxima': 'Máxima',
            'Mínima': 'Mínima', 'Minima': 'Mínima', 'minima': 'Mínima',
            'Vol.': 'Vol.', 'Var%': 'Var%'
        }
        df_temp = df_temp.rename(columns=mapeamento)

        # 3. VALIDAÇÃO
        colunas_necessarias = ['Data', 'Último', 'Abertura', 'Máxima', 'Mínima']
        faltando = [c for c in colunas_necessarias if c not in df_temp.columns]

        if not faltando:
            # 4. SALVAMENTO (Sobrescrevendo o arquivo oficial no volume do Docker)
            caminho_correto = "Dados/Dados Históricos - Ibovespa_ate_09_01.csv"
            df_temp.to_csv(caminho_correto, index=False)
            
            st.sidebar.success(f"✅ Base '{arquivo_novo.name}' integrada!")
            
            if st.sidebar.button("🔄 Aplicar e Atualizar Gráfico"):
                st.rerun()
        else:
            st.sidebar.error(f"❌ O arquivo deve conter: {', '.join(faltando)}")
            
    except Exception as e:
        st.sidebar.error(f"⚠️ Erro ao processar: {e}")

# Inputs
proxima_data = ultima_data_historico + timedelta(days=1)
input_Data = st.date_input("Data do pregão", proxima_data)
input_Ultimo = st.number_input("Último fechamento", format="%.0f")
input_Abertura = st.number_input("Abertura", format="%.0f")
input_Maxima = st.number_input("Máxima", format="%.0f")
input_Minima = st.number_input("Mínima", format="%.0f")

st.write("### Valores digitados (formato B3)")
st.write("Último fechamento:", formato_b3(input_Ultimo))
st.write("Abertura:", formato_b3(input_Abertura))
st.write("Máxima:", formato_b3(input_Maxima))
st.write("Mínima:", formato_b3(input_Minima))

# Botão prever
if st.button("Prever"):
    novo_registro = {
        "Data": input_Data.strftime("%d.%m.%Y"),
        "Ultimo": input_Ultimo,
        "Abertura": input_Abertura,
        "Maxima": input_Maxima,
        "Minima": input_Minima,
    }
    
    try:
        
        response = requests.post(f"{API_URL}/predict", json=novo_registro, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            previsao = "Alta" if result.get("prediction", 0) == 0 else "Baixa"

            # Mostrar resultado
            if previsao == "Alta":
                st.success(f"✅ Previsão para {input_Data.strftime('%d/%m/%Y')}: Alta 📈")
            else:
                st.error(f"⚠️ Previsão para {input_Data.strftime('%d/%m/%Y')}: Baixa 📉")

            # Registrar no log
            df_log = pd.read_csv(LOG_FILE)
            novo_id = len(df_log) + 1
            novo_log = pd.DataFrame([{
                "ID": novo_id,
                "DataConsulta": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "Ultimo": input_Ultimo,
                "Abertura": input_Abertura,
                "Maxima": input_Maxima,
                "Minima": input_Minima,
                "Previsao": previsao
            }])
            
            df_log = pd.concat([df_log, novo_log], ignore_index=True)
            df_log.to_csv(LOG_FILE, index=False)
            st.success("📑 Consulta registrada no log!")


            st.write("### 📊 Histórico e Tendência Prevista")

            # 1. Preparar dados (já ordenados)
            df_mat = df_hist.tail(15).copy()
            df_mat['Ultimo'] = pd.to_numeric(df_mat['Ultimo'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')
            df_mat['Data'] = pd.to_datetime(df_mat['Data'], dayfirst=True)
            df_mat = df_mat.dropna(subset=['Ultimo']).sort_values("Data")

            # 2. Configurar a figura
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(df_mat['Data'], df_mat['Ultimo'], marker='o', linestyle='-', color='#003366', label='Histórico', linewidth=2)

            # 3. ADICIONAR A PREVISÃO NO GRÁFICO
            ultima_data = df_mat['Data'].iloc[-1]
            ultimo_valor = df_mat['Ultimo'].iloc[-1]

            # Definir a direção da seta e a cor baseada na variável 'previsao'
            if previsao == "Alta":
                cor_prev = 'green'
                simbolo_prev = '▲'
                offset = (df_mat['Ultimo'].max() - df_mat['Ultimo'].min()) * 0.2  # Seta para cima
            else:
                cor_prev = 'red'
                simbolo_prev = '▼'
                offset = -(df_mat['Ultimo'].max() - df_mat['Ultimo'].min()) * 0.2 # Seta para baixo

            
            data_previsao = ultima_data + timedelta(days=1)

            # Desenhar a seta de tendência
            ax.annotate('', 
                xy=(data_previsao, ultimo_valor + offset), 
                xytext=(ultima_data, ultimo_valor),
                arrowprops=dict(facecolor=cor_prev, edgecolor=cor_prev, shrink=0.05, width=3, headwidth=10),
                        label=f'Previsão: {previsao}')

            # Adicionar o texto (Alta/Baixa)
            ax.text(data_previsao, ultimo_valor + offset, f" PREVISÃO:\n {previsao} {simbolo_prev}", 
                    color=cor_prev, fontweight='bold', fontsize=12, va='center')

            # 4. Ajustes Finais 
            min_y = df_mat['Ultimo'].min()
            max_y = df_mat['Ultimo'].max()
            ax.set_ylim(min_y - abs(offset), max_y + abs(offset)) # Ajusta o zoom para caber a seta

            ax.grid(True, linestyle='--', alpha=0.6)
            plt.xticks(rotation=45)
            plt.title(f"B3: Histórico + Tendência para {input_Data.strftime('%d/%m')}", fontsize=14)

            st.pyplot(fig)

        else:
            st.error(f"❌ Erro na API: {response.status_code}")
            
    except Exception as e:
        st.error(f"⚠️ Erro inesperado: {str(e)}")

# Histórico de consultas
st.write("---")
st.write("### 📑 Log de Consultas")
try:
    df_log_display = pd.read_csv(LOG_FILE)
    st.dataframe(df_log_display.sort_values("ID", ascending=False), use_container_width=True)
except:
    st.write("Ainda não há logs registrados.")
