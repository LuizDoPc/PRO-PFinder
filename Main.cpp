/*
 Trabalho de Estrutura de Dados 2018.2
 Pro-PFinder
 Por Alice Rezende Ribeiro, Gabriel Piovesan Melchiori Peruzza e Luiz Otávio Andrade Soares
 ->colocar o q cada arquivo tem
*/

#include "ABB.h"
#include "Lista.h"
#include <dirent.h>
#include <vector>
#include <fstream>



vector<string> open(string path = "LA FILES") {

    DIR* dir;
    dirent* pdir;
    vector<string> files;

    dir = opendir(path.c_str());

    while ((pdir = readdir(dir))) {
        files.push_back(pdir->d_name);
    }
    
    return files;
}

void criarEd(ABB *abb, Lista *l){
    vector<string> f;

    f = open();

    for(vector<string>::iterator it =  f.begin(); it != f.end(); it++){
        ifstream file("LA FILES/"+*it);
        if(file.is_open()){
            string line;
            NohLista *aux = l->inserir((*it));

            while(getline(file, line)){
                if(line[0] != '#'){
                    int cont = 0;
                    string accession = "";
                    for(long unsigned int i=0; i<line.size(); i++){
                        if(line[i] == '\t'){ 
                            cont ++;
                        }
                        if(line[i] != '\t' and cont == 1){
                            accession += line[i];
                        }
                    }
                    aux->lista->inserirInterno(accession);
                    abb->Inserir((*it), aux->posicao);
                    //cout << accession << endl;
                }    
            }
        }
    }
    //l->imprimir();
}

void add(char alternativa, ABB *abb, Lista *l){

    if(alternativa == 'o'){
        string especie, organismo;
        getline(cin, especie);
        getline(cin, organismo);

        NohLista *aux = l->busca(especie);
        aux->lista->inserirInterno(organismo);
    }else{
        string especie;
		getline(cin, especie);

        NohLista *aux = l->inserir(especie);
        abb->Inserir(especie, aux->posicao);
    }
}

void rem(char alternativa, ABB *abb, Lista *l){
    if(alternativa == 'o'){
        string especie, organismo;
        getline(cin, especie);
        getline(cin, organismo);

        NohLista *aux = l->busca(especie);
        aux->lista->removerInterno(organismo);
    }else{
        string especie;
        getline(cin, especie);

        NohLista *aux = l->busca(especie);
        l->remover(aux->posicao);
    }
}

void consultar(char alternativa, ABB *abb, Lista *l){
    if(alternativa == 'o'){
        string especie, organismo;
        getline(cin, especie);
        getline(cin, organismo);
        int pos = abb->Busca(especie);
        NohLista *posespecie = l->buscaPosicao(pos);
        NohInterno *posorganismo = posespecie->lista->busca(organismo);
        cout << "ORGANISMO: " << posorganismo->valor << endl << "ESPECIE: " << especie << endl << "POSICAO: " << posorganismo->posicao << endl;
    }else{
        string especie;
        getline(cin, especie);
        int pos = abb->Busca(especie);
        NohLista *aux = l->buscaPosicao(pos);
        cout << "ESPECIE: " << especie << endl;
        aux->lista->imprimirInterno();
    }
}

void imprimir(ABB *abb, Lista *l){
    l->imprimir();
}

void ordena(ABB *abb, Lista *l){
    


}

void menu(ABB *abb, Lista *l){
    int opcao;
	cout << "                Pro-PFinder                 " << endl;
	cout << "*---*---*---*---*---*----*---*---*---*---*---*---*---*" << endl;
	cout << "*---*---*---*---*---*----*---*---*---*---*---*---*---*" << endl;
	cout << "            Escolha uma alternativa:         " << endl;
	cout << endl;
	cout << "1: Para criar a estrutura a partir dos arquivos" << endl;
    cout << "2: Para inserir novo organismo(o) ou especie(e)" << endl;
	cout << "3: Para remover, organismo(o) ou especie(e)" << endl;
	cout << "4: Para consultar,organismo(o) ou especie(e)" << endl;
	cout << "5: Para imprimir tudo" << endl;
	cout << "6: Para imprimir de foma ordenada" << endl;
	cout << "0: Para finalizar o programa" << endl;
	cout << endl;
	cout << "*---*---*---*---*---*----*---*---*---*---*---*---*---*" << endl;
	cout << "*---*---*---*---*---*----*---*---*---*---*---*---*---*" << endl;
	cin >>opcao;
	 do {
        switch (opcao) {
            case 1: // Cria estrutura a partir de arquivo
                criarEd(abb, l);
                break;
            case 2: // Inserir
                char alternativa;
				cin >> alternativa;
				add(alternativa, abb, l);
                break;
            case 3: // Remover
				char alternativa;
				cin >> alternativa;
				rem(alternativa, abb, l);
                break;
            case 4: // Buscar
				char alternativa;
				cin >> alternativa;
				consultar(alternativa, abb, l);
                break;
            case 5: // Imprime  
                imprimir(abb, l);
                break;
            case 6: // Ordena e Imprime
                ordena(abb, l);
                imprimir(abb, l);
                break;
			default:
				cout << "Comando Invalido!";
        }
		cin >> opcao;
		if (opcao == 0 ){
			cout << "" << endl;
		}
    } while (opcao != 0);
}

int main(){
    
    ABB *abb = new ABB();
    Lista *l = new Lista();
    
    menu(abb, l);

    return 0;
}
