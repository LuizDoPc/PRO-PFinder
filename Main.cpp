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
                }    
            }
        }
    }
}

void add(char alternativa, ABB *abb, Lista *l){

    if(alternativa == 'o'){
        string especie, organismo;
        cout << "INFORME ESPECIE: ";
        cin.ignore();
        getline(cin, especie);
        cout << "INFORME ORGANISMO: ";
        getline(cin, organismo);
        NohLista *aux = l->busca(especie);
        if(aux == NULL){
            cout <<endl << "ESPECIE NAO ENCONTRADA"<<endl;
        }else{
            aux->lista->inserirInterno(organismo);
        }
    }else{
        string especie;
        cout << "INFORME ESPECIE: ";
        cin.ignore();
		getline(cin, especie);
        NohLista *aux = l->inserir(especie);
        abb->Inserir(especie, aux->posicao);
    }
}

void rem(char alternativa, ABB *abb, Lista *l){
    if(alternativa == 'o'){
        string especie, organismo;
        cout << "INFORME ESPECIE: ";
        cin.ignore();
        getline(cin, especie);
        cout << "INFORME ORGANISMO: ";
        getline(cin, organismo);

        int pos = abb->Busca(especie);
        NohLista *posespecie = l->buscaPosicao(pos);
        if(posespecie == NULL){
            cout <<endl << "ESPECIE NAO ENCONTRADA"<<endl;
        }else{
            posespecie->lista->removerInterno(organismo);
        }
    }else{
        string especie;
        cout << "INFORME ESPECIE: ";
        cin.ignore();
        getline(cin, especie);

        int pos = abb->Busca(especie);
        if(pos == -1){
            cout <<endl << "ESPECIE NAO ENCONTRADA"<<endl;
        }else{
            l->remover(pos);
            abb->Remover(especie);
        }
    }
}

void consultar(char alternativa, ABB *abb, Lista *l){
    if(alternativa == 'o'){
        string especie, organismo;
        cout << "INFORME ESPECIE: ";
        cin.ignore();
        getline(cin, especie);
        cout << "INFORME ORGANISMO: ";
        getline(cin, organismo);
        int pos = abb->Busca(especie);
        NohLista *posespecie = l->buscaPosicao(pos);
        if(posespecie == NULL){
            cout <<endl << "ESPECIE NAO ENCONTRADA"<<endl;
        }else{
            NohInterno *posorganismo = posespecie->lista->busca(organismo);
            cout << "ORGANISMO: " << posorganismo->valor << endl << "ESPECIE: " << especie << endl << "POSICAO: " << posorganismo->posicao << endl;
        }
    }else{
        string especie;
        cout << "INFORME ESPECIE: ";
        cin.ignore();
        getline(cin, especie);
        int pos = abb->Busca(especie);
        NohLista *aux = l->buscaPosicao(pos);
        if(aux == NULL){
            cout <<endl << "ESPECIE NAO ENCONTRADA"<<endl;
        }else{
            cout << "ESPECIE: " << especie << endl;
            cout << "ORGANISMOS: ";
            aux->lista->imprimirInterno();
        }
    }
}

void imprimir(ABB *abb, Lista *l){
    cout <<endl;
    cout << "IMPRIMINDO LISTA" <<endl;
    l->imprimir();
    cout <<endl;
    cout << "IMPRIMINDO ARVORE" <<endl;
    abb->EmOrdem();
    cout<<endl;
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
	cout << "0: Para finalizar o programa" << endl;
	cout << endl;
	cout << "*---*---*---*---*---*----*---*---*---*---*---*---*---*" << endl;
	cout << "*---*---*---*---*---*----*---*---*---*---*---*---*---*" << endl;
	cin >>opcao;
    char alternativa;
	 do {
        switch (opcao) {
            case 1:
                criarEd(abb, l);
                break;
            case 2:
                cout << "ESPECIE (e) OU ORGANISMO (o): ";
				cin >> alternativa;
				add(alternativa, abb, l);
                break;
            case 3:
                cout << "ESPECIE (e) OU ORGANISMO (o): ";
				cin >> alternativa;
				rem(alternativa, abb, l);
                break;
            case 4:
                cout << "ESPECIE (e) OU ORGANISMO (o): ";
				cin >> alternativa;
				consultar(alternativa, abb, l);
                break;
            case 5:
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
