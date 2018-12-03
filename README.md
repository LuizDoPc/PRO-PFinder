# PRO-P Finder

Software para localizar uma proteina em um grupo de espécies.

Para organizar o grupo de espécies será usada uma Árvore Binária de Busca (ABB) que irá armazenar o nome da espécie, e sua posição no vetor de hash.

O hash funcionará da seguinte maneira: 
    - Cada posição do hash irá pertencer a uma espécie.
    - Na lista de cada posição, haverá os organismos daquela espécie que provavelmente possuem a proteína.

Para encontrar os organismos a serem inseridos no hash será usado um script externo desenvolvido na linguagem python. Esse script irá usar a ferramenta Blastp para encontrar os dados em um banco de dados externo do NCBI. Os resultados desse scripts serão armazenados num arquivo .al que será lido pelo programa em C++. 

O programa em C++ irá ler os arquivos que o script gerou e construir, a partir deles, as estruturas de dados. Então, será possível, fazer consultas otimizadas do tipo: "Quais são os organizmos da espécie X que possuem a proteína Y?".

As ordenações serão feitas em disco (nos arquivos) e podem ser feitas através de duas chaves: o número do organismo no hash ou o e-value do mesmo.

O script de instalação irá criar a estrutura de pastas e transferir, da web, os arquivos nescessários para o funcionamento do PRO-P Finder.

É nescessário uma conexão estável com a internet para que o software gere os arquivos nescessários para construir as estruturas de dados.


# NOTES

blastp -query fastafile -db nr -remote -entrez_query "species name" -outfmt 7 > saida.out
