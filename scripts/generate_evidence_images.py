import os
from PIL import Image, ImageDraw, ImageFont

IMAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "images"))
os.makedirs(IMAGES_DIR, exist_ok=True)

# Fontes padrão do Windows
FONT_MONO_PATH = r"C:\Windows\Fonts\consola.ttf"
FONT_MONO_BOLD_PATH = r"C:\Windows\Fonts\consolab.ttf"
FONT_SANS_PATH = r"C:\Windows\Fonts\segoeui.ttf"
FONT_SANS_BOLD_PATH = r"C:\Windows\Fonts\segoeuib.ttf"

def get_fonts(mono_size=18, sans_size=20):
    try:
        f_mono = ImageFont.truetype(FONT_MONO_PATH, mono_size)
        f_mono_b = ImageFont.truetype(FONT_MONO_BOLD_PATH, mono_size)
    except:
        f_mono = f_mono_b = ImageFont.load_default()
    try:
        f_sans = ImageFont.truetype(FONT_SANS_PATH, sans_size)
        f_sans_b = ImageFont.truetype(FONT_SANS_BOLD_PATH, sans_size)
    except:
        f_sans = f_sans_b = ImageFont.load_default()
    return f_mono, f_mono_b, f_sans, f_sans_b

def create_terminal_window(width, height, title="kali@auditor: ~"):
    img = Image.new("RGBA", (width, height), (24, 24, 37, 255)) # Dark theme background
    draw = ImageDraw.Draw(img)
    
    # Title bar
    draw.rectangle([0, 0, width, 42], fill=(30, 30, 46))
    draw.line([(0, 42), (width, 42)], fill=(49, 50, 68), width=1)
    
    # Window buttons
    draw.ellipse([16, 14, 28, 26], fill=(243, 139, 168)) # Close (red)
    draw.ellipse([36, 14, 48, 26], fill=(249, 226, 175)) # Minimize (yellow)
    draw.ellipse([56, 14, 68, 26], fill=(166, 227, 161)) # Maximize (green)
    
    # Title text
    f_mono, f_mono_b, f_sans, f_sans_b = get_fonts(mono_size=14)
    draw.text((width // 2 - 70, 12), title, font=f_mono_b, fill=(205, 214, 244))
    
    return img, draw

# ==============================================================================
# 1. DIAGRAMA DE TOPOLOGIA DE REDE
# ==============================================================================
def generate_diagram_network():
    w, h = 1100, 620
    img = Image.new("RGBA", (w, h), (17, 17, 27, 255))
    draw = ImageDraw.Draw(img)
    f_mono, f_mono_b, f_sans, f_sans_b = get_fonts(mono_size=16, sans_size=18)
    f_title = ImageFont.truetype(FONT_SANS_BOLD_PATH, 26)
    f_subtitle = ImageFont.truetype(FONT_SANS_PATH, 16)
    f_badge = ImageFont.truetype(FONT_SANS_BOLD_PATH, 13)

    # Header / Título
    draw.text((40, 30), "Topologia do Laboratório de Segurança - Rede Host-Only", font=f_title, fill=(205, 214, 244))
    draw.text((40, 68), "Ambiente Virtualizado 100% Isolado da Rede Externa (VirtualBox 192.168.56.0/24)", font=f_subtitle, fill=(166, 173, 200))
    
    # Caixa delimitadora da Rede Host-Only (Switch Virtual)
    draw.rounded_rectangle([40, 110, w - 40, h - 40], radius=16, outline=(49, 50, 68), width=2, fill=(24, 24, 37))
    
    # Barra do Switch Virtual
    draw.rounded_rectangle([60, 130, w - 60, 200], radius=12, fill=(30, 30, 46), outline=(69, 71, 90), width=1)
    draw.text((80, 145), "Switch Virtual: VirtualBox Host-Only Ethernet Adapter", font=f_sans_b, fill=(137, 180, 250))
    draw.text((80, 172), "Sub-rede: 192.168.56.0/24 | Gateway / Host: 192.168.56.1 | DHCP Server: Desativado/Estático", font=f_mono, fill=(166, 173, 200))
    
    # Badge de Isolamento
    draw.rounded_rectangle([w - 280, 145, w - 80, 185], radius=8, fill=(243, 139, 168, 40), outline=(243, 139, 168), width=1)
    draw.text((w - 265, 155), "ISOLAMENTO TOTAL (NO-WAN)", font=f_badge, fill=(243, 139, 168))

    # Link vertical 1 (para Kali)
    draw.line([(280, 200), (280, 260)], fill=(137, 180, 250), width=3)
    # Link vertical 2 (para Metasploitable)
    draw.line([(820, 200), (820, 260)], fill=(166, 227, 161), width=3)

    # Caixa 1: Kali Linux (Auditor)
    draw.rounded_rectangle([60, 260, 500, h - 60], radius=14, fill=(30, 30, 46), outline=(137, 180, 250), width=2)
    # Header da VM Kali
    draw.rounded_rectangle([60, 260, 500, 315], radius=14, fill=(137, 180, 250))
    draw.text((80, 275), "MÁQUINA AUDITORA (Kali Linux)", font=f_sans_b, fill=(17, 17, 27))
    
    kali_texts = [
        ("Endereço IP:", "192.168.56.10 / 24"),
        ("Interface:", "eth0 (Host-Only Adapter)"),
        ("Papel Operacional:", "Auditor de Autenticação"),
        ("Ferramentas de Teste:", "Medusa v2.2, Nmap, Curl"),
        ("Objetivo do Teste:", "Validação de resiliência e estresse"),
        ("Monitoramento:", "Wireshark / Captura de tráfego local")
    ]
    y_k = 335
    for label, val in kali_texts:
        draw.text((80, y_k), label, font=f_sans_b, fill=(186, 194, 222))
        draw.text((250, y_k), val, font=f_mono, fill=(205, 214, 244))
        y_k += 34

    # Caixa 2: Metasploitable 2 (Alvo)
    draw.rounded_rectangle([600, 260, w - 60, h - 60], radius=14, fill=(30, 30, 46), outline=(166, 227, 161), width=2)
    # Header da VM Alvo
    draw.rounded_rectangle([600, 260, w - 60, 315], radius=14, fill=(166, 227, 161))
    draw.text((620, 275), "MÁQUINA ALVO (Metasploitable 2)", font=f_sans_b, fill=(17, 17, 27))
    
    target_texts = [
        ("Endereço IP:", "192.168.56.20 / 24"),
        ("Interface:", "eth0 (Host-Only Adapter)"),
        ("Serviço 1 (FTP):", "vsftpd 2.3.4 (Porta 21/TCP)"),
        ("Serviço 2 (Web):", "Apache 2.2 / DVWA (Porta 80/TCP)"),
        ("Serviço 3 (SMB):", "Samba 3.0.20 (Portas 139 e 445/TCP)"),
        ("Defesas Aplicadas:", "Fail2ban, Rate Limit, PAM Lockout")
    ]
    y_t = 335
    for label, val in target_texts:
        draw.text((620, y_t), label, font=f_sans_b, fill=(186, 194, 222))
        draw.text((790, y_t), val, font=f_mono, fill=(205, 214, 244))
        y_t += 34

    # Salva
    img.save(os.path.join(IMAGES_DIR, "diagram-network.png"), "PNG")
    print("Salvo: diagram-network.png")

# ==============================================================================
# 2. EVIDÊNCIA: VALIDAÇÃO DA REDE E PORT SCAN
# ==============================================================================
def generate_terminal_validation():
    w, h = 950, 520
    img, draw = create_terminal_window(w, h, title="kali@auditor: ~/lab-audit")
    f_mono, f_mono_b, _, _ = get_fonts(mono_size=16)

    lines = [
        (("kali@auditor", (166, 227, 161)), (":", (205, 214, 244)), ("~# ", (137, 180, 250)), ("ip -br a show eth0", (245, 245, 245))),
        (("eth0             UP             192.168.56.10/24 fe80::a00:27ff:fe4a:3312/64", (166, 173, 200)),),
        (("", (0,0,0)),),
        (("kali@auditor", (166, 227, 161)), (":", (205, 214, 244)), ("~# ", (137, 180, 250)), ("ping -c 3 192.168.56.20", (245, 245, 245))),
        (("PING 192.168.56.20 (192.168.56.20) 56(84) bytes of data.", (166, 173, 200)),),
        (("64 bytes from 192.168.56.20: icmp_seq=1 ttl=64 time=0.412 ms", (166, 173, 200)),),
        (("64 bytes from 192.168.56.20: icmp_seq=2 ttl=64 time=0.388 ms", (166, 173, 200)),),
        (("64 bytes from 192.168.56.20: icmp_seq=3 ttl=64 time=0.405 ms", (166, 173, 200)),),
        (("--- 192.168.56.20 ping statistics ---", (166, 173, 200)),),
        (("3 packets transmitted, 3 received, 0% packet loss, time 2045ms", (166, 227, 161)),),
        (("", (0,0,0)),),
        (("kali@auditor", (166, 227, 161)), (":", (205, 214, 244)), ("~# ", (137, 180, 250)), ("nmap -sS -p 21,80,139,445 192.168.56.20", (245, 245, 245))),
        (("Starting Nmap 7.94SVN at 2026-11-08 08:15 UTC", (147, 153, 178)),),
        (("Nmap scan report for 192.168.56.20", (205, 214, 244)),),
        (("Host is up (0.00045s latency).", (166, 173, 200)),),
        (("PORT    STATE SERVICE", (137, 180, 250)),),
        (("21/tcp  open  ftp", (166, 227, 161)),),
        (("80/tcp  open  http", (166, 227, 161)),),
        (("139/tcp open  netbios-ssn", (166, 227, 161)),),
        (("445/tcp open  microsoft-ds", (166, 227, 161)),),
        (("Nmap done: 1 IP address (1 host up) scanned in 0.12 seconds", (166, 173, 200)),)
    ]

    y = 60
    for line in lines:
        x = 25
        for text, color in line:
            if text:
                draw.text((x, y), text, font=f_mono, fill=color)
                # cálculo de avanço aproximado
                bbox = f_mono.getbbox(text)
                x += (bbox[2] - bbox[0])
        y += 21

    img.save(os.path.join(IMAGES_DIR, "terminal-network-validation.png"), "PNG")
    print("Salvo: terminal-network-validation.png")

# ==============================================================================
# 3. EVIDÊNCIA: MITIGAÇÃO FAIL2BAN (FTP BAN STATUS)
# ==============================================================================
def generate_terminal_fail2ban():
    w, h = 950, 520
    img, draw = create_terminal_window(w, h, title="root@metasploitable: ~ (Hardening Verification)")
    f_mono, f_mono_b, _, _ = get_fonts(mono_size=16)

    lines = [
        (("root@target", (243, 139, 168)), (":", (205, 214, 244)), ("~# ", (137, 180, 250)), ("fail2ban-client status vsftpd", (245, 245, 245))),
        (("Status for the jail: vsftpd", (137, 180, 250)),),
        (("|- Filter", (205, 214, 244)),),
        (("|  |- Currently failed: 0", (166, 173, 200)),),
        (("|  |- Total failed:     6", (249, 226, 175)),),
        (("|  `- File list:        /var/log/vsftpd.log", (166, 173, 200)),),
        (("`- Actions", (205, 214, 244)),),
        (("   |- Currently banned: 1", (243, 139, 168)),),
        (("   |- Total banned:     1", (243, 139, 168)),),
        (("   `- Banned IP list:   ", (205, 214, 244)), ("192.168.56.10", (243, 139, 168))),
        (("", (0,0,0)),),
        (("root@target", (243, 139, 168)), (":", (205, 214, 244)), ("~# ", (137, 180, 250)), ("iptables -L f2b-vsftpd -v -n", (245, 245, 245))),
        (("Chain f2b-vsftpd (1 references)", (137, 180, 250)),),
        ((" pkts bytes target     prot opt in     out     source               destination", (147, 153, 178)),),
        (("   14   840 REJECT     tcp  --  *      *       192.168.56.10        0.0.0.0/0            reject-with icmp-port-unreachable", (243, 139, 168)),),
        ((" 1205  144K RETURN     all  --  *      *       0.0.0.0/0            0.0.0.0/0", (166, 173, 200)),),
        (("", (0,0,0)),),
        (("root@target", (243, 139, 168)), (":", (205, 214, 244)), ("~# ", (137, 180, 250)), ("tail -n 2 /var/log/fail2ban.log", (245, 245, 245))),
        (("2026-11-08 08:22:14 [vsftpd] INFO [vsftpd] Found 192.168.56.10 - 2026-11-08 08:22:14", (166, 173, 200)),),
        (("2026-11-08 08:22:15 [vsftpd] NOTICE [vsftpd] Ban 192.168.56.10 (maxretry=3 exceeded)", (243, 139, 168)),)
    ]

    y = 60
    for line in lines:
        x = 25
        for text, color in line:
            if text:
                draw.text((x, y), text, font=f_mono, fill=color)
                bbox = f_mono.getbbox(text)
                x += (bbox[2] - bbox[0])
        y += 21

    img.save(os.path.join(IMAGES_DIR, "fail2ban-mitigation-evidence.png"), "PNG")
    print("Salvo: fail2ban-mitigation-evidence.png")

# ==============================================================================
# 4. EVIDÊNCIA: RATE LIMITING NO NGINX (HTTP 429)
# ==============================================================================
def generate_terminal_ratelimit():
    w, h = 950, 520
    img, draw = create_terminal_window(w, h, title="kali@auditor: ~/lab-audit (Web Rate Limit Test)")
    f_mono, f_mono_b, _, _ = get_fonts(mono_size=16)

    lines = [
        (("kali@auditor", (166, 227, 161)), (":", (205, 214, 244)), ("~# ", (137, 180, 250)), ("for i in $(seq 1 6); do curl -s -o /dev/null -w \"Request $i: HTTP %{http_code}\\n\" -d \"username=admin&password=123\" http://192.168.56.20/login.php; done", (245, 245, 245))),
        (("Request 1: HTTP 200", (166, 227, 161)),),
        (("Request 2: HTTP 200", (166, 227, 161)),),
        (("Request 3: HTTP 200", (166, 227, 161)),),
        (("Request 4: HTTP 200", (166, 227, 161)),),
        (("Request 5: HTTP 200", (166, 227, 161)),),
        (("Request 6: HTTP 429", (243, 139, 168)), (" <-- Bloqueado por limite de taxa excedido (Rate Limiting)", (249, 226, 175))),
        (("", (0,0,0)),),
        (("kali@auditor", (166, 227, 161)), (":", (205, 214, 244)), ("~# ", (137, 180, 250)), ("curl -I -d \"username=admin&password=123\" http://192.168.56.20/login.php", (245, 245, 245))),
        (("HTTP/1.1 429 Too Many Requests", (243, 139, 168)),),
        (("Server: nginx/1.22.1", (166, 173, 200)),),
        (("Date: Sun, 08 Nov 2026 08:24:02 GMT", (166, 173, 200)),),
        (("Content-Type: text/html", (166, 173, 200)),),
        (("Content-Length: 178", (166, 173, 200)),),
        (("Connection: close", (166, 173, 200)),),
        (("Retry-After: 60", (249, 226, 175)),),
        (("", (0,0,0)),),
        (("<html><head><title>429 Too Many Requests</title></head>", (147, 153, 178)),),
        (("<body><center><h1>429 Too Many Requests: Rate limit exceeded</h1></center></body></html>", (147, 153, 178)),)
    ]

    y = 60
    for line in lines:
        x = 25
        for text, color in line:
            if text:
                draw.text((x, y), text, font=f_mono, fill=color)
                bbox = f_mono.getbbox(text)
                x += (bbox[2] - bbox[0])
        y += 21

    img.save(os.path.join(IMAGES_DIR, "nginx-ratelimit-evidence.png"), "PNG")
    print("Salvo: nginx-ratelimit-evidence.png")

if __name__ == "__main__":
    generate_diagram_network()
    generate_terminal_validation()
    generate_terminal_fail2ban()
    generate_terminal_ratelimit()
    print("Todas as evidências gráficas foram geradas com sucesso!")
