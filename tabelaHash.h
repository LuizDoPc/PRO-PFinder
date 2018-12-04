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
