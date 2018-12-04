#include "ABB.h"

// === Classe NohArvore ==============================================================
NohArvore::NohArvore(string d) // d tem valor default
    : valor(d), esq(NULL), dir(NULL), pai(NULL) {
}

// === Classe ABB ==============================================================
ABB::~ABB(){
    delete raiz;
}

void ABB::Inserir(string d) {
    NohArvore* novo = new NohArvore(d);
    if (raiz == NULL) {
        raiz = novo;
    } else {
        NohArvore* atual = raiz;
        NohArvore* anterior = NULL;
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
void ABB::EOAux( NohArvore* aux){
	if ( aux != NULL){
		EOAux(aux->esq);
		cout << aux->valor << "/" << Nivel(aux->valor) << " ";
		EOAux(aux->dir);
	}
}
void ABB::PreOrdem(){
	POAux(raiz);
}
void ABB::POAux( NohArvore* aux){
	if ( aux != NULL ){
		cout << aux->valor << "/" << Nivel(aux->valor) << " ";
		POAux(aux->esq);
		POAux(aux->dir);
	}
}
int ABB::Nivel(string d){
	NohArvore* atual = raiz;
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
NohArvore* ABB::BuscaAux( NohArvore* aux){
	NohArvore* atual = raiz;
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
void ABB::Transplanta(NohArvore* antigo, NohArvore* novo){
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

NohArvore* ABB::MinAux(NohArvore* aux){
	while(aux->esq != NULL){
		aux = aux->esq;
	}
	return aux;
}
void ABB::Remover(string d){
	NohArvore* aux = new NohArvore(d);
	NohArvore* NohArvoreRemover = BuscaAux(aux);
	if (NohArvoreRemover == NULL){
		cout << "ERRO" << endl;
	}
	else{
		if ( NohArvoreRemover->esq == NULL ){
			Transplanta(NohArvoreRemover, NohArvoreRemover->dir);
		}
		else if ( NohArvoreRemover->dir == NULL ){
			Transplanta(NohArvoreRemover, NohArvoreRemover->esq);
		}
		else{
			NohArvore* sucessor = MinAux(NohArvoreRemover->dir);
			if ( sucessor->pai != NohArvoreRemover ){
				Transplanta(sucessor, sucessor->dir);
				sucessor->dir = NohArvoreRemover->dir;
				sucessor->dir->pai = sucessor;
			}
			Transplanta(NohArvoreRemover, sucessor);
			sucessor->esq = NohArvoreRemover->esq;
			sucessor->esq->pai = sucessor;
		}
		delete NohArvoreRemover;
	}
}
void ABB:: PosOrdem(){
	OOAux(raiz);
}
void ABB:: OOAux(NohArvore* aux ){
	if (aux != NULL){
		OOAux(aux->esq);
		OOAux(aux->dir);
	}
}
