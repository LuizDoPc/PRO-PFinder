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

# EXTRATOR

ex ()
{
if [ -f $1 ] ; then
    case $1 in
    *.tar.bz2)   tar xjf $1   ;;
    *.tar.gz)    tar xzf $1   ;;
    *.bz2)       bunzip2 $1   ;;
    *.rar)       unrar x $1     ;;
    *.gz)        gunzip $1    ;;
    *.tar)       tar xf $1    ;;
    *.tbz2)      tar xjf $1   ;;
    *.tgz)       tar xzf $1   ;;
    *.zip)       unzip $1     ;;
    *.Z)         uncompress $1;;
    *.7z)        7z x $1      ;;
    *)           echo "'$1' cannot be extracted via ex()" ;;
    esac
else
    echo "'$1' is not a valid file"
fi
}
