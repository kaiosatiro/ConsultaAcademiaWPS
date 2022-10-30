from ftplib import FTP, all_errors
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

    window = psg.Window("Log In", layout, icon="wps.ico")
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
    return True, fdata, arq


# Funcao que valida as linhas do arquivo
def validaArquivo(lista):
    errlinhas = {
        "LinhaErrada": [],
        "DataErrada": [],
        "CPFErrado": []
    }
    listaclean = []
    for i, linha in enumerate(lista, 1):
        item = linha.split(';')
        ln = len(item)
        if ln in (6, 7):
            try:   
                #('%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d','%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y')
                strptime(item[2], "%Y-%m-%d %H:%M:%S")
                strptime(item[3], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                    errlinhas['DataErrada'].append(i)
            else:
                try:
                    int(item[5])
                except ValueError:
                    errlinhas['CPFErrado'].append(i)
                else:
                    listaclean.append()
        else:
            errlinhas['LinhaErrada'].append(i)

    for i in errlinhas.values():
        if i != []:
            return False, listaclean, errlinhas

    return True, listaclean, errlinhas



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
def salvaArquivo(arq, nome, jso=False, txt=False):
    pop = psg.popup_get_folder('Escolha a pasta', font=12, default_path='C:/', icon="wps.ico")
    dr = f'{pop}/{nome}'
    try:
        if jso:
            with open(dr + '.json', 'w', encoding='utf-8') as jsn:
                json.dump(arq, jsn)
        elif txt:
            with open(dr, 'w', encoding='utf-8') as cs:
                for linha in arq:
                    cs.writelines(linha + '\n')   
    except PermissionError:
        psg.popup('ERRO de permissão, Escolha OUTRA pasta', title='Erro', font=6, icon="wps.ico")
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


#Função que tranforma o dicionario de erros na lista a ser exibida
def transformadic(dc):
    linha, data, cpf = list(dc.values())

    i = 0
    while i < max(len(linha), len(data), len(cpf)):
        try:
            linha[i]
        except IndexError:
            linha.append('')
        try:
            data[i]
        except IndexError:
            data.append('')
        try:
            cpf[i]
        except IndexError:
            cpf.append('')
        i += 1

    ls = []
    for x, y, z in zip(linha, data, cpf):
            ls.append([x, y, z])
    
    return ls


# Função que exibe os possiveis erro do arquivo
def exibeErros(dc):
    ls = transformadic(dc)
    layout = [[psg.Table(values=ls, headings=[['Linha'], ['Data'], ['CPF']],
                    auto_size_columns=True, expand_x=True, expand_y=True,font=12, num_rows=10,
                    sbar_width=25, justification='center', alternating_row_color='#FFE8B9',)],
            [psg.Text("Proseguir", font=8, expand_x=True)],
            [psg.Button('Sim', font=6, bind_return_key=True), psg.Button('Não', font=6)]]
    
    window = psg.Window("Erros no aquivo", layout, icon="wps.ico", size=(500, 500))

    while True:
        event, values = window.read(close=True)
        if event == "Cancel" or event == psg.WIN_CLOSED:
            window.close()
            return False
        elif event == "Sim":
            window.close()
            return True


# Função que cria o popUp sobre as informações do programa
def popupSobre():
    popupsobre = psg.Window('TarifaAgendada', [
        [psg.Frame(title='Sobre...', layout=[[psg.Text('Feito por: Caio Satiro\nPython: ftplib - PysimpleGUI ')]], size=(400, 100))], 
        [psg.Exit()]
    ], modal=True, icon="wps.ico")
    evento, valor = popupsobre.read(close=True)
    if evento == 'Exit':
        return
    else:
        return

# Função que cria um popUp de ajuda no uso do programa
def popupAjuda():
    txt = """Na aba aluno --> Pesquise o CPF completo.
Na aba Lista :
    Por CPF -----> Pesquise um CPF inconpleto.
    Por Nome ---> Pesquise um nome inconompleto.
Não faz diferença pesquisar maiúsculo ou minúsculo, mas acentos fazem a direfença.

Na lista, você pode clicar no nome, ou no CPF, e o dado é inserido na barra de pesquisa automaticamente.
Dela é possivel copiar, ou alternando para a aba Aluno, fazer a pesquisa do CPF exato, e ver as 
informações completas do Aluno.

Na aba Lista, clique em pesquisar sem digitar nenhum dado na barra de pesquisa.
Dessa forma é listado todos os cadastros enviados pela academia.

Na barra do Menu é possível salvar no computador a lista completa em arquivo CSV ou  arquivo JSON.
Recomendo salvar na pasta da "Area de Trabalho" ou na pasta de Documentos, para evitar erro.

***No inicio, o programa já verifica todas as linhas arquivo, se alguma linha estiver fora do padrão
ele retorna uma janela de erro com os numeros das linhas erradas. 
    """
    popupajuda = psg.Window('TarifaAgendada', [
        [psg.Frame(title='Ajuda', layout=[[psg.Text(txt)]])], 
        [psg.Exit()]
    ], modal=True, icon="wps.ico")
    evento, valor = popupajuda.read(close=True)
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
        ['Menu',['Salvar', ['Json', 'Txt'], 'Exit']],
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
    return psg.Window('Alunos Academia', layout, icon="wps.ico")

# Função principal do programa
def main():
    # Coleta usuario e senha e checa o retorno
    # USER,  PASSWORD, chk = login()
    # if not chk:
    #     return

    # Cria a janela principal e busca a lista de alunos no ftp
    janela = cria_janela()
    retorno = acessoftp(USER, PASSWORD)

    if not retorno[0]:
        erro = 'ERRO de acesso ao FTP\nVerifique o Login e senha.'
        psg.Popup(erro, title='ERRO', icon="wps.ico", font=6)
        janela.close()
        return
    elif retorno[0]:
        validacao = validaArquivo(retorno[1])
        if not validacao[0]:
            prosseguir = exibeErros(validacao[2])
            if not prosseguir:
                janela.close()
                return
    
    alunos = dicionario(validacao[1])

    # Loop que monitora os eventos da janela
    while True:
        #Leitura dos eventos
        evento, valor = janela.read()

        if evento == '_TABGROUP_':
            if valor['_TABGROUP_'] == '_ALUNO_':
                janela['_RNM_'].Update(disabled=True)
                janela['_RCPF_'].Update(True)
            elif valor['_TABGROUP_'] == '_LISTA_':
                janela['_RNM_'].Update(disabled=False)
                janela['_RNM_'].Update(True)

        # Pesquisa por CPF retornando todos os dados
        elif evento == '_PSQSR_' and valor['_TABGROUP_'] == '_ALUNO_':
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
            listagem = pesquisa(alunos, valor['_INPUT_'], valor['_RCPF_'], valor['_RNM_'], True)
            if not listagem[0]:
                janela['_RPST_'].Update(listagem[1])
                janela['_TABLE_'].Update([])
            else:
                janela['_RPST_'].Update('')    
                janela['_TABLE_'].Update(listagem[1])

        # Codigo que possibilita a copia do nome ou cpf selecionado na lista para a barra de pesquisa
        elif isinstance(evento, tuple):
            try:
                print(listagem)
                tp = evento[2][1]
                if tp == 0:
                    snome = listagem[1][evento[2][0]][0]
                    janela['_INPUT_'].Update(snome)        
                elif tp == 1:
                    print(listagem[1][evento[2][0]][1])
                    scpf = listagem[1][evento[2][0]][1]
                    janela['_INPUT_'].Update(scpf)
            except TypeError:
                pass
            except IndexError:
                pass
            except KeyError:
                pass
            except UnboundLocalError:
                pass
        
        # Funções relativas ás opções do menu
        elif evento == 'Json':
            salvaArquivo(alunos, retorno[2], jso=True)
        elif evento == 'Txt':
            salvaArquivo(validacao[1], retorno[2], txt=True)
        elif evento == 'Ajuda':
            popupAjuda()
        elif evento == 'Sobre...':
            popupSobre()
        elif evento == psg.WIN_CLOSED or evento == 'Exit':
            break 

    janela.close()

if __name__ == '__main__':
    #Variaveis de acesso para teste
    # USER = 'fr_recreioshopping'
    # PASSWORD = 'R3creioshopping@2017'
    USER = 'sf_totalpass'
    PASSWORD = 'T0talpass@2019'
    #Chamada da janela principal
    main()
    