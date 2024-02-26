import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

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

    # Visualização da Curva de DTR com indicação de volume morto

    plt.figure(figsize=(10, 6))

    plt.plot(tempo, dtr, label='DTR')
    # plt.axvline(x=limite_inferior_pistonado, color='r', linestyle='--', label='Limite Inferior Pistonado')
    # plt.axvline(x=limite_superior_pistonado, color='r', linestyle='--', label='Limite Superior Pistonado')
    # plt.axvline(x=limite_superior_volume_morto, color='g', linestyle='--', label='Limite Superior Volume Morto')

    # Preenchendo a área entre os limites do volume de mistura
    plt.fill_between(tempo, dtr, where=((tempo >= limite_inferior_bypass) & (tempo <= limite_inferior_pistonado) | (tempo >= limite_superior_pistonado) & (tempo <= limite_superior_volume_morto)), color='green', alpha=0.1, label='Volume de Mistura')

    # Preenchendo a área entre os limites do volume de Bypass
    plt.fill_between(tempo, dtr, where=(tempo <= limite_inferior_bypass), color='yellow', alpha=0.1, label='Volume de Bypass')

    # Preenchendo a área entre os limites do volume pistonado
    plt.fill_between(tempo, dtr, where=(tempo >= limite_inferior_pistonado) & (tempo <= limite_superior_pistonado), color='red', alpha=0.1, label='Volume Pistonado')

    # Preenchendo a área entre os limites do volume morto
    plt.fill_between(tempo, dtr, where=(tempo >= limite_superior_volume_morto), color='blue', alpha=0.1, label='Volume Morto')

    plt.xlabel('Tempo')
    plt.ylabel('E(t)')
    plt.title('Análise de Distribuição de Tempo de Residência (DTR)')
    plt.legend()

    # Limitando o eixo x e y a começar em zero
    plt.ylim(bottom=0)
    plt.xlim(left=0)

    # Preparando o texto a ser adicionado abaixo da legenda
    texto_informacoes = f"Tempo médio de residência: {tm:.2f}\n"
    texto_informacoes += f"Variância do tempo de residência: {variancia:.2f}\n"
    texto_informacoes += f"Desvio padrão do tempo de residência: {desvio_padrao:.2f}\n"
    texto_informacoes += f"Skewness do tempo de residência: {skewness:.2f}\n\n"

    texto_informacoes2 = f"Volume de mistura: {percentual_mistura * 100:.2f}%\n"
    texto_informacoes2 += f"Volume de bypass (tempos < tm - 2*SD): {percentual_bypass * 100:.2f}%\n"
    texto_informacoes2 += f"Volume pistonado: {percentual_pistonado * 100:.2f}%\n"
    texto_informacoes2 += f"Volume morto (tempos > tm + 2*SD): {percentual_volume_morto * 100:.2f}%"


    figure_file = 'assets/DTR_Plots/DTR.png'
    plt.savefig(figure_file)
    plt.close()

    #plot_pearson_distribution(tm, variancia, skewness, tempo_novos)

    return texto_informacoes, texto_informacoes2

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
