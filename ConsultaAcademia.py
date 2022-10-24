from ftplib import FTP, all_errors
from re import T
from time import strptime, strftime
import PySimpleGUI as psg
import json

# Função que coleta o usuario e senha para acessar o ftp
def login():
    psg.ChangeLookAndFeel('SystemDefault1')
    layout = [[psg.Text("LogIn", font=1, justification='center', expand_x=True)],
            [psg.Text("Usuário", font=8, expand_x=True), psg.InputText('', key='_usrnm_', font=8)],
            [psg.Text("Senha", font=8, expand_x=True), psg.InputText('', key='_pwd_', font=8)],
            [psg.Button('Ok', font=6, bind_return_key=True), psg.Button('Cancel', font=6)]]

    window = psg.Window("Log In", layout, icon='wps.ico')
    user = ''
    password = ''
    while True:
        event, values = window.read(close=True)
        if event == "Cancel" or event == psg.WIN_CLOSED:
            window.close()
            return user, password, False
        elif event == "Ok":
            user = values['_usrnm_']
            password = values['_pwd_']
            window.close()
            return user, password, True
    
# Função de acesso ao ftp    
def acessoftp(user, password):
    fdata = []
    try:
        with FTP('academia.parkingplus.com.br') as ftp:
            ftp.login(user, password)
            arq = ftp.nlst('.').pop()
            ftp.retrlines(f'RETR {arq}', fdata.append)
    except all_errors as ftperro:
            return False, ['FTP error:', ftperro]
    return True, fdata

# Função que transforma a lista de alunos em um JSON
def dicionario(fdata):
    alunos = {}
    for cadastro in fdata:
        cadastro = cadastro.split(';')
        cadastro = {
            cadastro[5] : {
                'nome' : cadastro[1],
                'matricula': cadastro[0],
                'dataInicial': cadastro[2],
                'dataFinal': cadastro[3]
            }
        }
        alunos.update(cadastro)
    return alunos

# Função que salva no computador a lista de alunos de acordo com a opção escolhida
def salvaArquivo(arq, jso=False, csv=False):
    pop = psg.popup_get_folder('Escolha a pasta', font=12, default_path='C:/', icon='wps.ico')
    nome = 'AlunosAcademia_' + strftime("%d-%m-%Y")
    dr = f'{pop}/{nome}'
    try:
        if jso:
            with open(dr + '.json', 'w', encoding='utf-8') as jsn:
                json.dump(arq, jsn)
        elif csv:
            with open(dr + '.csv', 'w', encoding='utf-8') as cs:
                for linha in arq:
                    cs.writelines(linha + '\n')   
    except PermissionError as pme:
        psg.popup('ERRO de permissão, Escolha OUTRA pasta', title='Erro', font=6, icon='wps.ico')
        return

# Função que faz a pesquisa do nome ou CPF da lista de alunos
def pesquisa(jsn, dado, cpf, nome, listagem):
    if listagem:
        lista = []
        if cpf:
            for item in jsn:
                if dado in item:
                    lista.append([jsn[item]['nome'].title(), item])
            if lista == []:
                return False, 'Nenhum CPF não encontrado'
            return True, lista
        elif nome:
            for item in jsn:
                if dado.upper() in jsn[item]['nome'].upper():
                    lista.append([jsn[item]['nome'].title(), item])
            if lista == []:
                return False, 'Nome não encontrado'
            return True, lista
    else:
        if cpf:
            retorno = jsn.get(dado, False)
            if not retorno:
                return False, 'CPF não encontrado !'
            return True, retorno, dado

# Função que cria o popUp sobre as informações do programa
def popupSobre():
    popupsobre = psg.Window('TarifaAgendada', [
        [psg.Frame(title='Sobre...', layout=[[psg.Text('Desenvolvido por: Caio Satiro\nhttps://github.com/kaiosatiro')]], size=(400, 100))], 
        [psg.Exit()]
    ], modal=True, icon='wps.ico')
    evento, valor = popupsobre.read(close=True)
    if evento == 'Exit':
        return
    else:
        return

# Função que cria a janela principal do programa
def cria_janela():
    # Estilo
    psg.ChangeLookAndFeel('SystemDefault1')

    # Menu do programa
    menu = [
        ['Menu',['Salvar', ['Json', 'Csv'], 'Exit']],
        ['Outros', ['Ajuda', 'Sobre...']]
    ]

    # Montagem da aba que exibe as informações dos alunos
    aba1 = [
        [psg.Text('CPF:', font=12, p=12),
            psg.InputText('', readonly=True, font=12, size=19, disabled_readonly_background_color='#F2F2F2', key='_CPF_'),
        psg.Text('Matrícula:', font=12, p=12), 
            psg.InputText('', readonly=True, font=12, size=16, disabled_readonly_background_color='#F2F2F2', key='_MTRCL_')],
        [psg.Text('Nome:', font=12, p=12),
            psg.InputText('', readonly=True,  font=12, size=40, disabled_readonly_background_color='#F2F2F2', key='_NM_')],
        [psg.Text('Data Inicial:', font=12, p=12),
            psg.InputText('', readonly=True, font=12, size=14, disabled_readonly_background_color='#F2F2F2', key='_DTINCL_'),
        psg.Text('Data Final:', font=12, p=12),
            psg.InputText('', readonly=True, font=12, size=14, disabled_readonly_background_color='#F2F2F2', key='_DTFNL_')]
    ]

    # Montegem da aba que exibe a lista de alunos
    aba2 = [
        [psg.Table(values=[], headings=[['Nome'], ['CPF']],
            auto_size_columns=True, display_row_numbers=True, expand_x=True, enable_click_events=True,
            font=12, num_rows=10, sbar_width=25, justification='left', alternating_row_color='#FFE8B9',
            key='_TABLE_')]
    ]

    #Montagem da janela principal inteira
    layout = [
        [psg.Menu(menu)],
        [psg.Text('PESQUISE NOME OU CPF', font=18, justification='center', expand_x=True)],
        [psg.Input(key='_INPUT_', pad=10, font=18, justification='center', expand_x=True, tooltip='Pesquise nome completo ou pacial | Atenção com acentos')],
        [psg.Radio('Por CPF', 1, font=10, expand_x=True, key='_RCPF_', default=True), 
            psg.Radio('Por Nome', 1, font=10, expand_x=True, key='_RNM_', disabled=True)],
        [psg.TabGroup([[
            psg.Tab('Aluno', aba1, key='_ALUNO_'), 
            psg.Tab('Listagem', aba2, key='_LISTA_')
        ]], key='_TABGROUP_', enable_events=True)],
        [psg.Text(key='_RPST_', font='ANY 14 bold', text_color='red', expand_x=True, justification='center')],
        [psg.Button('PESQUISAR', expand_x=True, bind_return_key=True, enable_events=True,
                     button_color=("black", "#FDBC3B"), key='_PSQSR_', font=14)]
    ]
    return psg.Window('Alunos Academia', layout, icon='wps.ico')

# Função principal do programa
def main():
    # Coleta usuario e senha e checa o retorno
    USER,  PASSWORD, chk = login()
    if not chk:
        return

    # Cria a janela principal e busca a lista de alunos no ftp
    janela = cria_janela()
    retorno = acessoftp(USER, PASSWORD)

    evento, valor = janela.read() 

    if not retorno[0]:
        erro = f'ERRO de acesso ao FTP\nVerifique o Login e senha.'
        psg.Popup(erro, title='ERRO', icon='wps.ico', font=6)
        janela.close()
        return
    elif retorno[0]:
        alunos = dicionario(retorno[1]) 

    # Laço que monitora os eventos da janela
    while True:
        if evento == '_TABGROUP_':
            if valor['_TABGROUP_'] == '_ALUNO_':
                janela['_RNM_'].Update(disabled=True)
            elif valor['_TABGROUP_'] == '_LISTA_':
                janela['_RNM_'].Update(disabled=False)

        # Pesquisa por CPF retornando todos os dados
        if evento == '_PSQSR_' and valor['_TABGROUP_'] == '_ALUNO_':
            consulta = pesquisa(alunos, valor['_INPUT_'], valor['_RCPF_'], valor['_RNM_'], False)
            if not consulta[0]:
                janela['_RPST_'].Update(consulta[1])
            elif consulta[0]:
                janela['_CPF_'].Update(consulta[2])
                janela['_MTRCL_'].Update(consulta[1]['matricula'])
                janela['_NM_'].Update(consulta[1]['nome'])
                dtI = strptime(consulta[1]['dataInicial'], "%Y-%m-%d %H:%M:%S")
                janela['_DTINCL_'].Update(f"{dtI.tm_mday}/{dtI.tm_mon}/{dtI.tm_year}")
                dtF = strptime(consulta[1]['dataFinal'], "%Y-%m-%d %H:%M:%S")
                janela['_DTFNL_'].Update(f"{dtF.tm_mday}/{dtF.tm_mon}/{dtF.tm_year}")
 
        # Pesquisa por nome ou cpf, não precisa ser exato, retorna resultados proximos
        elif evento == '_PSQSR_' and valor['_TABGROUP_'] == '_LISTA_':
            consulta = pesquisa(alunos, valor['_INPUT_'], valor['_RCPF_'], valor['_RNM_'], True)
            if not consulta[0]:
                janela['_RPST_'].Update(consulta[1])
                janela['_TABLE_'].Update([])
            else:
                janela['_RPST_'].Update('')    
                janela['_TABLE_'].Update(consulta[1])

        # Codigo que possibilita a copia do nome ou cpf selecionado na lista para a barra de pesquisa
        elif isinstance(evento, tuple):
            try:
                tp = evento[2][1]
                if tp == 0:
                    snome = consulta[1][evento[2][0]][0]
                    janela['_INPUT_'].Update(snome)        
                elif tp == 1:
                    scpf = consulta[1][evento[2][0]][1]
                    janela['_INPUT_'].Update(scpf)
            except TypeError:
                pass
            except IndexError:
                pass
            except KeyError:
                pass
        
        # Funções relativas ás opções do menu
        elif evento == 'Json':
            salvaArquivo(alunos, jso=True)
        elif evento == 'Csv':
            salvaArquivo(retorno[1], csv=True)
        elif evento == 'Ajuda':
            ...
        elif evento == 'Sobre...':
            popupSobre()
        elif evento == psg.WIN_CLOSED or evento == 'Exit':
            break
        #Leitura dos eventos
        evento, valor = janela.read()  
    janela.close()

if __name__ == '__main__':
    #Variaveis de acesso para teste
    # USER = ''
    # PASSWORD = ''
    #Chamada da janela principal
    main()
    