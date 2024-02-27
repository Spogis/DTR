import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import plotly.graph_objects as go
from dash import dcc

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

def GeraGrafico(Dataset):
    # Passo 1: Leitura dos dados
    #caminho_do_arquivo = 'DTR_Curves/DTR3.xlsx'
    #dados = pd.read_excel(caminho_do_arquivo)

    dados = Dataset

    # Adicionando o ponto (0, 0) ao DataFrame
    nomes_das_colunas = dados.columns.tolist()
    novo_ponto = pd.DataFrame({nomes_das_colunas[0]: [0], nomes_das_colunas[1]: [0]})
    dados = pd.concat([novo_ponto, dados], ignore_index=True)
    dados = dados.sort_values(by=nomes_das_colunas[0]).reset_index(drop=True)

    tempo = dados.iloc[:, 0]
    concentracao = dados.iloc[:, 1]

    # Gera 5000 pontos igualmente espaçados entre o mínimo e o máximo de x
    tempo_novos = np.linspace(tempo.min(), tempo.max(), 10000)
    # Cria a função de interpolação
    funcao_interp = interp1d(tempo, concentracao, kind='linear')  # 'cubic' para interpolação cúbica; pode ajustar conforme necessário
    # Usa a função de interpolação para obter os novos valores de y
    concentracao_novos = funcao_interp(tempo_novos)

    tempo=tempo_novos
    concentracao = concentracao_novos

    # Passo 2: Cálculo da Curva de DTR
    area_sob_curva = np.trapz(concentracao, tempo)
    dtr = concentracao / area_sob_curva

    # Passo 3: Análise da DTR
    tm = np.trapz(tempo * dtr, tempo)
    variancia = np.trapz((tempo - tm)**2 * dtr, tempo)
    desvio_padrao = np.sqrt(variancia)

    # Cálculo da Skewness
    skewness = np.trapz(((tempo - tm) ** 3) * dtr, tempo) / (desvio_padrao ** 3)

    # Identificação de volume pistonado
    # Aqui, utilizaremos uma abordagem simplificada
    limite_inferior_pistonado = tm - desvio_padrao
    limite_superior_pistonado = tm + desvio_padrao

    # Percentual de tempo de residência dentro da faixa de volume pistonado
    percentual_pistonado = np.trapz(dtr[(tempo >= limite_inferior_pistonado) & (tempo <= limite_superior_pistonado)], tempo[(tempo >= limite_inferior_pistonado) & (tempo <= limite_superior_pistonado)]) / np.trapz(dtr, tempo)

    # Definição de critérios para volume morto
    limite_superior_volume_morto = tm + 2 * desvio_padrao  # Exemplo de critério para volume morto

    # Percentual de tempo de residência considerado como volume morto
    # Neste exemplo, consideramos o volume morto para tempos de residência muito longos
    percentual_volume_morto = np.trapz(dtr[tempo > limite_superior_volume_morto], tempo[tempo > limite_superior_volume_morto]) / np.trapz(dtr, tempo)

    # Definição de critérios para volume de bypass
    limite_inferior_bypass = tm - 2 * desvio_padrao  # Exemplo de critério para volume morto

    # Percentual de tempo de residência considerado como volume de bypass
    # Neste exemplo, consideramos o volume de bypass para tempos de residência muito curtos
    percentual_bypass = np.trapz(dtr[tempo < limite_inferior_bypass], tempo[tempo < limite_inferior_bypass]) / np.trapz(dtr, tempo)

    # Assumindo que volumes não identificados como pistonado, morto ou bypass contribuem para a mistura
    percentual_total_identificado = percentual_pistonado + percentual_volume_morto + percentual_bypass
    percentual_mistura = 1 - percentual_total_identificado  # Restante não classificado explicitamente


    # Preparando o texto a ser retornado
    texto_informacoes = f"Tempo médio de residência: {tm:.2f}\n"
    texto_informacoes += f"Variância do tempo de residência: {variancia:.2f}\n"
    texto_informacoes += f"Desvio padrão do tempo de residência: {desvio_padrao:.2f}\n"
    texto_informacoes += f"Skewness do tempo de residência: {skewness:.2f}\n\n"
    texto_informacoes += f"Volume de mistura: {percentual_mistura * 100:.2f}%\n"
    texto_informacoes += f"Volume de bypass (tempos < tm - 2*SD): {percentual_bypass * 100:.2f}%\n"
    texto_informacoes += f"Volume pistonado: {percentual_pistonado * 100:.2f}%\n"
    texto_informacoes += f"Volume morto (tempos > tm + 2*SD): {percentual_volume_morto * 100:.2f}%"


    #plot_pearson_distribution(tm, variancia, skewness, tempo_novos)


########################################################################################################################
    # Criando a figura com Plotly
    fig = go.Figure()

    # Adicionando a linha DTR
    fig.add_trace(go.Scatter(x=tempo, y=dtr, mode='lines', name='DTR', line=dict(color='black')))

    # Para adicionar preenchimentos condicionais, precisamos segmentar os dados manualmente.

    # Volume de Bypass
    idx_bypass = tempo <= limite_inferior_bypass
    fig.add_trace(go.Scatter(x=tempo[idx_bypass], y=dtr[idx_bypass], mode='none', fill='tozeroy',
                             fillcolor='rgba(255, 255, 0, 0.5)', name='Volume de Bypass'))

    # Volume de Mistura
    idx_mistura1 = (tempo >= limite_inferior_bypass) & (tempo <= limite_inferior_pistonado)
    fig.add_trace(go.Scatter(x=tempo[idx_mistura1], y=dtr[idx_mistura1], mode='none',
                             fill='tozeroy', fillcolor='rgba(0, 255, 0, 0.5)', name='Volume de Mistura'))

    idx_mistura2 = (tempo >= limite_superior_pistonado) & (tempo <= limite_superior_volume_morto)
    fig.add_trace(go.Scatter(x=tempo[idx_mistura2], y=dtr[idx_mistura2], mode='none', showlegend=False,
                             fill='tozeroy', fillcolor='rgba(0, 255, 0, 0.5)', name='Volume de Mistura'))

    # Volume Pistonado
    idx_pistonado = np.where((tempo >= limite_inferior_pistonado) & (tempo <= limite_superior_pistonado))[0]
    fig.add_trace(go.Scatter(x=tempo[idx_pistonado], y=dtr[idx_pistonado], mode='none', fill='tozeroy',
                             fillcolor='rgba(255, 0, 0, 0.5)', name='Volume Pistonado'))

    # Volume Morto
    idx_volume_morto = tempo >= limite_superior_volume_morto
    fig.add_trace(go.Scatter(x=tempo[idx_volume_morto], y=dtr[idx_volume_morto], mode='none', fill='tozeroy',
                             fillcolor='rgba(0, 0, 255, 0.5)', name='Volume Morto'))

    # Atualizando os layouts do gráfico
    fig.update_layout(title='Análise de Distribuição de Tempo de Residência (DTR)',
                      xaxis_title='Tempo',
                      yaxis_title='E(t)',
                      title_x=0.5)

    return texto_informacoes, fig

def plot_pearson_distribution(mean, variance, skewness, tempo_novos):
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.stats import gamma

    # Parâmetros da distribuição
    media = mean
    desvio_padrao = np.sqrt(variance)
    coeficiente_assimetria = skewness  # Exemplo de assimetria positiva

    # Calculando os parâmetros para a distribuição gama
    alfa = 4 / coeficiente_assimetria ** 2  # Forma
    beta = np.sqrt((desvio_padrao ** 2) / alfa)  # Escala
    loc = media - alfa * beta  # Localização

    # Valores para o eixo x
    x = tempo_novos

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(x, gamma.pdf(x, a=alfa, scale=beta, loc=loc),
             'r-', lw=1, alpha=0.6, label='Pearson Tipo III pdf')

    plt.title('Distribuição Pearson Tipo III')
    plt.xlabel('Valores')
    plt.ylabel('Densidade de Probabilidade')
    plt.legend(loc='best')
    # Limitando o eixo x e y a começar em zero
    plt.ylim(bottom=0)
    plt.xlim(left=0)

    figure_file = 'assets/DTR_Plots/Pearson.png'
    plt.savefig(figure_file)
    plt.close()
