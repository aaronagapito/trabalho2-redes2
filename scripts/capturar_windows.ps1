# =============================================================================
# Trabalho 2 - Redes de Computadores 2 - Prof. Alessandro Vivas Andrade
# Script que gera automaticamente as capturas dos exercicios 5 a 9 (Windows)
#
# Integrantes: Aaron Araujo Agapito Guedes / Kayky Francisco Rodrigues da Rocha / Gabriel Luiz Fonseca Brandao
#
# Requisito: Wireshark instalado (com o Npcap) em C:\Program Files\Wireshark.
# Como usar: de dois cliques em CAPTURAR.bat e aceite o pedido de administrador.
# A conexao de rede cai por alguns segundos no exercicio 9 (DHCP).
# =============================================================================

# ---- Reabre o script como administrador (necessario para DHCP e telnet) ----
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell.exe -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    exit
}

$raiz = Split-Path -Parent $PSScriptRoot          # pasta do repositorio
Start-Transcript -Path (Join-Path $PSScriptRoot "log_capturas.txt") -Force | Out-Null

function Titulo($texto) {
    Write-Host ""
    Write-Host "==================== $texto ====================" -ForegroundColor Cyan
}

# ---- Instala o Wireshark e o Npcap se ainda nao existirem ----
$dumpcap = Join-Path $env:ProgramFiles "Wireshark\dumpcap.exe"
$temWinget = $null -ne (Get-Command winget.exe -ErrorAction SilentlyContinue)
if (-not (Test-Path $dumpcap)) {
    Titulo "INSTALANDO O WIRESHARK"
    if ($temWinget) {
        winget.exe install -e --id WiresharkFoundation.Wireshark --silent --accept-package-agreements --accept-source-agreements
    } else {
        $instalador = Join-Path $env:TEMP "Wireshark-4.6.9-x64.exe"
        curl.exe -L -o $instalador https://2.na.dl.wireshark.org/win64/Wireshark-4.6.9-x64.exe
        Start-Process -FilePath $instalador -ArgumentList "/S" -Wait
    }
}
$temNpcap = (Test-Path (Join-Path $env:windir "System32\Npcap\wpcap.dll")) -or
            ($null -ne (Get-Service npcap -ErrorAction SilentlyContinue))
if (-not $temNpcap) {
    Titulo "INSTALANDO O NPCAP (clique em I Agree / Install / Finish)"
    # Instalador oficial do Npcap (a versao gratuita so instala com interface grafica)
    $npcapExe = Join-Path $env:TEMP "npcap-1.90.exe"
    curl.exe -L -o $npcapExe https://npcap.com/dist/npcap-1.90.exe
    if (Test-Path $npcapExe) {
        Start-Process -FilePath $npcapExe -Wait
    } else {
        Write-Host "Nao foi possivel baixar o Npcap. Instale em https://npcap.com" -ForegroundColor Yellow
    }
}
if (-not (Test-Path $dumpcap)) {
    Write-Host "Wireshark nao encontrado em $dumpcap" -ForegroundColor Red
    Write-Host "Instale em https://www.wireshark.org/download.html (marque a opcao do Npcap)."
    Stop-Transcript | Out-Null
    Read-Host "Pressione Enter para fechar"
    exit 1
}

# ---- Descobre a placa de rede em uso (a que tem a rota padrao) ----
$rota = Get-NetRoute -DestinationPrefix "0.0.0.0/0" -ErrorAction SilentlyContinue |
        Sort-Object RouteMetric | Select-Object -First 1
if ($null -eq $rota) {
    Write-Host "Sem conexao de rede (nenhuma rota padrao)." -ForegroundColor Red
    Stop-Transcript | Out-Null
    Read-Host "Pressione Enter para fechar"
    exit 1
}
$gateway  = $rota.NextHop
$placa    = Get-NetAdapter -InterfaceIndex $rota.ifIndex
$iface    = "\Device\NPF_" + $placa.InterfaceGuid
$ipv4     = (Get-NetIPAddress -InterfaceIndex $rota.ifIndex -AddressFamily IPv4 | Select-Object -First 1).IPAddress
$dhcpLig  = (Get-NetIPInterface -InterfaceIndex $rota.ifIndex -AddressFamily IPv4).Dhcp -eq "Enabled"
$dnsSrv   = (Get-DnsClientServerAddress -InterfaceIndex $rota.ifIndex -AddressFamily IPv4).ServerAddresses -join ", "

Titulo "REDE"
Write-Host "Placa: $($placa.Name) ($($placa.InterfaceDescription))"
Write-Host "IP: $ipv4 | Gateway: $gateway | DNS: $dnsSrv | DHCP: $dhcpLig"

# ---- Funcao que captura durante N segundos enquanto executa uma acao ----
function Capturar($arquivo, $segundos, $filtro, [scriptblock]$acao) {
    if (Test-Path $arquivo) { Remove-Item $arquivo -Force }
    $argumentos = "-i `"$iface`" -f `"$filtro`" -a duration:$segundos -w `"$arquivo`" -q"
    $proc = Start-Process -FilePath $dumpcap -ArgumentList $argumentos -PassThru -WindowStyle Hidden
    Start-Sleep -Seconds 3                     # espera a captura iniciar
    & $acao
    Write-Host "Aguardando o fim da captura ($segundos s)..."
    $proc.WaitForExit()
    if (Test-Path $arquivo) {
        Write-Host "Salvo: $arquivo ($((Get-Item $arquivo).Length) bytes)" -ForegroundColor Green
    } else {
        Write-Host "ERRO: a captura nao foi gerada." -ForegroundColor Red
    }
}

# ---------------- Exercicio 5 - HTTP ----------------
Titulo "EXERCICIO 5 - HTTP"
Capturar (Join-Path $raiz "exercicio5\captura_http.pcapng") 15 "tcp port 80" {
    curl.exe -s -o NUL -A "Mozilla/5.0" -w "http://www.google.com -> %{http_code}`n" http://www.google.com/
    Start-Sleep -Seconds 1
    curl.exe -s -o NUL -A "Mozilla/5.0" -w "http://example.com -> %{http_code}`n" http://example.com/
}

# ---------------- Exercicio 6 - telnet na porta 80 ----------------
Titulo "EXERCICIO 6 - TELNET"
$telnet = Join-Path $env:windir "System32\telnet.exe"
if (-not (Test-Path $telnet)) {
    Write-Host "Ativando o cliente telnet do Windows (pode levar 1 minuto)..."
    dism.exe /online /Enable-Feature /FeatureName:TelnetClient /NoRestart /Quiet | Out-Null
}
Capturar (Join-Path $raiz "exercicio6\captura_tcp.pcapng") 25 "tcp port 80" {
    if (Test-Path $telnet) {
        # Abre a conexao telnet na porta 80 (three-way handshake) e fecha depois de
        # alguns segundos (encerramento da conexao)
        $t = Start-Process -FilePath $telnet -ArgumentList "example.com 80" -PassThru
        Write-Host "telnet conectado em example.com:80; fechando em 8 segundos..."
        Start-Sleep -Seconds 8
        if (-not $t.HasExited) { Stop-Process -Id $t.Id -Force }
    } else {
        # Plano B: mesma conexao TCP feita pelo PowerShell
        Write-Host "telnet indisponivel; usando conexao TCP do PowerShell."
        $c = New-Object System.Net.Sockets.TcpClient("example.com", 80)
        $s = $c.GetStream()
        $b = [Text.Encoding]::ASCII.GetBytes("GET / HTTP/1.1`r`nHost: example.com`r`nConnection: close`r`n`r`n")
        $s.Write($b, 0, $b.Length)
        Start-Sleep -Seconds 3
        $c.Close()
    }
}

# ---------------- Exercicio 7 - DNS ----------------
Titulo "EXERCICIO 7 - DNS"
ipconfig /flushdns | Out-Null
Capturar (Join-Path $raiz "exercicio7\captura_dns.pcapng") 15 "port 53" {
    Resolve-DnsName www.google.com -Type A    -DnsOnly | Format-Table Name, Type, TTL, IPAddress -AutoSize | Out-String | Write-Host
    Resolve-DnsName www.google.com -Type AAAA -DnsOnly | Format-Table Name, Type, TTL, IPAddress -AutoSize | Out-String | Write-Host
}

# ---------------- Exercicio 8 - ICMP ----------------
Titulo "EXERCICIO 8 - PING NO GATEWAY $gateway"
Capturar (Join-Path $raiz "exercicio8\captura_icmp.pcapng") 20 "icmp" {
    ping.exe -n 10 $gateway
}

# ---------------- Exercicio 9 - DHCP ----------------
Titulo "EXERCICIO 9 - DHCP (a internet cai por alguns segundos)"
if ($dhcpLig) {
    Capturar (Join-Path $raiz "exercicio9\captura_dhcp.pcapng") 45 "port 67 or port 68" {
        ipconfig /release "$($placa.Name)" | Out-Null
        Write-Host "IP liberado. Pedindo um novo..."
        Start-Sleep -Seconds 3
        ipconfig /renew "$($placa.Name)" | Out-Null
        Write-Host "Novo IP: $((Get-NetIPAddress -InterfaceIndex $rota.ifIndex -AddressFamily IPv4 | Select-Object -First 1).IPAddress)"
    }
} else {
    Write-Host "Esta placa usa IP fixo (sem DHCP); exercicio 9 pulado." -ForegroundColor Yellow
}

Titulo "FIM"
Write-Host "Capturas salvas nas pastas exercicio5 a exercicio9." -ForegroundColor Green
Stop-Transcript | Out-Null
Start-Sleep -Seconds 5
