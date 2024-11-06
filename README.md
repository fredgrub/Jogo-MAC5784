# Projeto da disciplina MAC5784

## Instalação & Uso

O jogo está sendo desenvolvido na versão 3.11.10 do Python e de desenvolvimento do Arcade. As dependências podem ser instaladas através do arquivo `requirements.txt` executando o comando:

```bash
python -m pip install -r requirements.txt
```

(Execute o comando acima preferencialmente em um ambiente virtual).

O jogo pode ser executado, uma vez que o ambiente virtual esteja ativado, através do comando:

```bash
python game.py
```

## Terceira Entrega

A terceira entrega do projeto adiciona diversos elementos visuais e modifica a dinâmica do jogo para permitir a implementação de agentes sociais. O jogo agora ocorre em tempo real, em vez de ser baseado em turnos. As culturas possuem pontos de vida (HP) e crescem em estágios que levam certo tempo para se completarem.

O jogo inclui uma dinâmica de múltiplas pragas, cujo objetivo é consumir totalmente o HP das culturas. A quantidade de pragas que podem coexistir varia conforme o total de culturas consumidas. As pragas só podem se mover para culturas adjacentes do mesmo tipo de sua preferência. Caso não haja movimentos válidos, elas morrem. Quando uma cultura é completamente consumida, o solo se desgasta, tornando-se inutilizável.

Quando as pragas estão em culturas vizinhas, elas cooperam entre si, aumentando seu poder de consumo. Essa dinâmica incorpora uma esfera social entre os agentes, conforme discutido em aula. Além disso, se o jogador adotar uma estratégia de policultura, as pragas não conseguem se espalhar, destacando a importância ecológica desse tipo de prática e alinhando-se aos Objetivos de Desenvolvimento Sustentável (ODS) de uma agricultura sustentável.

O mecanismo de cura agora remove a praga da cultura atual. Quando não há pragas no jogo, elas podem reaparecer após um intervalo de tempo e se espalhar até o limite máximo permitido de pragas.

Esta versão passou por mudanças drásticas, pois precisei trocar de computador, e o novo sistema operacional tinha problemas com a versão anterior do Arcade. Foi necessário atualizar para a versão de desenvolvimento, que já contava com a correção do erro, mas que trouxe modificações na interface de várias funções, o que quebrou o jogo anterior. Gastei um bom tempo resolvendo isso.

A nova versão do Arcade está listada no arquivo `requirements.txt` e pode ser instalada da mesma forma. Certifique-se de estar usando a versão atualizada, pois o código não funciona na versão anterior.

Não consegui incluir instruções completas de jogo nesta entrega, então aqui está um mini tutorial: Para plantar e colher, basta clicar com o botão esquerdo do mouse. Para curar, use o botão direito. Você pode alterar a cultura a ser plantada com as teclas 1 e 2. A barra de espaço exibe os detalhes das culturas e das pragas.

As ilustrações utilizadas são livres de copyright e estão sob licensas permissivas. Todos os créditos vão para os ilustradores. Mais detalhes nos links abaixo:

- Sprite da praga: https://opengameart.org/content/admurins-insect-items
- Sprites do terreno: https://opengameart.org/content/lpc-farming-tilesets-magic-animations-and-ui-elements
- Sprites das culturas: https://opengameart.org/content/lpc-crops

## Segunda Entrega

Na segunda entrega, o projeto passou por mudanças drásticas que trouxeram melhorias significativas para o jogo. A experiência se tornou mais interativa e estratégica em comparação com a versão inicial. O jogo evoluiu de uma simulação básica para um simulador de fazenda mais complexo, onde o jogador assume o papel de fazendeiro com interações diretas no tabuleiro. Além disso, foi introduzido um mecanismo de fim de jogo: se o dinheiro do jogador acabar, o jogo termina. Essa mudança trouxe um objetivo claro ao jogador, aprimorando o design geral.

Em termos de arquitetura de código, esse foi o aspecto que mais sofreu alterações. A primeira versão padecia de uma otimização precoce e era mais complexa do que o necessário, o que dificultou a introdução de elementos do Python Arcade, como a manipulação de sprites. Na segunda versão, decidi focar nas funcionalidades, deixando de lado, temporariamente, o meu lado de desenvolvedor de software. O código permanece bem estruturado, mas testes automatizados e a modularização foram deixados de lado num primeiro momento.

Uma das principais mudanças foi a introdução de novos tipos de culturas, como milho e soja. Cada cultura possui estágios de crescimento e custos associados à plantação, o que exige decisões estratégicas por parte do jogador, considerando seus objetivos e os recursos disponíveis. O jogador pode alternar entre os tipos de cultura utilizando as teclas exibidas no menu superior. O clique esquerdo do mouse realiza a ação de plantar, enquanto o clique direito executa outras ações, como curar e colher culturas prontas. Nesta nova implementação, o conceito de plantações mortas foi removido, e as plantações são representadas por círculos no centro de cada tile.

Outra mudança importante foi a implementação de um sistema de pragas que afeta culturas específicas. Atualmente, a praga pode infectar qualquer cultura que cruze, mas persegue apenas um tipo de plantação. As culturas podem ser curadas a um custo financeiro, e o jogador precisa monitorar suas plantações para decidir se vale a pena investir recursos na cura, levando em consideração os custos. A praga se movimenta com base em uma heurística simples que calcula qual a cultura mais próxima (o tamanho do tabuleiro permite essa abordagem). A infecção é representada por um círculo vermelho ao redor da cultura infectada.

Essas adições tornam o jogo mais estratégico e funcional, com a diversidade de culturas e a preferência da praga criando o terreno ideal para a próxima etapa: a implementação de um mecanismo de policultura para proteger as plantações contra a praga que poderá se reproduzir.

## Primeira Entrega

Esta primeira entrega apresenta uma versão simplificada do projeto proposto anteriormente. O ambiente, representado por uma fazenda, é modelado como uma grade 2D, onde cada célula possui um estado específico indicado por cores distintas. O agente, que representa o fazendeiro, é visualizado como uma esfera. A implementação atual não inclui interações com o usuário e pode ser encontrada nos arquivos `src/environment.py`, `src/agent.py` e `main.py`.

As células da grade podem assumir quatro estados diferentes, definidos em `src/tile_status.py`:
1. `EMPTY`: Solo fértil, pronto para plantio
2. `WAIT`: Plantio em fase de crescimento
3. `READY`: Plantio maduro, pronto para colheita
4. `DEAD`: Solo degradado, impróprio para cultivo

O agente possui um conjunto de ações disponíveis, definidas em `src/action.py`:
- Movimentação: Deslocamento para células adjacentes (cima, baixo, esquerda, direita)
- Plantio: Semear em solo fértil
- Colheita: Recolher plantio maduro

O processo decisório do agente é implementado no método `get_action()` (em `src/agent.py`), que segue a seguinte lógica:

1. Verifica o estado da célula atual:
   - Se for `READY`, executa a ação de colheita (`HARVEST`).
   - Caso contrário, prossegue para o próximo passo.

2. Analisa as células vizinhas em busca de plantios prontos para colheita:
   - Se encontrar, move-se para a célula correspondente.
   - Se não encontrar, continua para o próximo passo.

3. Examina o estado da célula atual:
   - Se for `EMPTY`, realiza a ação de plantio (`PLANT`).
   - Caso contrário, executa um movimento aleatório para uma célula adjacente disponível.

Este algoritmo prioriza a colheita de plantios maduros, seguida pelo plantio em solos férteis, e por fim, a exploração do ambiente através de movimentos aleatórios quando não há ações produtivas imediatas disponíveis.

O sistema opera em ciclos de um segundo, nos quais o agente toma suas decisões e o ambiente evolui. A cada ciclo, as células do ambiente têm a possibilidade de mudar de estado:
- Células em estado `WAIT` têm 25% de chance de evoluir para `READY`, indicando que o plantio amadureceu e está pronto para colheita.
- Células em estado `READY` têm 10% de chance de se degradar para `DEAD`, representando a deterioração do plantio não colhido.

## Entrega Zero

O projeto tem como objetivo desenvolver um jogo (prova de conceito) com agentes inteligentes, abordando a temática dos Objetivos de Desenvolvimento Sustentável (ODSs) da ONU. A proposta inicial era um jogo de construção de cidades, inspirado no SimCity, com foco na sustentabilidade. A mecânica contemplaria 3 ODSs: saúde e bem-estar (ODS 3), cidades e comunidades sustentáveis (ODS 11) e ação contra a mudança global do clima (ODS 13). A população reagiria às decisões do jogador, expressando satisfação ou insatisfação com base no atendimento de suas necessidades.

### Nova Proposta e Justificativa

A complexidade de implementação de um jogo de construção de cidades motivou a busca por uma alternativa mais viável. A nova proposta é um jogo de agricultura baseado em turnos, onde o jogador controla indiretamente um agricultor que planta, colhe e cuida de sua plantação. Suas ações impactam o ambiente, podendo levar a problemas como esgotamento do solo, poluição da água e desastres naturais. Essa abordagem aborda os ODSs 2 (fome zero e agricultura sustentável), 6 (água potável e saneamento), 13 (ação contra a mudança global do clima) e 15 (vida terrestre). O agricultor, modelado como um agente inteligente, busca maximizar suas reservas de alimentos. Ele avalia as ações disponíveis (plantar, colher, mover) com base no benefício percebido para alcançar seu objetivo. Suas decisões são influenciadas pelo estado do ambiente (fertilidade do solo, recursos disponíveis) e seu conhecimento sobre esses fatores.