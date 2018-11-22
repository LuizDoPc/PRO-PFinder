#include <iostream>
#include <string>

using namespace std;


class Noh {
    friend class ABB;
    public:
        Noh (string d);
    protected:
        string valor;
        Noh* esq;
        Noh* dir;
        Noh* pai;
};

class ABB {
    public:
        ABB() { raiz = NULL; }
        ~ABB();
        // Insere um dado na Ã¡rvore.
        void Inserir(string d);
        // Verifica se um dado tem sucessor e o retorna.
        void EmOrdem();
        void EOAux( Noh* aux);
        void PreOrdem();
        void POAux( Noh* aux);
        void Remover (string d);
		int Nivel(string d);
        void Transplanta( Noh* antigo, Noh* novo);
        Noh* BuscaAux(Noh* aux);
        Noh* MinAux(Noh* aux);
		void PosOrdem();
		void OOAux( Noh* aux);
    protected:
        Noh* raiz;
       
};

using namespace std;
// === Classe Noh ==============================================================
Noh::Noh(string d) // d tem valor default
    : valor(d), esq(NULL), dir(NULL), pai(NULL) {
}

// === Classe ABB ==============================================================
ABB::~ABB(){
    delete raiz;
}

void ABB::Inserir(string d) {
    Noh* novo = new Noh(d);
    if (raiz == NULL) {
        raiz = novo;
    } else {
        Noh* atual = raiz;
        Noh* anterior = NULL;
        while (atual != NULL) {
            anterior = atual;
            if (atual->valor > d) {
                atual = atual->esq;
            } else {
                atual = atual->dir;
            }
        }
        novo->pai = anterior;
        if ((anterior->valor) > (novo->valor)) {
            anterior->esq = novo;
        } else {
            anterior->dir = novo;
        }
    }
}

void ABB::EmOrdem(){
	EOAux(raiz);
}
void ABB::EOAux( Noh* aux){
	if ( aux != NULL){
		EOAux(aux->esq);
		cout << aux->valor << "/" << Nivel(aux->valor) << " ";
		EOAux(aux->dir);
	}
}
void ABB::PreOrdem(){
	POAux(raiz);
}
void ABB::POAux( Noh* aux){
	if ( aux != NULL ){
		cout << aux->valor << "/" << Nivel(aux->valor) << " ";
		POAux(aux->esq);
		POAux(aux->dir);
	}
}
int ABB::Nivel(string d){
	Noh* atual = raiz;
	int cont = 0;
	while ( atual->valor != d && atual != NULL ){
		cont++;
		if ( atual->valor > d){
			atual = atual->esq;
		}
		else{
			atual = atual->dir;
		}
	}
	return cont;
}
Noh* ABB::BuscaAux( Noh* aux){
	Noh* atual = raiz;
	while(atual != NULL ){
		if ( atual->valor == aux->valor){
			return atual;
		}
		else if (atual->valor > aux->valor){
			atual = atual->esq;
		}
		else{
			atual = atual->dir;
		}
	}
	return atual;
}
void ABB::Transplanta(Noh* antigo, Noh* novo){
	if ( raiz == antigo ){
		raiz = novo;
	}
	else if ( antigo == antigo->pai->esq){
		antigo->pai->esq = novo;
	}
	else{
		antigo->pai->dir = novo;
	}
	if ( novo != NULL ){
		novo->pai= antigo->pai;
	}
}

Noh* ABB::MinAux(Noh* aux){
	while(aux->esq != NULL){
		aux = aux->esq;
	}
	return aux;
}
void ABB::Remover(string d){
	Noh* aux = new Noh(d);
	Noh* nohRemover = BuscaAux(aux);
	if (nohRemover == NULL){
		cout << "ERRO" << endl;
	}
	else{
		if ( nohRemover->esq == NULL ){
			Transplanta(nohRemover, nohRemover->dir);
		}
		else if ( nohRemover->dir == NULL ){
			Transplanta(nohRemover, nohRemover->esq);
		}
		else{
			Noh* sucessor = MinAux(nohRemover->dir);
			if ( sucessor->pai != nohRemover ){
				Transplanta(sucessor, sucessor->dir);
				sucessor->dir = nohRemover->dir;
				sucessor->dir->pai = sucessor;
			}
			Transplanta(nohRemover, sucessor);
			sucessor->esq = nohRemover->esq;
			sucessor->esq->pai = sucessor;
		}
		delete nohRemover;
	}
}
void ABB:: PosOrdem(){
	OOAux(raiz);
}
void ABB:: OOAux(Noh* aux ){
	if (aux != NULL){
		OOAux(aux->esq);
		OOAux(aux->dir);
	}
}
// === Programa ================================================================
int main() {
    ABB arvore;
    string chave;
    char operacao;
	cin >> operacao;
    do {
        switch (operacao) {
            case 'i': // Inserir
                cin >> chave;
                arvore.Inserir(chave);
                break;
            case 'r': // Escrever
				cin >> chave;
                arvore.Remover(chave);
                break;
            case 'o': 
                arvore.EmOrdem();
                break;
            case 'p':  
                arvore.PreOrdem();
                break;
			default:
				cout << "Comando Invalido!";
        }
		cin >> operacao;
    } while (operacao != 'f');
    return 0;
}
