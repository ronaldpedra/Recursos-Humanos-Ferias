# Recursos Humanos - Férias

## Etapas

**1. Configurar o Ambiente Virtual**

Para as etapas de criação do Ambiente Virtual este video pode ajudar: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`

Para criar um ambiente virtual Python no VS Code, abra o terminal integrado (Ctrl+`), navegue até o diretório do seu projeto, execute o comando:

```bash
python -m venv venv
```

O PowerShell vem restrito por padrão, assim ele nega a ativação do Ambiente Virtual. É necessário liberar as permissões. Abra o PowerShell como Administrador e execute o comando:

```bash
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Ative o Ambiente Virtual com `./venv/Scripts/activate` (Windows) ou `source ./venv/bin/activate` (macOS/Linux)

Dê preferência para utilizar o interpretador python que está localizado no ambiente virtual quando o sistema te pedir para escolher um interpretador.

---

**2. Monte a Estrutura de Pastas**

Crie as pastas e arquivos conforme descrito na Fase 1 do Projeto.

Crie o arquivo `requirements.txt` conforme definido no Projeto.

**Instalar as Dependências**

```bash
pip install -r requirements.txt
```

