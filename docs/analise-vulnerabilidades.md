# 🔬 Análise Técnica de Vulnerabilidades de Autenticação

Este documento detalha o funcionamento interno, os riscos arquiteturais e os comportamentos dos três protocolos/serviços analisados neste projeto: **FTP**, **Web (HTTP/Formulário)** e **SMB**.

---

## 1. Cenário 1: Protocolo FTP (File Transfer Protocol)

### 📌 Mecanismo de Funcionamento
O FTP opera sobre a porta TCP 21 para canal de comando, conforme definido na **RFC 959**. A autenticação ocorre através de uma troca sequencial síncrona em texto claro:

1. O cliente estabelece conexão TCP de 3 vias (*3-Way Handshake*).
2. O servidor envia banner de boas-vindas (`220 (vsFTPd 2.3.4)`).
3. O cliente envia o comando: `USER <nome_usuario>`.
4. O servidor responde: `331 Please specify the password.`
5. O cliente envia o comando: `PASS <senha>`.
6. O servidor valida as credenciais contra a base de usuários do sistema (`/etc/passwd` e `/etc/shadow`) e responde:
   * `230 Login successful.` (Sucesso)
   * `530 Login incorrect.` (Falha)

```
Cliente Auditor                                     Servidor FTP (vsftpd)
       |                                                      |
       | ------------ SYN ----------------------------------> |
       | <----------- SYN/ACK ------------------------------- |
       | ------------ ACK ----------------------------------> |
       | <----------- 220 Welcome Banner -------------------- |
       | ------------ USER alice ---------------------------> |
       | <----------- 331 Please specify password ----------- |
       | ------------ PASS password123 ---------------------> |
       | <----------- 530 Login incorrect ------------------- |
```

### ⚠️ Vulnerabilidades Identificadas
* **Ausência de Criptografia:** Todas as credenciais trafegam sem proteção criptográfica na camada de transporte.
* **Falta de Rate Limiting e Backoff:** Em sua configuração padrão legada, o daemon não impõe atrasos progressivos (*exponential backoff*) entre respostas de erro, nem bloqueia conexões sequenciais da mesma origem.
* **Processamento Paralelo Desprotegido:** Servidores sem ajuste de `max_per_ip` permitem que múltiplas threads simultâneas realizem tentativas contínuas sem degradação perceptível.

---

## 2. Cenário 2: Autenticação Web (DVWA - Damn Vulnerable Web App)

### 📌 Mecanismo de Funcionamento
A autenticação web tradicional em formulários HTML baseia-se no envio de dados via método HTTP `POST` ou `GET` para um script backend (neste caso, PHP) que consulta uma base de dados relacional.

No formulário do DVWA (nível *Low*):
* Os parâmetros de submissão são tipicamente: `username`, `password` e `Login=Login`.
* O processamento compara a hash da senha fornecida com o banco MySQL subjacente.
* Respostas de sucesso redirecionam o usuário ou emitem cookie de sessão (`PHPSESSID`).
* Respostas de falha recarregam a página com texto de erro (*"Login failed"*).

```
Cliente (Navegador/Auditor)                           Servidor Apache (PHP/DVWA)
       |                                                           |
       | --- POST /login.php HTTP/1.1 (user=admin&pass=123456) --> |
       | <--- HTTP/1.1 200 OK ("Login failed") ------------------- |
       |                                                           |
       | --- POST /login.php HTTP/1.1 (user=admin&pass=password) > |
       | <--- HTTP/1.1 302 Found (Set-Cookie: PHPSESSID=...) ----- |
```

### ⚠️ Vulnerabilidades Identificadas
* **Ausência de Desafios Interativos (CAPTCHA):** O endpoint não exige validação humana em nenhum momento do ciclo de tentativas.
* **Falta de Tokens Anti-Automação / Anti-CSRF:** Não há tokens de uso único (*nonce*) atrelados ao formulário nos níveis básicos, simplificando o envio automatizado de requisições por ferramentas de script.
* **Ausência de Limitação de Requisições por IP:** O servidor web processa quantas requisições por segundo a CPU/rede suportarem, sem devolver códigos HTTP `429 Too Many Requests`.

---

## 3. Cenário 3: Serviço SMB (Server Message Block) e Password Spraying

### 📌 Mecanismo de Funcionamento
O protocolo SMB (portas 139 e 445/TCP) é amplamente utilizado para compartilhamento de arquivos, serviços de diretório e comunicação entre processos (IPC$). A autenticação envolve o protocolo de desafio-resposta NTLM ou Kerberos.

#### Enumeração de Usuários via Null Sessions
Em implementações SMB legadas (como as presentes no Metasploitable 2), o recurso de **sessão nula** permite conexões anônimas ao recurso especial `IPC$` (Inter-Process Communication):
* Usuário vazio (`""`) e senha vazia (`""`).
* Uma vez conectada, a sessão permite consultas via chamadas RPC (como a interface `SAMR` - Security Account Manager Remote) para listar a relação de contas de usuários locais e grupos existentes no sistema.

#### Dinâmica de Password Spraying
Ao contrário do ataque de força bruta tradicional (onde um único usuário recebe milhares de tentativas de senhas), o **Password Spraying** subverte a lógica tradicional de defesa:

```
[Força Bruta Convencional]
  Usuário: admin
  Tentativas: senha1, senha2, senha3, senha4, senha5 -> [BLOQUEIO DE CONTA ACIONADO]

[Password Spraying]
  Senha Única: "Empresa@2024"
  Tentativas:
    - usuario01 + "Empresa@2024" (1 falha)
    - usuario02 + "Empresa@2024" (1 falha)
    - usuario03 + "Empresa@2024" (Sucesso!)
    -> Nenhuma conta individual atinge o limiar de bloqueio (ex: 3 ou 5 falhas).
```

### ⚠️ Vulnerabilidades Identificadas
* **Exposição de Informações por Sessão Nula:** Permite a um invasor enumerar previamente toda a base de usuários válidos sem autenticação.
* **Senhas Padronizadas e Fracas:** A cultura de senhas corporativas fracas (ex: `NomeEmpresa@Ano`, `Mudar123`) torna o password spraying devastadoramente eficaz em ambientes sem MFA.
* **Evasão de Controles Locais:** Políticas de bloqueio de conta configuradas puramente por usuário não detectam a origem maliciosa se o número de tentativas por conta individual permanecer abaixo da margem de bloqueio.

---

## 🛠️ Arquitetura das Ferramentas de Auditoria (Exemplo: Medusa)

O **Medusa** é um auditor de força bruta paralelo e modular que se destaca pelo seguinte design:

1. **Estrutura Modular (`.mod`):** Cada protocolo possui uma biblioteca dedicada de comunicação (ex: `ftp.mod`, `web-form.mod`, `smbnt.mod`).
2. **Modelo Baseado em POSIX Threads (`pthread`):** Permite disparar dezenas de conexões concorrentes sem o overhead de criação de novos processos.
3. **Mecanismo de Retentativas e Timeouts:** Capaz de renegociar timeouts e reagir a quedas transitórias de conexão causadas pela saturação do servidor.
4. **Parâmetros Operacionais Estruturais:**
   * `-h <alvo>`: Define o endereço do host.
   * `-u <usuario>` ou `-U <arquivo>`: Define um usuário específico ou a lista enumerada.
   * `-p <senha>` ou `-P <arquivo>`: Define uma senha isolada (ideal para password spraying) ou um dicionário.
   * `-M <módulo>`: Seleciona o protocolo a ser exercitado.
   * `-n <porta>`: Altera a porta padrão de comunicação se necessário.

A compreensão desse modelo de operação é fundamental para projetar contra-ataques defensivos eficientes, como sistemas de detecção que identifiquem a assinatura comportamental dessas ferramentas (saturação de threads, alta taxa de erros síncronos e repetição de padrões).
