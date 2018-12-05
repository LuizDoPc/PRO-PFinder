#include "Lista.h"

NohLista* Lista::buscaPosicao(int pos){
    if(pos > tamanho){
        //lançar exceção
    }
    int k = 0;
    NohLista *nav = fim;
    while(nav != NULL and k != pos){
        nav = nav->ant;
    }
    return nav;
}


NohLista* Lista::busca(string valor){
    NohLista *nav = fim;
    while(nav != NULL and nav->lista->inicioInterno->valor != valor){
        nav = nav->ant;
    }
    return nav;
}

NohInterno* ListaInterno::busca(string valor){
    NohInterno *nav = fimInterno;
    while(nav != NULL and nav->valor != valor){
        nav = nav->ant;
    }
    return nav;
}

NohLista* Lista::inserir(string valor){
    NohLista *nova = new NohLista();
    if(fim == NULL){
        fim = nova;
        tamanho++;
        nova->posicao = tamanho;
        nova->lista = new ListaInterno();
        nova->lista->inserirInterno(valor);
        return nova;
    }else{
        nova->ant = fim;
        fim = nova;
        tamanho++;
        nova->posicao = tamanho;
        nova->lista = new ListaInterno();
        nova->lista->inserirInterno(valor);
        return nova;
    }
}

void Lista::remover(int pos){

    if(pos < 0 or pos > tamanho){
        //lançar exceção
    }
    NohLista *nav = fim;
    NohLista *proximo = NULL;
    int cont = 1;
    while(cont < pos){
        proximo = nav;
        nav = nav->ant;
        cont++;
    }
    
    if(nav->ant == NULL){
        proximo->ant = NULL;
        delete nav;
    }
    else{
        if(proximo == NULL){
            fim = nav->ant;
            delete nav;
        }else{
            proximo->ant = nav->ant;
            delete nav;
        }
    }
}

void Lista::imprimir(){
    NohLista *nav = fim;
    int cont = 1;
    while (nav != NULL){
        cout << "#" << cont << " ";
        nav->lista->imprimirInterno();
        cout <<endl;
        cont++;
        nav = nav->ant;
    }
}

void ListaInterno::imprimirInterno(){
    NohInterno *nav = fimInterno;
    cout << "[ ";
    while(nav != NULL){
        cout << nav->valor;

        if(nav->ant != NULL){
            cout << ", ";
        }
        nav = nav->ant;
    }
    cout << " ]";
}

void ListaInterno::inserirInterno(string valor){
    NohInterno *novo = new NohInterno();
    novo->valor = valor;
    if(fimInterno == NULL){
        fimInterno = novo;
        inicioInterno = novo;
        tamanho++;
        novo->posicao = tamanho;
    }else{
        novo->ant = fimInterno;
        fimInterno = novo;
        tamanho++;
        novo->posicao = tamanho;
    }
}

void ListaInterno::removerInterno(string valor){
    NohInterno *nav = fimInterno;
    NohInterno *proximo = NULL;

    while(nav->valor != valor){
        proximo = nav;
        nav = nav->ant;
    }
    
    if(nav->ant == NULL){
        proximo->ant = NULL;
        inicioInterno = proximo;
        tamanho--;
        delete nav;
    }
    else{
        if(proximo == NULL){
            fimInterno = nav->ant;
            tamanho--;
            delete nav;
        }else{
            proximo->ant = nav->ant;
            tamanho--;
            delete nav;
        }
    }
}
/*
int main(){
    Lista *l = new Lista();
    NohLista *aux = l->inserir("Luiz");
    aux->lista->inserirInterno("LuizInterno");
    aux->lista->inserirInterno("LuizInterno");
    aux->lista->inserirInterno("LuizInterno");
    aux->lista->inserirInterno("LuizInterno");
    aux->lista->inserirInterno("LuizInterno");

    aux = l->inserir("Alice");
    aux->lista->inserirInterno("AliceInterno");
    aux->lista->inserirInterno("AliceInterno");
    aux->lista->inserirInterno("AliceInterno");
    aux->lista->inserirInterno("AliceInterno");
    aux->lista->inserirInterno("AliceInterno");
    
    l->imprimir();
}*/