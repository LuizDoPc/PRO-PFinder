#include "ABB.h"
#include "TabelaHash.h"
#include <dirent.h>
#include <vector>
#include <fstream>

vector<string> open(string path = "LA FILES") {

    DIR*    dir;
    dirent* pdir;
    vector<string> files;

    dir = opendir(path.c_str());

    while ((pdir = readdir(dir))) {
        files.push_back(pdir->d_name);
    }
    
    return files;
}

int main(int argc, char const *argv[]){
    
    //ABB *abb = new ABB();
    //TabelaHash *th = new TabelaHash();

    
    vector<string> f;

    f = open(); // or pass which dir to open

    fstream file("LA FILES/"+f[2]);

    if(file.is_open()){
        string line;
        while ( getline (file, line) ){
            cout << line << endl;
        }
    }
    else{
        cerr << "Erro" <<endl;
    }
    return 0;
}
