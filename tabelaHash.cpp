#include "TabelaHash.h"

const int UMPRIMO = 39;

int funcaoHash(string s, int M) {
    int h = 0;
    for (unsigned i = 0; i < s.length(); i++)
        h = (UMPRIMO * h + s[i]) % M;
    return h;
}

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

// construtor padrÃ£o
TabelaHash::TabelaHash(int cap) {
    elementos = new NohHash*[cap];
    capacidade = cap;
    for (int i = 0; i < cap; i++)
        elementos[i] = NULL;
}

// destrutor
TabelaHash::~TabelaHash() {
    for (int i=0; i < capacidade; i++) {
        NohHash* atual = elementos[i];
        // percorre a lista removendo todos os nÃ³s
        while (atual != NULL) {
            NohHash* aux = atual;
            atual = atual-> proximo;
            delete aux;
        }
    }
    delete[] elementos;
}

// Insere um valor v com chave c.
void TabelaHash::insere(string c, string v) {
    int pos = funcaoHash(c,capacidade);
    if(elementos[pos] == NULL){ // se nao tiver nenhum elemento na lista
        NohHash* novo = new NohHash(c,v); //cria um novo NohHash 
        elementos[pos] = novo; // coloca ele no vetor
    }
    else{ // se ja tiver ocupada
        NohHash* privetor = elementos[pos]; // o elemento vira um NohHash
        NohHash* novo = new NohHash(c,v); // cria um novo NohHash
        while(privetor->proximo != NULL){//ate chegar no fim
            privetor= privetor->proximo;
        }
        privetor->proximo = novo; // encadeia a lista
        novo->proximo = NULL;
   }
}

// recupera um valor associado a uma dada chave
string TabelaHash::recupera(string c) {
    int h;
    h = funcaoHash(c, capacidade);

    if ((elementos[h] != NULL) and (elementos[h]->chave == c)) {
        return elementos[h]->valor;
    } else {
        NohHash* atual = elementos[h];

        while ((atual != NULL) and (atual->chave != c)) {
            atual = atual->proximo;
        }

        if ((atual != NULL) and (atual->chave == c)) {
            return atual->valor;
        } else {
            return "NAO ENCONTRADO!";
        }
    }
}

// altera o valor associado a uma chave
void TabelaHash::altera(string c, string v) {
   int pos = funcaoHash(c, capacidade); //calcula a posicao que quer
   if(elementos[pos] == NULL){ //se ela estiver vazia e pq o elemento já nao existe
       cout << "ERRO NA ALTERACAO!" << endl;
   }
   else{
       NohHash* privetor = elementos[pos]; // coloca o primeiro elemento como um NohHash
       while(privetor->chave != c && privetor->proximo != NULL){ // se é diferente e se nao chegou ao fim
           privetor = privetor->proximo;
       }
       if (privetor->chave == c){ // se saiu na primeira condicao, ou seja, se o elemeto existe na lista
           privetor->valor = v; // altera seu valor
       }
       else{ // se saiu na segunda condicao, ou seja, saiu da lista por que ela acabou, sem encontar o elemento
           cout << "ERRO NA ALTERACAO!" << endl;
       }

   }
}

// retira um valor associado a uma chave
void TabelaHash::remove(string c) {
    int pos = funcaoHash(c, capacidade);
    if (elementos[pos] == NULL){
        cout << "ERRO NA REMOCAO!" << endl;
    }
    else{
        NohHash* privetor = elementos[pos];
        NohHash* anterior = NULL;
        while(privetor->chave != c && privetor->proximo != NULL){ // se é diferente e se nao chegou ao fim
            anterior = privetor;
           privetor = privetor->proximo;
       }
       if (privetor->chave == c){ // se saiu na primeira condicao, ou seja, se o elemeto existe na lista
          if(anterior == NULL){
              elementos[pos]=privetor->proximo;
          }
          else if ( privetor->proximo == NULL){
              anterior->proximo = NULL;
          }
          else
          {
              anterior->proximo = privetor->proximo;
          }
       }
       else{ // se saiu na segunda condicao, ou seja, saiu da lista por que ela acabou, sem encontar o elemento
           cout << "ERRO NA REMOCAO!" << endl;
       }
        delete(privetor);
    }
}

// percorre a tabela hash, escrevendo as listas de itens (para fins de debug)
void TabelaHash::percorre( ) {
    NohHash* atual;
    for (int i = 0; i < capacidade; i++) {
        cout << i << ":";
        atual = elementos[i];
        while (atual != NULL) {
            cout << "[" << atual->chave << "/"
                 << atual->valor << "]->";
            atual = atual->proximo;
        }
        cout << "NULL  ";
    }
}