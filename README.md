# Sistema de Controle de Estoque

Um sistema completo para controle de estoque, desenvolvido com foco em performance, usabilidade e capacidade para gerenciar grandes volumes de dados (20.000+ itens).

## Características Principais

- **Interface Minimalista**: Design limpo e intuitivo, otimizado para performance
- **Gerenciamento de Produtos**: Cadastro, edição, exclusão e pesquisa avançada
- **Controle de Estoque**: Registro de entradas e saídas com histórico completo
- **Sistema de Permissões**: Níveis de acesso diferenciados (administrador, operador)
- **Sistema de Solicitações**: Fluxo de aprovação para retiradas de estoque
- **Relatórios e Exportação**: Exportação de dados em formato CSV
- **Alta Performance**: Otimizado para lidar com 20.000+ itens sem travamentos

## Requisitos do Sistema

- Python 3.8+
- Pip (gerenciador de pacotes Python)
- SQLite (desenvolvimento) ou PostgreSQL (produção)

## Configuração do Ambiente no PyCharm

### 1. Clonar o Repositório

1. Abra o PyCharm
2. Selecione "Get from VCS" na tela inicial ou "File > New > Project from Version Control"
3. Cole a URL do repositório e clique em "Clone"

### 2. Configurar o Ambiente Virtual

1. Abra o terminal do PyCharm (View > Tool Windows > Terminal)
2. Navegue até a pasta do projeto (se necessário)
3. Crie um ambiente virtual:
   ```
   python -m venv venv
   ```
4. Ative o ambiente virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
5. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

### 3. Configurar o PyCharm para Usar o Ambiente Virtual

1. Vá para "File > Settings" (Windows/Linux) ou "PyCharm > Preferences" (Mac)
2. Navegue até "Project: estoque > Python Interpreter"
3. Clique na engrenagem e selecione "Add..."
4. Escolha "Existing Environment" e selecione o interpretador Python dentro da pasta `venv`
   - Windows: `venv\Scripts\python.exe`
   - Linux/Mac: `venv/bin/python`
5. Clique em "OK" para salvar

### 4. Configurar a Execução do Projeto

1. Vá para "Run > Edit Configurations..."
2. Clique no "+" e selecione "Python"
3. Configure:
   - Name: `Flask Run`
   - Script path: Selecione o arquivo `src/main.py`
   - Python interpreter: Selecione o interpretador do ambiente virtual
   - Working directory: Selecione a pasta raiz do projeto
4. Clique em "OK" para salvar

## Inicialização do Sistema

### Primeira Execução

1. No terminal do PyCharm (com ambiente virtual ativado), execute:
   ```
   python src/main.py
   ```
   Ou use a configuração de execução criada anteriormente.

2. O sistema inicializará o banco de dados e criará um usuário administrador padrão:
   - Usuário: `admin`
   - Senha: `admin`

3. Acesse o sistema em seu navegador: `http://localhost:5000`

4. **Importante**: Altere a senha do administrador após o primeiro login por questões de segurança.

## Estrutura do Projeto

```
estoque/
├── src/                      # Código-fonte principal
│   ├── static/               # Arquivos estáticos
│   │   ├── css/              # Estilos CSS
│   │   ├── js/               # Scripts JavaScript
│   │   └── img/              # Imagens e ícones
│   ├── templates/            # Templates HTML
│   ├── models/               # Modelos de dados
│   ├── controllers/          # Controladores/rotas
│   ├── utils/                # Utilitários
│   └── main.py               # Ponto de entrada da aplicação
├── migrations/               # Migrações de banco de dados
├── tests/                    # Testes automatizados
├── requirements.txt          # Dependências do projeto
└── README.md                 # Documentação
```

## Funcionalidades Detalhadas

### Gerenciamento de Produtos

- Cadastro de produtos com código, nome, quantidade, categoria e descrição
- Edição e exclusão de produtos
- Pesquisa avançada com filtros por código, nome, categoria e quantidade
- Visualização de produtos com indicadores visuais de estoque

### Controle de Estoque

- Registro de entradas e saídas de produtos
- Histórico completo de movimentações
- Filtros por data, tipo de movimentação e produto
- Exportação de relatórios de movimentação

### Sistema de Permissões

- **Administrador**: Acesso completo a todas as funcionalidades
- **Operador**: Acesso limitado (sem exclusão de produtos)
- **Usuário Comum**: Apenas visualização e solicitações

### Sistema de Solicitações

- Usuários podem solicitar produtos do estoque
- Administradores aprovam ou recusam solicitações
- Histórico completo de solicitações
- Atualização automática do estoque após aprovação

## Otimizações para Alta Performance

O sistema foi otimizado para lidar com grandes volumes de dados (20.000+ itens) através de:

1. **Paginação Eficiente**: Todas as listagens implementam paginação
2. **Índices Otimizados**: Campos de busca frequente possuem índices
3. **Consultas Otimizadas**: Queries SQL eficientes e parametrizadas
4. **Carregamento Assíncrono**: Uso de AJAX para operações que não exigem refresh completo
5. **Interface Minimalista**: Redução de elementos visuais pesados
6. **Minificação de Recursos**: CSS e JavaScript otimizados

## Migração para Ambiente de Produção

Para migrar o sistema para um servidor de produção:

1. **Banco de Dados**:
   - Configure a variável de ambiente `DATABASE_URL` para apontar para seu PostgreSQL
   - Execute as migrações no novo banco de dados

2. **Configurações de Segurança**:
   - Defina uma chave secreta forte na variável de ambiente `SECRET_KEY`
   - Desative o modo debug (`debug=False` em `main.py`)
   - Configure HTTPS no servidor web

3. **Servidor Web**:
   - Use Gunicorn ou uWSGI como servidor WSGI
   - Configure um proxy reverso (Nginx ou Apache)
   - Exemplo de comando Gunicorn:
     ```
     gunicorn -w 4 -b 0.0.0.0:8000 "src.main:app"
     ```

## Solução de Problemas

### Erro de Conexão com Banco de Dados

Verifique se o arquivo do banco de dados SQLite existe e tem permissões corretas, ou se as credenciais do PostgreSQL estão corretas nas variáveis de ambiente.

### Erro ao Iniciar o Servidor

Certifique-se de que a porta 5000 não está sendo usada por outro processo. Você pode alterar a porta no arquivo `main.py`.

### Problemas de Performance

Se o sistema estiver lento com grandes volumes de dados:

1. Execute a rota de otimização do banco: `/utils/otimizar_db` (requer login de administrador)
2. Verifique se os índices foram criados corretamente
3. Aumente o valor de paginação se necessário (padrão: 20 itens por página)

## Segurança

- Todas as senhas são armazenadas com hash seguro (bcrypt)
- Proteção contra CSRF em todos os formulários
- Validação de entrada em todos os campos
- Escape adequado de dados em templates para prevenir XSS

## Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## Contato e Suporte

Para suporte ou dúvidas, entre em contato através do email: suporte@controleestoque.com
