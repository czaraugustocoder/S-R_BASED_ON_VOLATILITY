import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

import warnings
warnings.filterwarnings("ignore")

st.title('Supply and Demand Levels Forecasting Based on Returns Volatility')

st.write("""
         Suply and demand levels, which are also named resistance and support, are important drivers for investment and trading decisions in any kind of market. For retail trading
         in the stock market, indetifying these zones is very popular. However, these techniques have 
         an issue which is they are subject to personal interpretation of the current scenario pointed out by a chart or indicators that are calculated
         from past price data. The Supply and Demand Levels Forecasting Based on Returns Volatility its a proposition for not arbitrarily or subjetively on a chart""")

current_working_directory = os.getcwd()

cwdarq = os.path.join(current_working_directory, "acoes_listadas_b3.csv")

print(cwdarq)

acoes = pd.read_csv(cwdarq, sep=";")

acao = st.sidebar.selectbox('Choose your stock', acoes)

acoes_br = acoes.loc[acoes['Market'] == 'B3']['Ticker_Nome'].tolist()

if acao in acoes_br:

    acao_cod = str(acao.split("-")[0])
    acao_cod = acao_cod.strip()

    if acao_cod == "IBOV":
        ticker1 = "^BVSP"
    else:
        ticker1 = str(acao_cod+".SA")

else:

    acao_cod = str(acao.split("-")[0])
    acao_cod = acao_cod.strip()
    ticker1 = acao_cod

print(ticker1)
df1 = yf.download(ticker1, "2012-01-01", str(datetime.today().date()))
df1["Returns"] = df1["Adj Close"].pct_change(1)
df1["Adj Low"] = df1["Low"] - (df1["Close"]-df1["Adj Close"])
df1["Adj High"] = df1["High"] - (df1["Close"]-df1["Adj Close"])
df1["Adj Open"] = df1["Open"] - (df1["Close"]-df1["Adj Close"])
df1["Target"] = df1["Returns"].shift(-1)


vol_p1 = 20
df1["Vol"] = np.round((df1["Returns"].rolling(vol_p1).std()*np.sqrt(252))/np.sqrt(12), 4)
df1["MM_20"] = df1["Close"].rolling(vol_p1).mean()
df1["MM_10"] = df1["Close"].rolling(10).mean()

def gerar_datas_entre(data_inicio, data_fim):
    datas = []
    data_atual = datetime.strptime(data_inicio, '%Y-%m')
    data_fim = datetime.strptime(data_fim, '%Y-%m')
    
    while data_atual <= data_fim:
        datas.append(data_atual.strftime('%Y-%m'))
        # Avança para o próximo mês
        if data_atual.month == 12:
            data_atual = data_atual.replace(year=data_atual.year + 1, month=1)
        else:
            data_atual = data_atual.replace(month=data_atual.month + 1)
    
    return datas

# Exemplo de uso
data_inicio = '2024-01'
data_fim = '2024-07'

datas = gerar_datas_entre(data_inicio, data_fim)
print(datas)

Upper_Band_12m1d = []
Lower_Band_12m1d = []
Upper_Band_12m2d = []
Lower_Band_12m2d = []
for mes in range(1, len(datas)):

    year = str(datas[mes])
    year_std = str(datas[mes-1])

    for mes_f in range(0,len(df1.loc[year]["Vol"].index.tolist())):

        Upper_Band_12m1d.append(df1.loc[year_std]["Vol"][-1]*df1.loc[year_std]["Adj Close"][-1] + df1.loc[year_std]["Adj Close"][-1])
        Lower_Band_12m1d.append(df1.loc[year_std]["Adj Close"][-1] - df1.loc[year_std]["Vol"][-1]*df1.loc[year_std]["Adj Close"][-1])

        Upper_Band_12m2d.append(2*df1.loc[year_std]["Vol"][-1]*df1.loc[year_std]["Adj Close"][-1] + df1.loc[year_std]["Adj Close"][-1])
        Lower_Band_12m2d.append(df1.loc[year_std]["Adj Close"][-1] - 2*df1.loc[year_std]["Vol"][-1]*df1.loc[year_std]["Adj Close"][-1])

year_0 = str(datas[1])
year_1 = str(datas[-1])

# Annual S&D Volatility Zones chart

fig = make_subplots(rows = 2, cols = 1,
                    shared_xaxes = True,
                    vertical_spacing = 0.08)

fig.add_trace(go.Candlestick(x = df1.loc[year_0:year_1].index
                            , open = df1.loc[year_0:year_1]["Adj Open"], high = df1.loc[year_0:year_1]["Adj High"]
                            , low = df1.loc[year_0:year_1]["Adj Low"], close = df1.loc[year_0:year_1]["Adj Close"]
                            , name = "Candle"
                            , increasing_line_color = "black", decreasing_line_color = "red")
            , row = 1, col = 1
            )

fig.add_trace(go.Scatter(x = df1.loc[year_0:year_1].index, y = Upper_Band_12m1d
                         , name = "Upper_Band_12m1d", line = dict({'color': 'blue', 'dash': 'dot'}))
              , row = 1, col = 1)

fig.add_trace(go.Scatter(x = df1.loc[year_0:year_1].index, y = Lower_Band_12m1d
                         , name = "Lower_Band_12m1d", line = dict({'color': 'blue', 'dash': 'dot'}))
              , row = 1, col = 1)

fig.add_trace(go.Scatter(x = df1.loc[year_0:year_1].index, y = Upper_Band_12m2d
                         , name = "Upper_Band_12m2d", line = dict({'color': 'green', 'dash': 'dot'}))
              , row = 1, col = 1)

fig.add_trace(go.Scatter(x = df1.loc[year_0:year_1].index, y = Lower_Band_12m2d
                         , name = "Lower_Band_12m2d", line = dict({'color': 'green', 'dash': 'dot'}))
              , row = 1, col = 1)

#fig.add_trace(go.Scatter(x = df1.loc[year_0:year_1].index, y = df1.loc[year_0:year_1]["MM_20"]
#                         , name = "Média Móvel 20", line = dict({'color': '#FFB3B3'}))
#              , row = 1, col = 1)

#fig.add_trace(go.Scatter(x = df1.loc[year_0:year_1].index, y = df1.loc[year_0:year_1]["MM_10"]
#                         , name = "Média Móvel 10", line = dict({'color': 'yellow'}))
#              , row = 1, col = 1)


fig.update_layout(height = 600, width = 800
                , title_text = "Monthly S&D Volatility Zones: " + ticker1 + " - " + str(datetime.today().date())
                , font_color = "blue"
                , title_font_color = "black"
                , yaxis_title = "close"
                , yaxis2_title = "volatility"
                , legend_title = "Vol"
                , font = dict(size = 15, color = "Black")
                , xaxis_rangeslider_visible = False
                , showlegend=False
                )
fig.update_layout(hovermode = "x")

fig.add_trace(go.Scatter(x = df1.loc[year_0:year_1].index, y = df1.loc[year_0:year_1]["Vol"]*100
                         , name = "Volatilidade", line = dict(color = "blue"))
              , row = 2, col = 1)

# Code to exclude empty dates from the chart
dt_all = pd.date_range(start = df1.loc[year_0:year_1].index[0]
                    , end = df1.loc[year_0:year_1].index[-1]
                    , freq = "D")
dt_all_py = [d.to_pydatetime() for d in dt_all]
dt_obs_py = [d.to_pydatetime() for d in df1.loc[year_0:year_1].index]

dt_breaks = [d for d in dt_all_py if d not in dt_obs_py]

fig.update_xaxes(
    rangebreaks = [dict(values = dt_breaks)]
)

#fig.show()

st.plotly_chart(fig, use_container_width=True)
