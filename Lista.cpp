#include "Lista.h"

NohLista* Lista::buscaPosicao(int pos){
    int k = 1;
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

void Lista::arrumaPosicao(){
    NohLista *nav = fim;
    int cont = 1;
    while(nav != NULL){
        nav->posicao = cont;
        nav = nav->ant;
        cont ++;
    }
}

NohLista* Lista::inserir(string valor){
    NohLista *nova = new NohLista();
    tamanho++;
    nova->posicao = tamanho;
    nova->lista = new ListaInterno();
    nova->lista->inserirInterno(valor);
    if(fim == NULL){
        fim = nova;
        arrumaPosicao();
        return nova;
    }else{
        NohLista *nav = fim;
        NohLista *proximo = NULL;
        while(nav != NULL and nav->lista->inicioInterno->valor < valor){
            proximo = nav;
            nav = nav->ant;
        }

        if(nav == NULL){
            proximo->ant = nova;
        }
        else{
            if(proximo == NULL){
                nova->ant = nav;
                fim = nova;
            }else{
                proximo->ant = nova;
                nova->ant = nav;
            }
        }
        arrumaPosicao();
        return nova;
    }
}

void Lista::remover(int pos){
    NohLista *nav = fim;
    NohLista *proximo = NULL;
    int cont = 1;
    while(cont != pos){
        proximo = nav;
        nav = nav->ant;
        cont++;
    }

    cout << nav->posicao <<endl;

    if(nav->ant == NULL){
        proximo->ant = NULL;
    }
    else{
        if(proximo == NULL){
            fim = nav->ant;
        }else{
            proximo->ant = nav->ant;
        }
    }
    tamanho--;
    delete nav;
    arrumaPosicao();
}

void Lista::imprimir(){
    NohLista *nav = fim;
    while (nav != NULL){
        cout << "#" << nav->posicao << " ";
        nav->lista->imprimirInterno();
        cout <<endl;
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
    novo->posicao = tamanho;
    if(fimInterno == NULL){
        inicioInterno = novo;
    }else{
        novo->ant = fimInterno;
    }
    fimInterno = novo;
    tamanho++;
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
    }
    else{
        if(proximo == NULL){
            fimInterno = nav->ant;
        }else{
            proximo->ant = nav->ant;
        }
    }
    tamanho--;
    delete nav;
}