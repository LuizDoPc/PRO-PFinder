#include <iostream>
#include <string>
using namespace std;

class NohHash {
    friend class tabelaHash;
    private:
        string chave;
        string valor;
        NohHash* proximo = NULL;
    public:
        NohHash(string c, string v) {
            chave = c;
            valor = v;
        }
};

class TabelaHash {
    private:
        // vetor de ponteiros de nÃ³s
        NohHash** elementos;
        int capacidade;
    public:
        // construtor padrÃ£o
        TabelaHash(int cap = 100);
        // destrutor
        ~TabelaHash();
        // insere um valor v com chave c
        void insere(string c, string v);
        // recupera um valor associado a uma dada chave
        string recupera(string c);
        // altera o valor associado a uma chave
        void altera(string c, string v);
        // retira um valor associado a uma chave
        void remove(string c);
        // percorrendo a tabela hash (para fins de debug)
        void percorre();
};