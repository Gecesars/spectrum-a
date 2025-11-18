

# **Relatório Técnico: Classificação Regulatória, Limiares de Recepção e Metodologias de Cálculo e Visualização de Contornos de Radiodifusão (FM e TV Digital) Conforme Padrões ANATEL**

## **I. Estrutura Regulatória e Classificação de Emissoras de Radiodifusão no Brasil**

A gestão do espectro radioelétrico para serviços de radiodifusão no Brasil, conduzida pela Agência Nacional de Telecomunicações (ANATEL), é fundamentada em um sistema de classificação de emissoras. Este sistema não se baseia apenas em um único parâmetro, mas em uma inter-relação complexa entre a potência de transmissão, a altura da antena e o alcance geográfico resultante. Esta seção detalha os pilares dessa classificação para os serviços de Frequência Modulada (FM) e Televisão Digital (TV Digital).

### **A. Os Pilares Regulatórios: ERP e HAAT como Métricas de Planejamento**

A estrutura regulatória da ANATEL utiliza dois parâmetros técnicos fundamentais para definir os limites operacionais e a classe de uma estação de radiodifusão: a Potência Efetiva Radiada (ERP) e a Altura da Antena Sobre o Terreno Médio (HAAT).

1. **Potência Efetiva Radiada (ERP \- Effective Radiated Power):** A ERP é o parâmetro primário de classificação.1 É crucial notar que a ERP não é simplesmente a potência de saída do transmissor (TPO). Ela é definida como o produto da potência do transmissor pelo ganho do sistema de antena, medido na direção de máxima irradiação. Em termos logarítmicos, é a soma da potência do transmissor (em dBk ou dBW) e do ganho da antena (em dBd ou dBi), subtraídas as perdas do sistema (cabos, conectores, etc.). A regulamentação define os *limites máximos* de ERP para cada classe.2  
2. **Altura da Antena Sobre o Terreno Médio (HAAT \- Height Above Average Terrain):** Também referida na regulamentação brasileira como HNMT (Altura de Referência sobre o Nível Médio da Radial), este parâmetro é igualmente crítico.1 O HAAT não é a altura física da torre. É uma medida complexa da elevação do centro de irradiação da antena em relação ao terreno circundante. O cálculo padrão, alinhado com as recomendações internacionais (como as da FCC dos EUA e da UIT), envolve:  
   * Amostragem de dados de elevação do terreno (obtidos de um Modelo de Elevação Digital \- DEM) ao longo de múltiplas radiais, tipicamente oito (em azimutes de 0, 45, 90, 135, 180, 225, 270 e 315 graus).3  
   * O cálculo da elevação média do terreno ao longo de cada radial, em uma faixa de distância específica, comumente de 3 km a 16 km do local da antena.3  
   * A subtração dessa elevação média do terreno da altura da antena acima do nível médio do mar (AMSL) para obter o HAAT em cada radial específica.  
   * O HAAT médio da estação (para fins de classificação) é a média aritmética dos valores de HAAT obtidos nas oito radiais.3

A regulamentação da ANATEL não define a classe de uma estação apenas pela sua ERP; ela estabelece um sistema de *trade-off* (compensação) entre ERP e HAAT. As tabelas regulatórias definem os requisitos *máximos* permitidos para cada classe.1 Isso cria um "teto operacional" que reconhece a física da propagação de rádio: a distância de cobertura (e, portanto, o potencial de interferência) é uma função de *ambos*, ERP e HAAT. Na prática, uma classe de estação é uma autorização para um "orçamento de interferência" máximo, permitindo flexibilidade de engenharia dentro desses limites.

### **B. Classificação de Emissoras de Rádio FM e RTR (Retransmissão de Rádio)**

Para os serviços de Radiodifusão Sonora em Frequência Modulada (FM) e Retransmissão de Rádio na Amazônia Legal (RTR), a classificação e os requisitos técnicos são estabelecidos pelo Ato nº 4174, de 16 de maio de 2021\.2 Este ato consolida o Plano Básico de Distribuição de Canais de FM (PBFM).5  
O Ato define 10 classes de canais, variando de E1 (a mais alta potência) a C (a mais baixa potência).2 A tabela a seguir, baseada no Ato nº 4174, detalha os requisitos máximos para cada classe.  
Tabela 1: Classificação dos Canais de FM e RTR em Função de suas Características Máximas 2

| CLASSES | REQUISITOS MÁXIMOS |  |  |  |
| :---- | :---- | :---- | :---- | :---- |
|  | **POTÊNCIA (ERP)** |  | **DISTÂNCIA MÁXIMA AO CONTORNO PROTEGIDO ($66 \\text{ dBµV/m}$) (km)** | **ALTURA DE REFERÊNCIA SOBRE O NÍVEL MÉDIO DA RADIAL (m)** |
|  | **kW** | **dBk** |  |  |
| E1 | 100 | 20,0 | 78,5 | 600 |
| E2 | 75 | 18,8 | 67,5 | 450 |
| E3 | 60 | 17,8 | 54,5 | 300 |
| A1 | 50 | 17,0 | 38,5 | 150 |
| A2 | 30 | 14,8 | 35,0 | 150 |
| A3 | 15 | 11,8 | 30,0 | 150 |
| A4 | 5 | 7,0 | 24,0 | 150 |
| B1 | 3 | 4,8 | 16,5 | 90 |
| B2 | 1 | 0 | 12,5 | 90 |
| C | 0,3 | \-5,2 | 7,5 | 60 |

Fonte: ANATEL, Ato nº 4174, de 16 de maio de 2021 2  
Uma análise aprofundada desta tabela revela a natureza não linear da propagação de rádio. Por exemplo, ao comparar a Classe B2 com a Classe E1, observa-se que um aumento de potência de 100 vezes (de 1 kW para 100 kW) resulta em um aumento na distância máxima do contorno de apenas 6,28 vezes (de 12,5 km para 78,5 km).  
Este fenômeno de "retornos decrescentes" ocorre porque a intensidade do campo de RF, em um cenário real sobre o terreno, diminui a uma taxa muito mais rápida do que o quadrado da distância (como ocorreria no espaço livre). A relação entre a potência (ERP) e a intensidade do campo (dBµV/m) é logarítmica. Ao estabelecer essas classes, a ANATEL está, na prática, encapsulando essa realidade física em sua regulamentação. O sistema incentiva os engenheiros a otimizar o HAAT (um ativo de infraestrutura de longo prazo) em vez de simplesmente aumentar a ERP (o que consome mais energia e gera mais interferência para outros radiodifusores).  
O Ato nº 4174 também especifica que "A classe do canal é identificada pela radial de maior distância ao contorno protegido".2 Isso confirma que o contorno de serviço não é um círculo perfeito; ele é determinado pelo terreno em 360 graus, e a classificação da estação é definida pelo seu "pior caso" de alcance, exceto se essa radial terminar sobre água ou território estrangeiro.2

### **C. Classificação de Emissoras de TV Digital (ISDB-Tb)**

Para os serviços de Radiodifusão de Sons e Imagens Digital (GTVD) e Retransmissão de Televisão Digital (RTVD), sob o padrão ISDB-Tb, a regulamentação é definida pelo Ato nº 9751, de 6 de julho de 2022 6, que revogou atos anteriores como o Ato nº 3114, de 10 de junho de 2020\.7  
A classificação para TV Digital é dividida em quatro classes principais: Especial, A, B e C.1 Notavelmente, a regulamentação faz distinções claras para diferentes faixas de canais, reconhecendo as características de propagação distintas do VHF-alto (canais 7-13) e UHF (canais 14-51).1  
Tabela 2: Classificação dos Canais Digitais de TV em Função de suas Características Máximas 1

| Classe | Canais | Máxima Potência ERP (kW) | HMNT (m) | Distância Máxima ao Contorno Protegido (km) |
| :---- | :---- | :---- | :---- | :---- |
| Especial | 7 \- 13 | 16 | 150 | 65,6 |
|  | 14 \- 46 | 80 | 150 | 58,0 |
|  | 47 \- 51 | 100 | 150 | 58,0 |
| A | 7 \- 13 | 1,6 | 150 | 47,9 |
|  | 14 \- 51 | 8 | 150 | 42,5 |
| B | 7 \- 13 | 0,16 | 150 | 32,3 |
|  | 14 \- 51 | 0,8 | 150 | 29,1 |
| C | 7 \- 13 | 0,016 | 150 | 20,2 |
|  | 14 \- 51 | 0,08 | 150 | 18,1 |

Fonte: Baseado nos Atos da ANATEL sobre o Plano Básico de Distribuição de Canais de Televisão Digital (PBTVD) 1  
Esta tabela oferece uma visão clara da estratégia regulatória. Observe a "Classe Especial": para atingir uma distância de contorno similar (aproximadamente 58-65 km), a ANATEL permite uma ERP de 16 kW em VHF-alto (canais 7-13), mas permite 80 kW (5 vezes mais potência) na faixa principal de UHF (canais 14-46).1  
Isso ocorre porque as frequências UHF sofrem significativamente mais atenuação (perda de sinal) devido a obstruções, penetração em edifícios e distância, em comparação com as frequências VHF. O regulador permite uma ERP substancialmente maior em UHF para compensar essa perda de propagação. Isso reforça a conclusão da seção de FM: o objetivo final da ANATEL não é limitar a ERP por si só, mas sim gerenciar a *distância de cobertura* e o *alcance da interferência*, garantindo o uso eficiente do espectro.1

## **II. Definição dos Limiares de Recepção e Contornos de Serviço**

A definição de "limiares de recepção" é uma das partes mais críticas e frequentemente mal interpretadas do planejamento de radiodifusão. A consulta do usuário solicita os limiares para FM e TV Digital. Para responder com precisão, é imperativo primeiro dissecar a ambiguidade do termo, distinguindo entre o limiar de planejamento (regulação) e o limiar de sensibilidade (hardware).

### **A. O Contorno Protegido vs. O Limiar de Recepção: Uma Distinção Crítica**

No contexto da engenharia de RF e da regulação da ANATEL, existem dois limiares fundamentalmente diferentes:

1. **Limiar de Planejamento (O Contorno Protegido):** Este é um valor de intensidade de campo (em dBµV/m) definido pelo regulador (ANATEL). Exemplos incluem 66 dBµV/m para FM.2 Este valor é propositalmente *alto*. Ele não representa o ponto onde o rádio para de funcionar; ele representa o limite *legal* da área de serviço primária.8 Dentro deste contorno, a emissora tem proteção garantida pela ANATEL contra interferência objetável de outras estações (co-canais ou canais adjacentes).5 O valor elevado inclui uma margem de segurança (link margin) significativa para compensar desvanecimento do sinal (fading) e perdas de penetração em edificações.  
2. **Limiar de Sensibilidade (Recepção Real):** Este é o nível de sinal *mínimo* que um dispositivo receptor (um rádio de carro ou um receptor de TV digital) requer em seus terminais de antena para demodular o sinal com sucesso (ou seja, com qualidade mínima aceitável). Este valor é tipicamente *baixo* e é definido por normas técnicas de hardware (como as da ABNT) e pela física do receptor. Por exemplo, 32 dBµV/m para TV Digital.9

A confusão entre esses dois números leva a equívocos. O limiar de planejamento da ANATEL (66 dBµV/m) é alto para garantir que, na borda da área de serviço licenciada, o sinal entregue ao receptor esteja *muito acima* do limiar de sensibilidade do hardware (32 dBµV/m). Essa diferença (a margem) é o que permite a recepção interna, móvel e em condições não ideais.

### **B. Limiar para Rádio FM Analógico**

Para o serviço de Rádio FM comercial (excluindo Rádio Comunitária), o limiar de planejamento é claro e consistentemente definido pela ANATEL:

* **Contorno Protegido (Planejamento): $66 \\text{ dBµV/m}$**

Este valor é explicitamente estipulado no Ato nº 4174 2 e em regulamentações anteriores.5 É este o valor de intensidade de campo que deve ser usado como alvo nos cálculos do modelo de propagação (ITU-R P.1546) para determinar a "Distância Máxima ao Contorno Protegido" listada na Tabela 1\.2  
Embora outros valores possam ser mencionados para contextos específicos (como 54 dBµV/m para área rural em alguns documentos 10), o valor de 66 dBµV/m é o padrão-ouro para o *contorno protegido* usado na classificação e planejamento de canais de FM.  
Como ponto de comparação, o serviço de Radiodifusão Comunitária (RadCom) opera com regras diferentes. Para RadCom, o contorno de serviço é definido por um limiar muito mais alto, de **91 dBµV/m**, refletindo seu propósito de cobertura local e alta qualidade de sinal em uma área restrita.2

### **C. Limiares para TV Digital (ISDB-Tb)**

Para a TV Digital, a situação é mais complexa e demonstra perfeitamente a distinção entre os dois tipos de limiares.

* Limiar de Sensibilidade (Recepção Real): $32 \\text{ dBµV/m}$  
  Este valor é derivado das normas técnicas de hardware. A Norma ABNT NBR 15604:2007 (Televisão digital terrestre — Receptores) especifica a sensibilidade mínima de um receptor (para recepção full-seg) como sendo menor ou igual a \-77 dBm.9  
  Em sistemas de TV, que usam impedância de 75 ohms, o próprio documento da ABNT fornece a conversão: $-77 \\text{ dBm} \\approx 32 \\text{ dBuV}$ (ou dBµV/m, assumindo uma antena com fator 0 dB/m).9  
  Este é o "limiar do penhasco digital" (digital cliff): o nível de sinal mínimo absoluto que o receptor necessita para travar o sinal e exibir uma imagem perfeita. Abaixo disso, a recepção cessa abruptamente.  
* Contorno de Planejamento (ANATEL):  
  Diferentemente do FM, os Atos da ANATEL para TV Digital (como o Ato nº 9751 ou 3114\) não especificam um único valor de dBµV/m para o contorno protegido. Em vez disso, a Tabela 2 1 define diretamente a Distância Máxima ao Contorno Protegido (km) com base na Classe e na ERP.  
  Outros documentos normativos da ANATEL e da ABNT (como o NBR 15604 12\) mencionam a divisão da área de serviço em "Contornos 1, 2 e 3", baseados em diferentes intensidades de campo.12 Por exemplo, valores como 43 dBµV/m ou 51 dBµV/m são citados em estudos de planejamento como limiares para diferentes qualidades de serviço (ex: recepção interna vs. externa).13  
  Isso implica que, para TV Digital, o processo de planejamento é muitas vezes "invertido": a ANATEL define a distância máxima do contorno para uma classe (ex: 58,0 km para Classe Especial UHF 1); o engenheiro deve então usar o modelo de propagação para provar que sua configuração de ERP/HAAT atinge os limiares de planejamento (ex: 43 dBµV/m) dentro das áreas-alvo (como os 70% dos setores censitários urbanos do município).1

Em resumo, para TV Digital, o limiar de *hardware* é **32 dBµV/m** 9, mas o *planejamento* do serviço é feito usando limiares significativamente mais altos (como 43 ou 51 dBµV/m) para garantir uma margem robusta acima do penhasco digital, permitindo a recepção interna.

### **D. A Estatística por Trás dos Contornos: E(50,50) vs. E(50,10)**

Os limiares de intensidade de campo não são valores absolutos e constantes no espaço ou no tempo. O sinal de rádio flutua devido ao desvanecimento (fading) e variações de local para local ( sombreamento). Portanto, os limiares são definidos estatisticamente.

* Contorno Protegido (Serviço): $E(50,50)$  
  A regulamentação da ANATEL (como a Resolução 546\) e as normas ABNT são explícitas: "A curva E(50,50)... é utilizada para calcular as distâncias ao Contorno Protegido".12  
  $E(50,50)$ significa que o valor do campo (ex: 66 dBµV/m para FM) é excedido em 50% dos locais (variabilidade espacial) durante 50% do tempo (variabilidade temporal). Este é o padrão mediano, usado para definir a área de serviço onde se espera que a recepção funcione na maioria das vezes, na maioria dos lugares.  
* Contorno Interferente: $E(50,10)$  
  Para o cálculo de interferência (o sinal indesejado de outra estação), a regra é mais rigorosa. A mesma Resolução 546 estipula que "a curva E(50,10)... é utilizada para o cálculo dos sinais interferentes".14  
  $E(50,10)$ significa que o sinal interferente só pode exceder o limiar de interferência em 10% do tempo (em 50% dos locais).

O sistema de planejamento é projetado para que o sinal de serviço desejado ($E(50,50)$) seja robusto na maior parte do tempo, enquanto o sinal interferente ($E(50,10)$) seja fraco na maior parte do tempo. A viabilidade de um novo canal é determinada garantindo que a Relação de Proteção (a diferença em dB entre o sinal desejado e o sinal interferente) seja mantida.6 O cálculo de viabilidade 15 verifica se $E\_{desejado}(50,50) \- E\_{interferente}(50,10) \> Relação\_{de\\\_Proteção}$.

## **III. A Metodologia Matemática para Estimativa do Contorno Protegido**

Esta seção aborda o núcleo técnico da consulta: "levantar como é estimado o contorno protegido" e "detalhar essa matematica". A estimativa não é uma fórmula simples, mas um algoritmo complexo baseado em um modelo de propagação empírico adotado internacionalmente.

### **A. O Modelo Padrão: Recomendação ITU-R P.1546**

A ANATEL, em sua regulamentação (como o Ato nº 4174 2), estipula o uso da metodologia da União Internacional de Telecomunicações (UIT), especificamente a **Recomendação ITU-R P.1546**.2 Esta recomendação fornece um "Método para predições ponto-a-área para serviços terrestres na faixa de frequência de 30 MHz a 4.000 MHz".16

* **O que é:** É um modelo de propagação *empírico*. Isso significa que ele não é derivado de primeiros princípios da física (como a equação de espaço livre), mas sim baseado em um vasto conjunto de medições de campo realizadas ao longo de décadas em diferentes terrenos e frequências.19  
* **Formato:** O modelo é apresentado como um conjunto de curvas e tabelas de dados que relacionam a intensidade do campo (em dBµV/m, normalizada para 1 kW ERP) com a distância, a altura da antena (HAAT), a frequência e os percentuais estatísticos (tempo e local).18  
* **Aplicabilidade:** Sua faixa de frequência (30-4000 MHz) cobre perfeitamente o Rádio FM (88-108 MHz) e a TV Digital (VHF 174-216 MHz e UHF 470-698 MHz).  
* **Uso:** É usado para *prever* a intensidade do campo em uma determinada distância do transmissor.20 No nosso caso, é usado "ao contrário": para *encontrar a distância* na qual a intensidade do campo cai para um limiar específico (ex: 66 dBµV/m).

### **B. Entradas Essenciais para o Modelo**

Para executar o cálculo do P.1546 e determinar o contorno, os seguintes dados de entrada são matematicamente essenciais:

1. **Cálculo da Altura Efetiva (HAAT/HNMT):** Conforme detalhado na Seção I.A, este é o primeiro passo matemático. Para o cálculo do *contorno*, que é específico para cada azimute, o HAAT deve ser calculado não como a média de 8 radiais, mas sim como a altura efetiva *específica para cada radial* (ex: 360 radiais) que está sendo calculada.4 O método (média de elevação de 3 km a 16 km) é aplicado individualmente a cada radial.3  
2. **Potência Efetiva Radiada (ERP):** O valor da ERP deve ser expresso em dBk (decibéis relativos a 1 kW). A conversão é $ERP(dBk) \= 10 \\times \\log\_{10}(ERP(kW))$. Por exemplo, uma estação de 50 kW (Classe A1) tem uma ERP de $10 \\times \\log\_{10}(50) \= 17 \\text{ dBk}$.2  
3. **Frequência do Canal ($f$):** A frequência exata da operação (ex: 100,1 MHz para FM, ou 605 MHz para um canal UHF de TV). O modelo P.1546 possui curvas-base para 100 MHz, 600 MHz e 2.000 MHz.18  
4. **Limiar de Contorno Alvo ($E\_{alvo}$):** O valor de intensidade de campo que define o contorno (ex: 66 dBµV/m para FM 2).  
5. **Estatística:** O percentual de tempo e local. Para o contorno protegido, é $E(50,50)$.14

### **C. O Processo de Cálculo Passo a Passo (A "Matemática")**

A "matemática" do P.1546 é um algoritmo de consulta e interpolação, idealmente implementado em software. O processo para encontrar a distância $d$ do contorno em um único azimute é o seguinte:  
Passo 1\. Normalização do Campo Alvo  
As curvas P.1546 são normalizadas para uma ERP de 1 kW (ou 0 dBk).19 Devemos, portanto, ajustar nosso $E\_{alvo}$ para encontrar o valor equivalente na curva de 1 kW. Subtraímos a ERP (em dBk) do campo alvo:  
$$E\_{normalizado} \= E\_{alvo} \- ERP\_{dBk}$$  
*Exemplo (Rádio FM Classe A1):*

* $E\_{alvo} \= 66 \\text{ dBµV/m}$  
* $ERP \= 50 \\text{ kW} \= 17 \\text{ dBk}$  
* $E\_{normalizado} \= 66 \- 17 \= 49 \\text{ dBµV/m}$

O problema matemático agora é: "A que distância $d$, usando o modelo P.1546 para 1 kW, com o HAAT e frequência da estação, o campo previsto é de 49 dBµV/m?"  
Passo 2\. Seleção e Interpolação das Curvas P.1546  
O modelo P.1546 não possui curvas para todas as frequências ou alturas. Ele fornece curvas discretas (ex: $f$ \= 100, 600 MHz; $h$ \= 10, 20, 37.5, 75, 150 m, etc.).18 Devemos interpolar entre essas curvas para encontrar uma "curva virtual" para o HAAT e a frequência exatos da nossa estação.

* Interpolação de Frequência: A interpolação entre as curvas de frequência (ex: 100 MHz e 600 MHz) é logarítmica. Para uma frequência $f$ (ex: 100,1 MHz) entre uma frequência inferior ($f\_{inf}$) e superior ($f\_{sup}$), o campo $E$ em uma dada distância é:

  $$E(f) \= E(f\_{inf}) \+ \[E(f\_{sup}) \- E(f\_{inf})\] \\times \\frac{\\log\_{10}(f / f\_{inf})}{\\log\_{10}(f\_{sup} / f\_{inf})}$$  
* Interpolação de Altura (HAAT): Da mesma forma, a interpolação entre as curvas de altura (ex: $h$ \= 75 m e 150 m) também é logarítmica. Para um HAAT $h$ (ex: 120 m) entre uma altura inferior ($h\_{inf}$) e superior ($h\_{sup}$):

  $$E(h) \= E(h\_{inf}) \+ \[E(h\_{sup}) \- E(h\_{inf})\] \\times \\frac{\\log\_{10}(h / h\_{inf})}{\\log\_{10}(h\_{sup} / h\_{inf})}$$

*Nota:* Para automatizar isso, a Recomendação ITU-R P.1546, em seu Anexo 8 (em versões anteriores) e em arquivos de dados associados, fornece equações polinomiais e coeficientes que representam essas curvas, eliminando a necessidade de interpolação gráfica manual e permitindo a implementação computacional precisa.22  
Passo 3\. Interpolação de Distância (O Problema Inverso)  
Após o Passo 2, temos uma "curva virtual" (ou uma função) que nos dá o $E\_{campo}(d)$ para a frequência e HAAT da nossa estação, assumindo 1 kW ERP.  
Agora, devemos encontrar a distância $d$ onde esta curva cruza nosso $E\_{normalizado}$ (do Passo 1). Matematicamente, estamos resolvendo a equação $f(d) \= E\_{campo}(d) \- E\_{normalizado} \= 0$. Este é um problema de busca de raiz.15  
Na prática, isso é feito por interpolação inversa. O algoritmo:

1. Consulta a tabela de dados P.1546 (já interpolada para $f$ e $h$) e encontra duas distâncias, $d\_1$ e $d\_2$.  
2. Essas distâncias $d\_1$ e $d\_2$ produzem campos $E(d\_1)$ e $E(d\_2)$ que "sanduicham" o nosso $E\_{normalizado}$ (ou seja, $E(d\_1) \> E\_{normalizado} \> E(d\_2)$).  
3. Realiza-se uma interpolação linear (ou log-linear, pois a distância nas curvas é frequentemente em escala logarítmica) entre $(d\_1, E(d\_1))$ e $(d\_2, E(d\_2))$ para encontrar o $d$ exato onde $E(d) \= E\_{normalizado}$.

Passo 4\. Correções de Trajeto (Refinamento)  
O processo acima assume um terreno "médio" (rolling hills). Para trajetos específicos no mundo real, correções são necessárias:

* **Trajetos Mistos (Terra/Água):** Se a radial (o caminho do transmissor ao receptor) cruzar uma combinação de terra e água (oceanos, grandes lagos), a propagação muda. O **Método de Millington** é o procedimento padrão-ouro, adotado pela UIT, para calcular a intensidade do campo em trajetos mistos.23 Ele calcula o campo em ambas as direções (transmissor $\\rightarrow$ receptor e receptor $\\rightarrow$ transmissor) e tira a média, contabilizando a mudança abrupta nas propriedades elétricas (condutividade, permissividade) na fronteira terra-água.23  
* **Obstrução de Terreno (TCA):** Para caminhos curtos (tipicamente \< 15 km), onde o HAAT médio não é representativo, o modelo P.1546 padrão pode falhar. Nesses casos, utiliza-se uma correção baseada no perfil detalhado do terreno, especificamente o **Ângulo de Obstrução do Terreno** (TCA \- Terrain Clearance Angle).24 Isso analisa se o receptor está em linha de visada (LoS) ou obstruído, e aplica um ganho ou perda com base no ângulo de obstrução.

Passo 5\. Geração do Contorno Completo  
O processo descrito (Passos 1-4) calcula a distância do contorno para um único azimute. Para plotar o contorno protegido, este processo é repetido para múltiplas radiais ao redor da torre (ex: 360 radiais, uma para cada grau de 0 a 359).  
Para cada radial, o HAAT *específico daquela radial* é calculado 4, e o perfil do terreno é analisado para correções (Millington, TCA).  
O resultado final é um conjunto de 360 pontos de dados no formato (Azimute, Distância). Esses pontos, quando convertidos de coordenadas polares (com centro na torre) para coordenadas geográficas (Latitude, Longitude), formam os **vértices do polígono do contorno protegido**.

## **IV. Guia de Implementação: Plotagem de Contornos de Cobertura na API do Google Maps**

A etapa final da consulta é como visualizar esse contorno calculado usando a API do Google Maps. A plotagem depende do formato dos dados de saída (um conjunto de vértices vetoriais ou uma imagem raster de cobertura). Existem três métodos principais para realizar esta tarefa.

### **A. Geração de Dados Geoespaciais (Pré-requisito)**

Antes de plotar, os dados do contorno devem ser gerados. Existem duas abordagens principais:

1. **Abordagem 1: Cálculo em Software (ex: Python, Matlab):** Implementar o algoritmo completo da Seção III. O resultado será um $Array$ de 360 (ou mais) objetos de coordenadas $LatLng$, representando os vértices do polígono do contorno.  
2. **Abordagem 2: Ferramentas de Simulação (Radio Mobile, QGIS):** Utilizar software dedicado que já implementa o ITU-R P.1546.  
   * **Radio Mobile:** Um software gratuito e popular para planejamento de rádio.25 O usuário insere os parâmetros da estação (localização, ERP, HAAT, frequência), ele executa o modelo de propagação 26 e pode exportar o resultado (o contorno ou um mapa de cobertura completo) como um arquivo **KML** (Keyhole Markup Language), que é diretamente compatível com o ecossistema Google.27  
   * **QGIS:** Um software de Sistema de Informação Geográfica (SIG) de código aberto.29 Ele pode ser usado para processar dados de saída do Radio Mobile 26 ou usar plugins de propagação para gerar os contornos como *shapefiles* ou KMLs.

### **B. Método 1: Renderização Vetorial com google.maps.Polygon (Plotando a Linha do Contorno)**

Este é o método mais direto se você usou a Abordagem 1 e tem o $Array$ de vértices do contorno.

* **Conceito:** A classe google.maps.Polygon da API do Google Maps é projetada para desenhar uma forma fechada e preenchida no mapa.30 Ela é instanciada passando um $Array$ de coordenadas google.maps.LatLng que definem os caminhos (vértices) da forma.31  
* **Implementação (JavaScript):**  
  JavaScript  
  /\*  
   Assumindo que 'map' é o seu objeto google.maps.Map inicializado  
   e 'contourCoordinates' é o seu Array de 360 objetos google.maps.LatLng  
   calculados na Seção III.  
  \*/

  // Criar o polígono  
  const protectedContour \= new google.maps.Polygon({  
    paths: contourCoordinates,  // O Array de vértices  
    strokeColor: "\#FF0000",      // Cor da linha  
    strokeOpacity: 0.8,         // Opacidade da linha  
    strokeWeight: 2,            // Espessura da linha  
    fillColor: "\#FF0000",        // Cor do preenchimento  
    fillOpacity: 0.25,          // Opacidade do preenchimento  
    map: map                    // O mapa onde o polígono será desenhado  
  });

* **Notas de Implementação:** A API Polygon é robusta; ela fecha automaticamente o polígono conectando o último vértice de volta ao primeiro, portanto, não é necessário repetir o primeiro ponto no final do $Array$.31 Este polígono é um objeto nativo do mapa, sendo leve, responsivo ao zoom e interativo (pode-se adicionar ouvintes de eventos, como 'click' 33).

### **C. Método 2: Sobreposição de Camadas KML com google.maps.KmlLayer**

Este método é o mais eficiente se você usou a Abordagem 2 (Radio Mobile, QGIS) e possui um arquivo .kml ou .kmz.

* **Conceito:** KML é um padrão XML para dados geográficos. A API do Google Maps possui uma classe dedicada, google.maps.KmlLayer, que busca, analisa e renderiza um arquivo KML/KMZ diretamente no mapa.34  
* **Implementação (JavaScript):**  
  JavaScript  
  /\*  
   Assumindo que 'map' é o seu objeto google.maps.Map inicializado.  
  \*/

  // O arquivo KML/KMZ DEVE estar em um servidor web acessível publicamente.  
  const kmlUrl \= "https://www.sua-emissora.com/contornos/estacao\_A1.kml";

  // Criar a camada KML  
  const kmlLayer \= new google.maps.KmlLayer({  
    url: kmlUrl,                // URL para o arquivo KML  
    map: map,                   // O mapa onde a camada será desenhada  
    preserveViewport: false     // 'false' faz o mapa dar zoom/pan para mostrar  
                                // o conteúdo KML automaticamente  
  });

* **Advertência Crítica de Implementação:** A falha mais comum ao usar KmlLayer é que o $kmlUrl$ *não pode ser um arquivo local* (ex: $file:///...$) nem estar em um $localhost$ não acessível pela internet.35 A KmlLayer é processada e renderizada nos servidores do Google. Portanto, o Google deve ser capaz de buscar o arquivo KML a partir do URL fornecido.35  
* **Vantagens:** Este método é extremamente simples de implementar (poucas linhas de código). Além disso, os arquivos KML podem conter muito mais do que apenas polígonos; eles suportam ícones, marcadores (Placemarks), dados HTML em balões de informação e estilos complexos, permitindo uma visualização rica exportada diretamente do software de simulação.34

### **D. Método 3 (Avançado): Sobreposição de Imagem Raster com google.maps.OverlayView**

Este método não plota apenas a linha do contorno, mas sim um *mapa de calor* completo da intensidade do sinal (ex: uma imagem PNG ou GeoTIFF georreferenciada, onde cores diferentes representam diferentes níveis de dBµV/m).

* **Conceito:** A classe google.maps.OverlayView é uma ferramenta poderosa que permite ao desenvolvedor colocar qualquer elemento HTML (como um $div$ contendo uma $img$) em cima do mapa, "ancorado" a coordenadas geográficas (um google.maps.LatLngBounds).36 A API garante que o elemento seja reposicionado e redimensionado corretamente quando o usuário arrasta ou dá zoom no mapa.37  
* **Implementação (Conceitual):**  
  1. O software de simulação (como QGIS ou Radio Mobile) gera a cobertura como uma imagem raster georreferenciada (ex: um GeoTIFF ou um PNG com um arquivo "world").  
  2. O desenvolvedor cria uma classe JavaScript customizada que estende google.maps.OverlayView.36  
  3. No construtor da classe, são passados os limites geográficos da imagem (LatLngBounds) e o URL da imagem.  
  4. No método onAdd(), o desenvolvedor cria os elementos DOM (ex: $document.createElement('div')$ e $document.createElement('img')$) e os anexa ao painel correto do mapa (ex: getPanes().overlayLayer.appendChild(this.div)).36  
  5. No método draw(), o desenvolvedor usa getProjection() para converter os LatLngBounds da imagem em coordenadas de pixel na tela. Em seguida, ele define o tamanho (largura/altura) e a posição (esquerda/topo) do $div$ para que a imagem se alinhe perfeitamente com o mapa subjacente.  
* Esta é a técnica correta e padrão da indústria para sobrepor imagens raster georreferenciadas no Google Maps.38  
* Por que NÃO usar HeatmapLayer?  
  Um erro comum é tentar usar a google.maps.visualization.HeatmapLayer para plotar grades de intensidade de sinal. Esta ferramenta é inadequada para essa tarefa. A HeatmapLayer é projetada para visualizar a densidade de pontos (quantos pontos estão agrupados em uma área).40 Ela não é projetada para renderizar uma grade de valores (onde cada ponto tem um valor de intensidade). O resultado seria visualmente incorreto, mostrando "calor" onde há muitos pontos de dados, e não onde o sinal é forte.42  
  Além disso, a HeatmapLayer da API do Google Maps foi oficialmente depreciada em maio de 2025 e será removida em uma versão futura.40 A própria documentação do Google recomenda o uso de OverlayView ou bibliotecas de terceiros. Portanto, o OverlayView (Método 3\) é a abordagem correta e à prova de futuro para visualização de mapas de calor de sinal.

## **V. Análise Conclusiva e Considerações de Engenharia**

Este relatório dissecou o processo de regulamentação, cálculo e visualização de contornos de radiodifusão no Brasil. A análise revela um sistema coeso onde a regulamentação está intrinsecamente ligada à física da propagação de rádio e às realidades da implementação de software.

### **A. Síntese: A Interdependência do Sistema de Radiodifusão**

Fica demonstrado que a classificação de uma emissora não é um rótulo arbitrário, mas o ponto de partida de uma cadeia causal técnica e regulatória:

1. A **Classe** da estação (ex: A1-FM, Especial-TV) é definida pela ANATEL e dita os limites máximos de operação.1  
2. Esses limites de **ERP/HAAT** são as entradas principais para o modelo de propagação.2  
3. O **Limiar do Contorno Protegido** (ex: 66 dBµV/m para FM) define o valor-alvo que o modelo deve calcular.2  
4. O **Modelo ITU-R P.1546**, usando a estatística **E(50,50)** 14, é o motor matemático que processa as entradas.17  
5. O resultado do cálculo é a **Distância do Contorno** para cada azimute.  
6. Este conjunto de distâncias gera um **polígono vetorial** (coordenadas $LatLng$) ou uma **imagem raster** de cobertura.  
7. Finalmente, esses dados geoespaciais são visualizados na **API do Google Maps** usando os métodos apropriados: google.maps.Polygon 30, google.maps.KmlLayer 34, ou google.maps.OverlayView.36

### **B. Recomendações Técnicas**

* **Para Planejamento de Espectro:** A análise da Tabela 1 (FM) 2 demonstra que o investimento em **HAAT (altura da antena)** é comprovadamente mais eficiente, tanto em termos de custo-benefício quanto de eficiência espectral, para expandir a cobertura do que aumentos brutos de ERP. A relação logarítmica (100x potência para \~6x distância) significa que a potência elevada gera mais interferência e custos de energia para retornos de cobertura decrescentes.  
* **Para Desenvolvimento de Software:** Ao criar ferramentas de visualização de cobertura, a escolha do método da API do Google Maps deve ser orientada pelo tipo de dado.  
  * Para uma visualização simples do **contorno legal** ("passa/não passa"), google.maps.Polygon (para dados brutos) ou google.maps.KmlLayer (para dados de simulação) são ideais e eficientes.30  
  * Para uma análise de **Qualidade de Serviço (QoS)**, que exibe a *gradação* da intensidade do sinal dentro e fora do contorno, a sobreposição de uma imagem raster usando google.maps.OverlayView é a metodologia correta e necessária.36  
* **Para Engenharia de TV Digital:** A disparidade entre o limiar de sensibilidade do receptor (32 dBµV/m 9) e os limiares de planejamento de serviço (ex: 43-51 dBµV/m 13) ressalta a importância crítica da "margem de penhasco digital". A cobertura de TV Digital não deve ser planejada para o limiar mínimo de recepção, mas sim para um nível de sinal robusto que supere as perdas de penetração em edificações, garantindo a recepção interna.

#### **Referências citadas**

1. AGÊNCIA NACIONAL DE TELECOMUNICAÇÕES ATO Nº 3114, DE ..., acessado em novembro 14, 2025, [https://camarablu.sc.gov.br/images/upload/1702509189657a3a85e45b0.pdf](https://camarablu.sc.gov.br/images/upload/1702509189657a3a85e45b0.pdf)  
2. Ato nº 4174, de 10 de junho de 2021 (REVOGADO) \- Anatel, acessado em novembro 14, 2025, [https://informacoes.anatel.gov.br/legislacao/atos-de-requisitos-tecnicos-de-gestao-do-espectro/2021/1569-ato-4174](https://informacoes.anatel.gov.br/legislacao/atos-de-requisitos-tecnicos-de-gestao-do-espectro/2021/1569-ato-4174)  
3. 47 CFR 24.53 \-- Calculation of height above average terrain (HAAT). \- eCFR, acessado em novembro 14, 2025, [https://www.ecfr.gov/current/title-47/chapter-I/subchapter-B/part-24/subpart-C/section-24.53](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-B/part-24/subpart-C/section-24.53)  
4. Calculation of Effective antenna heights using SRTM1 and GDEM v3 databases \- ITU, acessado em novembro 14, 2025, [https://www.itu.int/SRTM3/](https://www.itu.int/SRTM3/)  
5. AGÊNCIA NACIONAL DE TELECOMUNICAÇÕES ATO Nº 3115, DE 10 DE JUNHO DE 2020 REQUISITOS TÉCNICOS DE CONDIÇÕES DE USO DE RADIO \- ABERT, acessado em novembro 14, 2025, [http://www.abert.org.br/pdf/SEI\_ANATEL\_5643153\_Ato.pdf](http://www.abert.org.br/pdf/SEI_ANATEL_5643153_Ato.pdf)  
6. Ato nº 9751, de 06 de julho de 2022 \- Anatel \- Agência Nacional de Telecomunicações, acessado em novembro 14, 2025, [https://informacoes.anatel.gov.br/legislacao/atos-de-requisitos-tecnicos-de-gestao-do-espectro/2022/1688-ato-9751](https://informacoes.anatel.gov.br/legislacao/atos-de-requisitos-tecnicos-de-gestao-do-espectro/2022/1688-ato-9751)  
7. Ato nº 3114, de 10 de junho de 2020 (REVOGADO) \- Anatel, acessado em novembro 14, 2025, [https://www.anatel.gov.br/legislacao/atos-de-requisitos-tecnicos-de-gestao-do-espectro/2020/1490-ato-3114](https://www.anatel.gov.br/legislacao/atos-de-requisitos-tecnicos-de-gestao-do-espectro/2020/1490-ato-3114)  
8. Anatel \- Ato Nº 3116, de 10 de Junho de 2020 | PDF | Radiodifusão | Antena (rádio) \- Scribd, acessado em novembro 14, 2025, [https://pt.scribd.com/document/508125925/Anatel-Ato-n%C2%BA-3116-de-10-de-junho-de-2020](https://pt.scribd.com/document/508125925/Anatel-Ato-n%C2%BA-3116-de-10-de-junho-de-2020)  
9. Ajuste do Nível de Sinal \- teleco.com.br, acessado em novembro 14, 2025, [https://www.teleco.com.br/tutoriais/tutorialanttvd/pagina\_4.asp](https://www.teleco.com.br/tutoriais/tutorialanttvd/pagina_4.asp)  
10. Rádio Digital no Brasil, acessado em novembro 14, 2025, [https://legis.senado.leg.br/sdleg-getter/documento/download/5a0b0075-0139-456a-a299-b06f2db008c3](https://legis.senado.leg.br/sdleg-getter/documento/download/5a0b0075-0139-456a-a299-b06f2db008c3)  
11. Ato nº 8104, de 10 de junho de 2022 \- Anatel \- Agência Nacional de Telecomunicações, acessado em novembro 14, 2025, [https://informacoes.anatel.gov.br/legislacao/atos-de-requisitos-tecnicos-de-gestao-do-espectro/2022/1687-ato-8104](https://informacoes.anatel.gov.br/legislacao/atos-de-requisitos-tecnicos-de-gestao-do-espectro/2022/1687-ato-8104)  
12. ESTUDO DE VIABILIDADE TÉCNICA PARA INCLUSÃO DE SERVIÇO DE RADIODIFUSÃO DE TV DIGITAL \- BDM UnB, acessado em novembro 14, 2025, [https://bdm.unb.br/bitstream/10483/28120/1/2019\_GlaucioFernandoBeserraPinheiro\_tcc.pdf](https://bdm.unb.br/bitstream/10483/28120/1/2019_GlaucioFernandoBeserraPinheiro_tcc.pdf)  
13. UNIVERSIDADE DE SÃO PAULO ESCOLA POLITÉCNICA GUNNAR BEDICKS JUNIOR SINTONIZADOR-DEMODULADOR PARA O SISTEMA BRASILEIRO DE TV DI, acessado em novembro 14, 2025, [https://teses.usp.br/teses/disponiveis/3/3142/tde-26092008-101922/publico/2008\_GBJR\_Sintonizador\_Demodulador\_para\_o\_SBTVD.pdf](https://teses.usp.br/teses/disponiveis/3/3142/tde-26092008-101922/publico/2008_GBJR_Sintonizador_Demodulador_para_o_SBTVD.pdf)  
14. Resolução nº 546, de 1º de setembro de 2010 (REVOGADA) \- Anatel, acessado em novembro 14, 2025, [https://informacoes.anatel.gov.br/legislacao/component/content/article/25-resolucoes/2010/14-resolucao-546](https://informacoes.anatel.gov.br/legislacao/component/content/article/25-resolucoes/2010/14-resolucao-546)  
15. Análise Numérica da Ferramenta SIGANATEL para o Cálculo de Viabilidade de Canais de FM \- Biblioteca da SBrT, acessado em novembro 14, 2025, [https://biblioteca.sbrt.org.br/articlefile/3106.pdf](https://biblioteca.sbrt.org.br/articlefile/3106.pdf)  
16. P.1546 : Method for point-to-area predictions for terrestrial services in the frequency range 30 MHz to 4 000 MHz \- ITU, acessado em novembro 14, 2025, [https://www.itu.int/rec/r-rec-p.1546/en](https://www.itu.int/rec/r-rec-p.1546/en)  
17. Avaliação Empírica de Recomendações da ITU-R para Propagação nas Faixas de TV e FM \- Biblioteca da SBrT, acessado em novembro 14, 2025, [https://biblioteca.sbrt.org.br/articlefile/4740.pdf](https://biblioteca.sbrt.org.br/articlefile/4740.pdf)  
18. RECOMMENDATION ITU-R P.1546-6( \- Method for point-to-area predictions for terrestrial services in the frequency range 30 MHz, acessado em novembro 14, 2025, [https://www.itu.int/dms\_pubrec/itu-r/rec/p/R-REC-P.1546-6-201908-I\!\!PDF-E.pdf](https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.1546-6-201908-I!!PDF-E.pdf)  
19. The Planning and Optimisation of DVB-H Radio Network \- Aaltodoc, acessado em novembro 14, 2025, [https://aaltodoc.aalto.fi/bitstreams/109e0555-9ed0-4fbf-9470-e63df99e462b/download](https://aaltodoc.aalto.fi/bitstreams/109e0555-9ed0-4fbf-9470-e63df99e462b/download)  
20. ANÁLISE COMPARATIVA DE REDES NEURAIS NA PREVISÃO DE INTENSIDADE DE SINAL DE TELEVISÃO DIGITAL NA FAIXA DE UHF \- Repositório Institucional \- Universidade Federal de Uberlândia, acessado em novembro 14, 2025, [https://repositorio.ufu.br/bitstream/123456789/41343/1/An%C3%A1liseComparativadeRedes.pdf](https://repositorio.ufu.br/bitstream/123456789/41343/1/An%C3%A1liseComparativadeRedes.pdf)  
21. RECOMMENDATION ITU-R P.1546-3 Method for point-to-area predictions for terrestrial services in the frequency range 30 MHz to 3000 MHz, acessado em novembro 14, 2025, [https://www.itu.int/dms\_pubrec/itu-r/rec/p/R-REC-P.1546-3-200711-S\!\!PDF-E.pdf](https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.1546-3-200711-S!!PDF-E.pdf)  
22. RECOMMENDATION ITU-R P.1546-1 \- Method for point-to-area predictions for terrestrial services in the frequency range 30 MHz to 3, acessado em novembro 14, 2025, [https://www.itu.int/dms\_pubrec/itu-r/rec/p/R-REC-P.1546-1-200304-S\!\!PDF-E.pdf](https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.1546-1-200304-S!!PDF-E.pdf)  
23. I Modelo de Propagação de Campo Elétrico para TV Digital em Percursos Mistos do tipo cidade-rio na Região Amazônica, acessado em novembro 14, 2025, [https://repositorio.ufpa.br/bitstreams/37aeff03-f8f8-46f9-8601-0cef3cdd857a/download](https://repositorio.ufpa.br/bitstreams/37aeff03-f8f8-46f9-8601-0cef3cdd857a/download)  
24. (PDF) Comparison of UHF Measurements with the Propagation Model of Recommendation ITU-R P.1546 \- ResearchGate, acessado em novembro 14, 2025, [https://www.researchgate.net/publication/295795806\_Comparison\_of\_UHF\_Measurements\_with\_the\_Propagation\_Model\_of\_Recommendation\_ITU-R\_P1546](https://www.researchgate.net/publication/295795806_Comparison_of_UHF_Measurements_with_the_Propagation_Model_of_Recommendation_ITU-R_P1546)  
25. Radio Mobile Tutorial EGTNA8 \- Revc \- 291113 | PDF | Antena (rádio) | Google \- Scribd, acessado em novembro 14, 2025, [https://pt.scribd.com/document/214812772/Radio-Mobile-Tutorial-EGTNA8-revC-291113](https://pt.scribd.com/document/214812772/Radio-Mobile-Tutorial-EGTNA8-revC-291113)  
26. Monografia PHILIPE MANOEL RAMOS PINHEIRO PDF-A.pdf, acessado em novembro 14, 2025, [https://repositorio.uema.br/bitstream/123456789/964/3/Monografia%20PHILIPE%20MANOEL%20RAMOS%20PINHEIRO%20PDF-A.pdf](https://repositorio.uema.br/bitstream/123456789/964/3/Monografia%20PHILIPE%20MANOEL%20RAMOS%20PINHEIRO%20PDF-A.pdf)  
27. Import units \- Radio Mobile \- RF propagation simulation software, acessado em novembro 14, 2025, [http://radiomobile.pe1mew.nl/?How\_to\_\_\_Work\_with\_Google\_Earth\_\_\_Import\_units](http://radiomobile.pe1mew.nl/?How_to___Work_with_Google_Earth___Import_units)  
28. Radio Mobile \- RF propagation simulation software \- Import coverage, acessado em novembro 14, 2025, [http://radiomobile.pe1mew.nl/?How\_to\_\_\_Work\_with\_Google\_Earth\_\_\_Import\_coverage...](http://radiomobile.pe1mew.nl/?How_to___Work_with_Google_Earth___Import_coverage...)  
29. CÁLCULO DA ÁREA DE COBERTURA DE SINAL DE RADIOFREQUÊNCIA UTILIZANDO QGIS A PARTIR DE DADOS ADVINDOS DO RADIO MOBILE \- UEMA, acessado em novembro 14, 2025, [https://marandu.uema.br/software/calculo-da-area-de-cobertura-de-sinal-de-radiofrequencia-utilizando-qgis-a-partir-de-dados-advindos-do-radio-mobile/](https://marandu.uema.br/software/calculo-da-area-de-cobertura-de-sinal-de-radiofrequencia-utilizando-qgis-a-partir-de-dados-advindos-do-radio-mobile/)  
30. Polygons | Maps JavaScript API \- Google for Developers, acessado em novembro 14, 2025, [https://developers.google.com/maps/documentation/javascript/reference/polygon](https://developers.google.com/maps/documentation/javascript/reference/polygon)  
31. Shapes and lines | Maps JavaScript API \- Google for Developers, acessado em novembro 14, 2025, [https://developers.google.com/maps/documentation/javascript/shapes](https://developers.google.com/maps/documentation/javascript/shapes)  
32. Simple Polygon | Maps JavaScript API \- Google for Developers, acessado em novembro 14, 2025, [https://developers.google.com/maps/documentation/javascript/examples/polygon-simple](https://developers.google.com/maps/documentation/javascript/examples/polygon-simple)  
33. Draw polygon using mouse on google maps \- Stack Overflow, acessado em novembro 14, 2025, [https://stackoverflow.com/questions/2325670/draw-polygon-using-mouse-on-google-maps](https://stackoverflow.com/questions/2325670/draw-polygon-using-mouse-on-google-maps)  
34. KML and GeoRSS Layers | Maps JavaScript API \- Google for Developers, acessado em novembro 14, 2025, [https://developers.google.com/maps/documentation/javascript/kmllayer](https://developers.google.com/maps/documentation/javascript/kmllayer)  
35. Adding Kml Layer to google map \- Stack Overflow, acessado em novembro 14, 2025, [https://stackoverflow.com/questions/10027350/adding-kml-layer-to-google-map](https://stackoverflow.com/questions/10027350/adding-kml-layer-to-google-map)  
36. Custom Overlays | Maps JavaScript API \- Google for Developers, acessado em novembro 14, 2025, [https://developers.google.com/maps/documentation/javascript/customoverlays](https://developers.google.com/maps/documentation/javascript/customoverlays)  
37. Custom Overlays | Maps JavaScript API \- Google for Developers, acessado em novembro 14, 2025, [https://developers.google.com/maps/documentation/javascript/examples/overlay-simple](https://developers.google.com/maps/documentation/javascript/examples/overlay-simple)  
38. How to overlay a raster image type with Google Maps API? \- Stack Overflow, acessado em novembro 14, 2025, [https://stackoverflow.com/questions/74385622/how-to-overlay-a-raster-image-type-with-google-maps-api](https://stackoverflow.com/questions/74385622/how-to-overlay-a-raster-image-type-with-google-maps-api)  
39. How to use a .tpk or GeoTiff file as a Google Maps Overlay \- GIS StackExchange, acessado em novembro 14, 2025, [https://gis.stackexchange.com/questions/367719/how-to-use-a-tpk-or-geotiff-file-as-a-google-maps-overlay](https://gis.stackexchange.com/questions/367719/how-to-use-a-tpk-or-geotiff-file-as-a-google-maps-overlay)  
40. Heatmap Layer | Maps JavaScript API \- Google for Developers, acessado em novembro 14, 2025, [https://developers.google.com/maps/documentation/javascript/heatmaplayer](https://developers.google.com/maps/documentation/javascript/heatmaplayer)  
41. Heatmap | Overview | ArcGIS Maps SDK for JavaScript \- Esri Developer, acessado em novembro 14, 2025, [https://developers.arcgis.com/javascript/latest/visualization/high-density-data/heatmap/](https://developers.arcgis.com/javascript/latest/visualization/high-density-data/heatmap/)  
42. How can i display signal strength on maps api? : r/webdev \- Reddit, acessado em novembro 14, 2025, [https://www.reddit.com/r/webdev/comments/1lw9dnc/how\_can\_i\_display\_signal\_strength\_on\_maps\_api/](https://www.reddit.com/r/webdev/comments/1lw9dnc/how_can_i_display_signal_strength_on_maps_api/)  
43. Heatmaps | Maps JavaScript API \- Google for Developers, acessado em novembro 14, 2025, [https://developers.google.com/maps/documentation/javascript/reference/visualization](https://developers.google.com/maps/documentation/javascript/reference/visualization)