#ifndef LISTA_H
#define LISTA_H

#include <iostream>
using namespace std;

class NohInterno {
    friend class ListaInterno;
    private:
        NohInterno *ant;
        string valor;
    public:
        NohInterno(){
            ant = NULL;
        }
};

class ListaInterno{
    friend class NohInterno;
    private:
        NohInterno *fimInterno;
        int tamanho;
    public:
        ListaInterno(){
            fimInterno = NULL;
            tamanho = 0;
        }
        void inserirInterno(string valor);
        void removerInterno(string valor);
        void imprimirInterno();
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
};
#endif