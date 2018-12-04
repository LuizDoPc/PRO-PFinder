#include <iostream>
#include <string>

using namespace std;

class NohArvore {
    friend class ABB;
    public:
        NohArvore (string d);
    protected:
        string valor;
        NohArvore* esq;
        NohArvore* dir;
        NohArvore* pai;
};

class ABB {
    public:
        ABB() { raiz = NULL; }
        ~ABB();
        // Insere um dado na Ã¡rvore.
        void Inserir(string d);
        // Verifica se um dado tem sucessor e o retorna.
        void EmOrdem();
        void EOAux( NohArvore* aux);
        void PreOrdem();
        void POAux( NohArvore* aux);
        void Remover (string d);
		int Nivel(string d);
        void Transplanta( NohArvore* antigo, NohArvore* novo);
        NohArvore* BuscaAux(NohArvore* aux);
        NohArvore* MinAux(NohArvore* aux);
		void PosOrdem();
		void OOAux( NohArvore* aux);
    protected:
        NohArvore* raiz;
       
};
