# 🌐 Guia de Configuração da Topologia do Laboratório

Este documento descreve detalhadamente o processo de criação de um ambiente seguro e isolado para testes de auditoria de autenticação e implementação de controles defensivos utilizando o **Oracle VM VirtualBox**.

---

## 🎯 Requisitos de Segurança

1. **Isolamento de Tráfego:** Os testes de autenticação geram tráfego ruidoso e pacotes que jamais devem trafegar pela rede local física (LAN doméstica ou corporativa) nem pela Internet.
2. **Uso de Rede Host-Only (Exclusiva do Hospedeiro):** Garante comunicação estrita entre a máquina auditora (Kali Linux), a máquina vulnerável (Metasploitable 2) e o sistema operacional hospedeiro.

---

## 🖥️ Especificações das Máquinas Virtuais

| Parâmetro | Máquina 1 (Auditora) | Máquina 2 (Alvo Vulnerável) |
| :--- | :--- | :--- |
| **Sistema Operacional** | Kali Linux (Rolling Release) | Metasploitable 2 (Ubuntu 8.04 LTS baseado) |
| **CPU / Memória** | 2 vCPUs / 2048 MB RAM | 1 vCPU / 512 MB - 1024 MB RAM |
| **Modo de Rede** | Adaptador Host-Only (`vboxnet0` ou similar) | Adaptador Host-Only (`vboxnet0` ou similar) |
| **Endereço IPv4** | `192.168.56.10/24` (exemplo) | `192.168.56.20/24` (exemplo) |
| **Serviços Ativos** | Medusa, Nmap, Ferramentas de auditoria | vsftpd (21), Apache/PHP (80), Samba (139/445) |

---

## ⚙️ Configuração Passo a Passo no VirtualBox

### Passo 1: Criar/Verificar a Rede Host-Only no Gerenciador de Rede
1. No VirtualBox, acesse: **Arquivo (File)** > **Ferramentas (Tools)** > **Gerenciador de Rede (Network Manager)**.
2. Na aba **Redes do Hospedeiro (Host-only Networks)**, verifique se existe uma interface criada (comumente `VirtualBox Host-Only Ethernet Adapter` ou `vboxnet0`).
3. Se não existir, clique em **Criar (Create)**.
4. Ajuste as propriedades da interface:
   * **IPv4 Address:** `192.168.56.1`
   * **IPv4 Network Mask:** `255.255.255.0`
   * **Servidor DHCP:** Pode ser mantido ativado ou desativado se optar por IPs estáticos.

### Passo 2: Ajustar a Conexão de Rede nas Máquinas Virtuais
1. Com a VM desligada, clique com o botão direito na VM e vá em **Configurações (Settings)**.
2. Navegue até a aba **Rede (Network)**.
3. No **Adaptador 1**:
   * Marque a opção: **Habilitar Adaptador de Rede**.
   * Em **Conectado a (Attached to)**, selecione: **Placa de rede exclusiva do hospedeiro (Host-only Adapter)**.
   * Em **Nome (Name)**, selecione a interface configurada no Passo 1 (`vboxnet0` ou equivalente).
   * Em **Avançado**: Modo Promíscuo pode ficar em **Recusar (Deny)**.
4. Repita rigorosamente o mesmo processo para a segunda máquina virtual.

---

## 🔍 Validação da Conectividade

Após iniciar ambas as máquinas virtuais, valide o endereçamento e o isolamento:

### 1. Na máquina Metasploitable 2:
```bash
# Verificar endereço IP atribuído
ifconfig eth0
```
*Identifique o IP (exemplo: `192.168.56.20`).*

### 2. Na máquina Kali Linux:
```bash
# Verificar endereço IP da interface
ip a show eth0

# Testar a comunicação bidirecional com a máquina alvo
ping -c 3 192.168.56.20

# Verificar se não há acesso à Internet (garantir isolamento)
ping -c 2 8.8.8.8
# (O comando acima deve falhar ou retornar 'Network is unreachable', comprovando o isolamento)
```

### 3. Validação de Portas Abertas (Varredura Não Intrusiva):
A partir do Kali Linux, execute uma verificação rápida de estado de portas para confirmar os serviços a serem estudados:
```bash
nmap -sS -p 21,80,139,445 192.168.56.20
```

Se as portas 21 (FTP), 80 (HTTP), 139 e 445 (SMB) estiverem em estado `open`, o ambiente está pronto para as etapas de análise conceitual e implementação das defesas.
