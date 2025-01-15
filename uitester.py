import streamlit as st
from classtester import DadosAbertos
from constantes import estados
from datetime import datetime
from babel.numbers import format_currency
import plotly.express as px

class UI:
    def __init__(self):
        self.app = DadosAbertos()
    
    def lista_deputados(self, uf = None):
        uf_estado = st.selectbox('Estado', list(estados.values()), index = None, placeholder='Todos estados')
        if uf_estado:
            uf = uf_estado.split(' - ')[0]
            
        busca_dep = st.text_input('Buscar', key='busca_dep', placeholder='Ex: Silva')
        
        with st.spinner('Carregando dados...'):
            if busca_dep:
                deputados = self.app.busca_deputados_nome(busca_dep)
            else:
                deputados = self.app.carregar_lista_deputados(uf)
        
        # st.success('Carregamento concluído!')
        
        for dep in deputados:
            nome = dep['nome']
            foto = dep['urlFoto']
            partido = dep['siglaPartido']
            estado = dep['siglaUf']
            link = dep['uri']
            link_partido = dep['uriPartido']
            link_route = f'/?id_deputado={dep['id']}'
            
            with st.container(border=True):
                col1, col2 = st.columns([1,3])
                with col1:
                    st.html(
                        f'''
                        <a href={link_route} target="_blank">
                            <img src={foto} width=140 height=190 style="cursor: pointer">
                        </a>
                        '''
                        )
                with col2:
                    st.html(
                        f'''
                        <a href={link}>
                            <h4>{nome}</h4>
                        </a>
                        '''
                    )
                    # st.text(nome)
                    st.html(
                        f'''
                        <a href={link_partido}>
                            <h4>{partido}</h4>
                        </a>
                        '''
                    )
                    # st.text(partido)
                    st.text(estados.get(estado, 'None'))
                    # st.text(link_route)
    
    def parametros_id_deputado(self):
        dep_params = st.query_params.get('id_deputado')
        return dep_params
    
    def parametros_id_deputado_dashboard(self):
        dash_params = st.query_params.get('dash')
        return dash_params
    
    def detalhes_deputado(self, id_deputado):
        with st.spinner('Aguarde um momento...'):
            dep = self.app.detalhe_deputado(id_deputado)
        dash_params = self.parametros_id_deputado_dashboard()
        
        nome_eleitoral = dep['ultimoStatus']['nomeEleitoral']
        nome_civil = dep['nomeCivil']
        foto = dep['ultimoStatus']['urlFoto']
        sigla_partido = dep['ultimoStatus']['siglaPartido']
        
        if dep:
            with st.container(border=True):
                with st.container(border=False):
                    col1, col2 = st.columns([1,3])
                    with col1:
                        st.image(foto, width=70)
                    with col2:
                        st.subheader(nome_eleitoral)
                        
                    col3, col4 = st.columns([4,1])
                    with col3:
                        st.text(nome_civil)
                        st.text(sigla_partido)
                    with col4:
                        if st.button('Dashboard'):
                            st.query_params.from_dict({'id_deputado': id_deputado, 'dash': 'True'})
                            st.rerun() # tem que ter o rerun se não, não atualiza pro próximo query_params
            
            if dash_params == 'True':
                with st.container(border=True):
                    col1, col2 = st.columns([4,1])
                    with col1:
                        st.subheader('Dashboard')
                    with col2:
                        st.button('Voltar')
                    
                    dashboard_vars = ['tipoDespesa', 'dataDocumento', 'valorDocumento', 'ano']
                    
                    with st.spinner('Carregando dados...'):
                        desp_dep_2024 = self.app.despesas_deputados_df(id_deputado, 2024)[dashboard_vars].sort_values(by='dataDocumento', ascending=True)
                        desp_dep_2023 = self.app.despesas_deputados_df(id_deputado, 2023)[dashboard_vars].sort_values(by='dataDocumento', ascending=True)
                    
                    df_combinados = self.app.concatenar_df(desp_dep_2023, desp_dep_2024)
                    
                    fig = px.line(
                        df_combinados,
                        x='dataDocumento',
                        y='valorDocumento',
                        color='ano',
                        title='Despesas por ano',
                        labels={'dataDocumento': 'Data', 'valorDocumento': 'Valor da despesa'},
                        line_group='ano'
                    )
                    
                    st.plotly_chart(fig)
                
            else:
            
                with st.container(border=True):
                    st.subheader('Despesas por ano')
                    
                    selecao_ano = st.selectbox(label='Ano', options=[2024, 2023], index=0)
                    desp_dep = self.app.despesas_deputado(id_deputado, selecao_ano)
                    tipos_despesas = self.app.obter_tipos_despesas(id_deputado, selecao_ano)
                    selecao_tipo_despesa = st.selectbox(label='Tipo da despesa', options=tipos_despesas, index=None, placeholder='Escolha um tipo de despesa específica')
                    
                    with st.spinner('Carregando dados...'):
                        if tipos_despesas:
                            desp_dep_ = self.app.despesas_deputado(id_deputado, selecao_ano, selecao_tipo_despesa)
                        else:
                            desp_dep_ = desp_dep
                            
                    
                    df_desp_dep_ = self.app.retornar_df(desp_dep_)
                    soma_valores = format_currency(number=df_desp_dep_['valorDocumento'].sum(), currency='BRL', locale='pt_BR')
                    
                    with st.container(border=True):
                        st.text('Gasto total anual')
                        st.html(f'''<h3>{soma_valores}</h3>''')
                        
                    
                    for desp in desp_dep_:
                        tipo_desp = desp['tipoDespesa']
                        ano = desp['ano']
                        mes = desp['mes']
                        data_documento = datetime.strptime(desp['dataDocumento'], '%Y-%m-%dT%H:%M:%S').strftime('%d-%m-%Y')
                        link_documento = desp['urlDocumento']
                        valor_documento = format_currency(number=desp['valorDocumento'], currency='BRL', locale='pt_BR')
                        nome_fornecedor = desp['nomeFornecedor']
                        cnpj_fornecedor = desp['cnpjCpfFornecedor']
                        
                        with st.container(border=True):
                            st.text(tipo_desp)
                            st.text(f'Prestador: {nome_fornecedor}')
                            st.text(f'CNPJ: {cnpj_fornecedor}')
                            st.text(f'Data: {data_documento}')
                            st.html(f'''<a href={link_documento}><h4>Acesso ao documento</h4></a>''')
                            st.text(f'Valor do serviço: {valor_documento}')
                    
                    st.write(desp_dep_)
            
        else:
            st.error('deputado não encontrado')
            
        # st.write(dep)
    
    def run(self):
        st.title('test')
        id_deputado = self.parametros_id_deputado()
        if id_deputado:
            self.detalhes_deputado(id_deputado)
        else:
            self.lista_deputados()

app = UI()
app.run()