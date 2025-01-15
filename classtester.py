import requests
import re
import pandas as pd

class DadosAbertos:
    def __init__(self):
        self.url_base = 'https://dadosabertos.camara.leg.br/api/v2/'
    
    def carregar_lista_deputados(self, uf: str = None):
        deputados = []
        pagina = 1
        
        while True:
            url = f'{self.url_base}deputados?ordem=ASC&ordenarPor=nome&pagina={pagina}&itens=100'
            response = requests.get(url)
            
            if response.status_code == 200:
                j = response.json()
                
                deputados.extend(j['dados'])
                
                header = j['links']
                href_ultima_pagina = next(h['href'] for h in header if h['rel'] == 'last')
                ultima_pagina = int(re.search(r'pagina=(\d+)', href_ultima_pagina).group(1))
                
                if pagina < ultima_pagina:
                    pagina += 1
                else:
                    break
            else:
                print('nooope')
                break
            
        if uf:
            deputados_uf = [dep for dep in deputados if uf.lower() in dep['siglaUf'].lower()]
        
        return deputados if uf == None else deputados_uf
    
    # def busca_por_estado(self, uf):
    #     deputados = self.carregar_lista_deputados()
        
    #     deputados_encontrados = [dep for dep in deputados if uf.lower() in dep['siglaUf'].lower()]
        
    #     return deputados_encontrados

    def busca_deputados_nome(self, nome: str):
        deputados = self.carregar_lista_deputados()
        
        deputados_encontrados = [dep for dep in deputados if nome.lower() in dep['nome'].lower()]
        
        return deputados_encontrados

    def detalhe_deputado(self, id: int):
        url = f'{self.url_base}deputados/{id}'
        response = requests.get(url)
        
        if response.status_code == 200:
            j = response.json()
        else:
            print('Erro ao localizar id de deputado')
        
        return j['dados']

    def despesas_deputado(self, id: int, ano: int, tipo_despesa: str = None):
        despesas = []
        pagina = 1
        
        while True:
            url = f'{self.url_base}deputados/{id}/despesas?ano={ano}&ordem=ASC&ordenarPor=mes'
            response = requests.get(url)
            
            if response.status_code == 200:
                j = response.json()
                
                despesas.extend(j['dados'])
                
                header = j['links']
                href_ultima_pagina = next(h['href'] for h in header if h['rel'] == 'last')
                ultima_pagina = int(re.search(r'pagina=(\d+)', href_ultima_pagina).group(1))
                
                if pagina < ultima_pagina:
                    pagina += 1
                else:
                    break
            else:
                print('noope, deu ruim nas despesas do deputado')
                break
        
        if tipo_despesa:
            despesas_por_tipo = [desp_tipo for desp_tipo in despesas if tipo_despesa.lower() in desp_tipo['tipoDespesa'].lower()]
            
        return despesas if tipo_despesa == None else despesas_por_tipo
    
    def obter_tipos_despesas(self, id_deputado, ano) -> list:
        despesas = self.despesas_deputado(id_deputado, ano)
        return sorted(list(set(d['tipoDespesa'] for d in despesas)))
    
    def despesas_deputados_df(self, id_deputado: int, ano: int):
        despesas_df = pd.DataFrame(self.despesas_deputado(id_deputado, ano))
        despesas_df['dataDocumento'] = pd.to_datetime(despesas_df['dataDocumento'])
        return despesas_df

    def retornar_df(self, dataframe) -> pd.DataFrame:
        df = pd.DataFrame(dataframe)
        return df

    def concatenar_df(self, df_a, df_b):
        concatenado = pd.concat([df_a, df_b])
        return concatenado

if __name__ == '__main__':
    app = DadosAbertos()
    print(app.carregar_lista_deputados())