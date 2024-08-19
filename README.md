# Descrição

O objetivo da aplicação é o de gerar e verificar assinaturas seguindo o esquema MTSS, em que é possível localizar modificações feitas no documento assinado até certo ponto. Para isso, o arquivo é separado em blocos, e até `d` blocos podem ser modificados conforme a estrutura gerada para a assinatura. O DOI do artigo original é `10.1007/978-3-030-35423-7_2`.

# Utilização

Submódulos: liboqs, liboqs-python

Dependências: Python 3.10, pycryptodome, galois, pytest, sympy, liboqs-python

## Experimentos para artigo (SBSeg 2024)

O artigo que remete à performance obtida do trabalho original sobre o MTSS foi aceito para o SBSeg 2024. Como o artigo ainda não tem um DOI, não foi colocado no repositório. Para a realização dos experimentos, foram utilizados os seguintes scripts:

Para os testes de performance de assinatura (Sig), verificação (Ver) e localização (Ver, com |I| = 1), tanto com esquemas RAW, quanto utilizando o framework MTSS (Table 1 e Table 3), é executado o arquivo `tests/multiple_performance_signature.py`. Nele, são executados 100 iterações e feito um arquivo onde são colocados os tempos de execução para cada iteração para cada esquema de assinatura e função de hash, e operação executada (conforme explicado anteriormente). Estes arquivos de performance foram postos em `data/benchmark`. Para análise desses resultados, ou seja, para tirar a média e o seu desvio padrão correspondente, foi utilizado o script `data/analyze_benchmark.py`; seu output é o csv `data/benchmark-analysis-time.csv`.

O gráfico de performance do algoritmo de divisão de blocos (DivideBlocks), ou seja, Figure 2a, foi feito utilizando o script `blocks_test_script.py`. Para o gráfico de criação de CFFs utilizando construção polinomial, ou seja, Figure 2b, foi utilizado o script `test_cff.py`. Para o gráfico de performance entre os estágios de `pre-sign` e `sign`, ou seja, Figure 3, foi utilizado o script `performance_signature.py` (por 100 iterações); o resultado foi colocado em `data/performance-pre-sign-sign.txt`.

Para outros testes, foram executados os scripts, manualmente, `benchmark.sh` e `benchmark_batch.sh`.

# Utilização dos scripts em geral

## Geração de chaves

A aplicação aceita a utilização de chaves PKCS#1 ou Ed25519, e novas chaves podem ser geradas com os comandos abaixo. O resultado do script será um par de arquivos de nome ```{caminho das chaves}_priv.pem``` e ```{caminho das chaves}_pub.pem```, para a chave privada e pública respectivamente. Caso o caminho desejado para os arquivos não seja especificado, as chaves serão salvas na pasta ```test_keys```. Caso se deseje criptografar a chave privada, será dada a opção de inserir a senha durante a execução.

- Geração de chaves PKCS#1

    - ```python test_keys/key_generator.py rsa {caminho das chaves} {modulus da chave}```

- Geração de chaves Ed25519

    - ```python test_keys/key_generator.py ed25519 {caminho das chaves}```

- Geração de chaves Dilithium{versão}
    - ```python test_keys/key_generator.py Dilithium{VERSION} {caminho das chaves}```

## Geração de assinatura

A aplicação gera assinaturas detached, com a opção de se assinar utilizando os esquemas tradicionais PKCS#1 v1.5 (RSA), Ed25519 ou os esquemas pós quânticos Dilithium2, Dilithium3 e Dilithium5. Os hashes para a assinatura podem ser criados a partir das funções SHA256, SHA512, SHA3-256 ou SHA3-512. São aceitos para assinar arquivos de texto (extensão ```.txt```) ou XML.

- ```python mtss_signer.py sign {alg. assinatura} {caminho do arquivo} {caminho da chave privada} {flag} {valor inteiro} {função hash}```

O resultado do algoritmo, se bem sucedido, será uma assinatura detached de nome ```{caminho do arquivo}_sig.mts```.

- Algoritmos de assinatura: ```rsa```, ```ed25519```, ```Dilithium2```, ```Dilithium3```, ```Dilithium5```
- Flag: ```-k```
    - Flag ```k``` pode receber valores a partir de 1. Para k=1, será gerada uma assinatura que detecta até 1 modificação. A partir desse valor, números maiores para k terão uma maior compressão de assinatura em relação ao número de blocos, mas menos erros detectáveis em número e proporção. O valor de k precisa ser compatível com o número de blocos (```n```) gerados para o documento a ser assinado, já que n é necessariamente uma potência de primo elevado por k.
- Funções de hash: ```sha256```, ```sha512```, ```sha3-256```, ```sha3-512```, ```blake2b```

## Verificação de assinatura com localização de modificações

- ```python mtss_signer.py verify {alg. assinatura} {caminho do arquivo} {caminho da chave pública} {caminho da assinatura} {função hash}```

Se bem sucedido, o resultado será a exibição de quais índices de blocos foram modificados.

## Verificação de assinatura com localização e correção de modificações

- ```python mtss_signer.py verify-correct {alg. assinatura} {caminho do arquivo} {caminho da chave pública} {caminho da assinatura} {função hash}```

Se bem sucedido, o resultado será a exibição de quais índices de blocos foram modificados e um arquivo de nome ```{caminho do arquivo}_corrected.{extensão original do arquivo}``` que conterá a correção.

## Opções adicionais

No final dos comandos, se for inserida a flag ```--debug```, a aplicação registrará dados sobre a execução no arquivo ```logs.txt```, como quais os blocos e CFFs gerados para o documento, além de dados de medição de tempo. Para realizar medições de tempo a partir da saída dos algoritmos, ao invés de serem exibidos os resultados da execução, a flag ```--time-only``` pode ser utilizada para que a saída no terminal seja apenas o tempo de execução em segundos. As opções são mutuamente exclusivas, para o registro de informações de debug não interferir nos dados da medição de tempo mais precisa.