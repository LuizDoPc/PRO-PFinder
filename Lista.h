#ifndef LISTA_H
#define LISTA_H

#include <iostream>
using namespace std;

class NohInterno {
    friend class ListaInterno;
    friend class Lista;
    private:
        NohInterno *ant;
    public:
        string valor;
        int posicao;
        NohInterno(){
            ant = NULL;
        }
};

class ListaInterno{
    friend class NohInterno;
    friend class Lista;
    private:
        NohInterno *fimInterno;
        NohInterno *inicioInterno;
        int tamanho;
    public:
        ListaInterno(){
            fimInterno = NULL;
            tamanho = 0;
        }
        void inserirInterno(string valor);
        void removerInterno(string valor);
        void imprimirInterno();
        NohInterno* busca(string valor);
};

class NohLista{
    friend class Lista;
    private:
        NohLista *ant;
    public:
        ListaInterno *lista;
        int posicao;
        NohLista(){
            lista = NULL;
            ant = NULL;
        }
};

class Lista{
    friend class NohLista;
    friend class ListaInterno;
    friend class NohInterno;
    private:
        NohLista *fim;
        int tamanho;
    public:
        Lista(){
            fim = NULL;
            tamanho = 0;
        }
        NohLista* inserir(string valor);
        void remover(int pos);
        void imprimir();
        NohLista* busca(string valor);
        NohLista* buscaPosicao(int pos);
        void arrumaPosicao();
};
#endif