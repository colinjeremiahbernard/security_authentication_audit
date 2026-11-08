# 🛡️ Guia Completo de Mitigação, Hardening e Defesa Ativa

Este guia reúne as implementações práticas, regras de configuração e políticas de segurança necessárias para neutralizar os vetores de ataque avaliados nos cenários de **FTP**, **Aplicações Web** e **SMB**.

---

## 1. Hardening e Proteção para o Serviço FTP

### A. Substituição Tecnológica por SFTP (Recomendação Primária)
Sempre que possível, o protocolo FTP legado deve ser desativado em favor do **SFTP** (SSH File Transfer Protocol), que garante:
* Criptografia ponta a ponta (AES-GCM / ChaCha20-Poly1305).
* Autenticação baseada em chaves públicas assimétricas (Ed25519), eliminando a vulnerabilidade a dicionários de senhas fracas.

### B. Ajustes no Arquivo de Configuração do vsftpd (`/etc/vsftpd.conf`)
Caso o uso de FTP seja estritamente indispensável, aplique as diretivas abaixo:

```ini
# Desabilitar acesso anônimo
anonymous_enable=NO

# Forçar encriptação via TLS/SSL (FTPS)
ssl_enable=YES
allow_anon_ssl=NO
force_local_data_ssl=YES
force_local_logins_ssl=YES
ssl_tlsv1=YES
ssl_sslv2=NO
ssl_sslv3=NO

# Limitação de concorrência e conexões por IP
max_clients=15
max_per_ip=2

# Limite de tentativas de login por sessão antes de desconectar
max_login_fails=3
```

### C. Implementação do Fail2ban para FTP
O Fail2ban analisa os logs de auditoria em tempo real e adiciona regras dinâmicas no firewall para bloquear o atacante:

1. Instale o pacote:
   ```bash
   sudo apt update && sudo apt install fail2ban -y
   ```
2. Crie a regra específica em `/etc/fail2ban/jail.d/vsftpd.local` (consulte o arquivo modelo em `configs/fail2ban-vsftpd.local`).
3. Reinicie o serviço:
   ```bash
   sudo systemctl restart fail2ban
   sudo fail2ban-client status vsftpd
   ```

---

## 2. Hardening e Proteção para Aplicações Web (DVWA / Portais)

### A. Rate Limiting via Proxy Reverso (Nginx)
Adicionar uma camada de proxy reverso com controle de taxa de requisições impede que ferramentas de força bruta automatizadas testem credenciais em massa:

```nginx
# Define uma zona de memória compartilhada para rastrear IPs (10MB armazenam ~160.000 IPs)
# Limita o acesso ao endpoint de login a no máximo 5 requisições por minuto
limit_req_zone $binary_remote_addr zone=login_limit:10m rate=5r/m;

server {
    listen 80;
    server_name dvwa.local;

    location /login.php {
        # Aplica a zona de limite com tolerância a rajadas de 2 requisições
        limit_req zone=login_limit burst=2 nodelay;
        limit_req_status 429; # Retorna HTTP 429 Too Many Requests

        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### B. Defesas em Nível de Código e Arquitetura
1. **Desafios Anti-Robô (CAPTCHA / Proof-of-Work):**
   * Ativar desafios após 2 tentativas incorretas para a mesma sessão/IP.
2. **Tokens Anti-CSRF:**
   * Garantir que cada requisição de login exija um token criptográfico único gerado na sessão do usuário, dificultando requisições em lote por clientes HTTP simples.
3. **Respostas Genéricas:**
   * Evitar mensagens como *"Usuário inexistente"* ou *"Senha incorreta"*. Utilize sempre: *"Credenciais inválidas"*.
4. **Atraso Exponencial (Exponential Backoff):**
   * Inserir pausas programadas no código backend (`sleep(attempts * 2)`) para cada falha consecutiva.
5. **Autenticação Multifator (MFA):**
   * Implementação obrigatória de TOTP (Time-Based One-Time Password) ou chaves FIDO2/WebAuthn.

---

## 3. Hardening para SMB e Ambientes Corporativos (Active Directory / Samba)

### A. Desativação de Sessões Nulas (Null Sessions)
Para impedir a enumeração de contas sem autenticação:

* **No Linux (Samba - `/etc/samba/smb.conf`):**
  ```ini
  [global]
  restrict anonymous = 2
  map to guest = never
  usershare allow guests = no
  ```
* **No Windows (Registro / GPO):**
  Definir a chave `HKLM\SYSTEM\CurrentControlSet\Control\Lsa\RestrictAnonymous` com o valor `1` ou `2`.

### B. Desativação do SMBv1
O protocolo SMBv1 é inerentemente vulnerável e deve ser inteiramente suprimido:
* No Samba:
  ```ini
  [global]
  min protocol = SMB2
  client min protocol = SMB2
  ```

### C. Configuração de Política de Bloqueio de Contas (Account Lockout Policy)
Uma política balanceada é indispensável para conter força bruta direta:
* **Limiar de bloqueio:** 5 tentativas incorretas.
* **Duração do bloqueio:** 15 a 30 minutos.
* **Janela de redefinição do contador:** 15 minutos.

> ⚠️ **Atenção:** Em ataques de *Password Spraying*, o atacante testa 1 senha a cada período superior à janela de redefinição para evitar esse bloqueio. Por isso, a política de bloqueio deve ser combinada com detecção de anomalias no SIEM.

### D. Bloqueio no Linux via Módulo PAM (`pam_faillock`)
Em sistemas operacionais Linux modernos, o módulo `pam_faillock` é utilizado para bloquear contas locais após tentativas consecutivas inválidas (consulte `configs/pam_lockout.conf`).

---

## 4. Monitoramento e Detecção Ativa (SIEM & Logs)

A prevenção é potencializada por um monitoramento capaz de identificar assinaturas comportamentais:

### Indicadores de Comprometimento (IoCs) a Monitorar:
1. **Picos de Falha em Múltiplos Usuários (Password Spraying):**
   * **Windows Event Log:** Monitorar o **Event ID 4625** (*An account failed to log on*). Criar alerta quando um mesmo endereço IP de origem gerar falhas em 5 ou mais contas de usuários distintas em uma janela de 10 minutos.
2. **Saturação de Conexões Concorrentes:**
   * Múltiplas conexões originadas do mesmo IP para as portas 21, 22 ou 445 em milissegundos indicam uso de ferramentas com múltiplos threads (ex: Medusa, Hydra).
3. **Logs do Linux (`/var/log/auth.log`):**
   * Padrões como `Failed password for ... from 192.168.56.X` em rápida sucessão.
