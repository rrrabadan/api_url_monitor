import os
import requests
import datetime
import time
import socket
import sys
import json
import pathlib

ENTER_URL = "Digite a URL ou API que deseja verificar: "
ENTER_TIMEOUT = "Digite o tempo de timeout em segundos: "
INVALID_HOST = "Host inválido. Por favor, informe um novo host."
REQUEST_ERROR = "Erro ao solicitar a URL. Por favor, informe uma nova URL."
SAVE_SUCCESS = "Arquivo salvo em:"

LOG_FILE_NAME = "log.txt"
LOG_MAX_SIZE = 1000000  # 1 MB
LOG_ROTATE_DAYS = 1

TIMEOUT = 5

def get_status(url, timeout):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    try:
        response = requests.get(url, timeout=timeout)
        status = response.status_code
        response_time = response.elapsed.microseconds / 1000
        try:
            response_content = json.dumps(response.json())
        except ValueError:
            response_content = "retorno não é um JSON válido"
        return status, response_time, response_content
    except requests.exceptions.RequestException as e:
        print(f"{REQUEST_ERROR} {url}: {e}")
        return None, None

def get_ip(url):
    try:
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException as e:
            print("Ocorreu uma exceção:", e)
            return None
        ip = socket.gethostbyname(response.url.split('/')[2])
        return ip
    except socket.gaierror:
        print(INVALID_HOST)
        print(url)
        return None

def save(data, log_file):
    log_path = pathlib.Path(log_file)
    if not log_path.exists():
        with log_path.open("w") as file:
            file.write("Data Hora,URL,Endereço IP,Código de Status,Tempo de Resposta,Tempo de Resposta Médio\n")
    with log_path.open("a") as file:
        file.write(data + "\n")

    # Verifica o tamanho do arquivo de log e faz rotação se necessário
    if log_path.stat().st_size > LOG_MAX_SIZE:
        rotate_logs(log_file)
    
    print(f"{SAVE_SUCCESS} {log_path.resolve()}\n")

def rotate_logs(log_file):
    log_path = pathlib.Path(log_file)
    log_dir = log_path.parent
    log_base = log_path.name

    # Cria um novo arquivo de log com a data atual
    log_date = datetime.date.today().strftime("%Y-%m-%d")
    new_log_name = f"{log_base}.{log_date}"
    new_log_path = log_dir / new_log_name
    with new_log_path.open("w") as file:
        file.write("Data Hora,URL,Endereço IP,Código de Status,Tempo de Resposta,Tempo de Resposta Médio\n")

    # Renomeia os arquivos de log antigos para incluir a data correspondente
    for old_log_path in log_dir.glob(f"{log_base}.*"):
        if old_log_path != new_log_path:
            old_log_date = old_log_path.suffix[1:]
            new_name = f"{log_base}.{old_log_date}"
            new_path = log_dir / new_name
            old_log_path.replace(new_path)

def print_bar(iteration, response_times):
    response_times = [int(float(x)) for x in response_times if x is not None]
    max_response_time = max(response_times) if response_times else 0
    min_response_time = min(response_times) if response_times else 0
    bar_length = max(max_response_time - min_response_time, 1)
    max_bar_length = min(12, bar_length)
    unit = bar_length // max_bar_length
    print("Iteração:", iteration)
    print("Gráfico:")
    for i in range(max_bar_length, 0, -1):
        line = "{:4d}|".format(min_response_time + (i * unit))
        for response_time in response_times:
            if response_time >= min_response_time + (i * unit):
                line += "#"
            else:
                line += " "
        print(line)
    print("{:4d}+{}".format(min_response_time, "-" * max_bar_length))
    print("    ms")

def main():
    if getattr(sys, 'frozen', False):
        log_file = os.path.join(os.path.dirname(sys.executable), LOG_FILE_NAME)
    else:
        log_file = os.path.join(os.getcwd(), LOG_FILE_NAME)

    url = input(ENTER_URL)
    ip = get_ip(url)
    while ip is None:
        url = input(ENTER_URL)
        ip = get_ip(url)

    timeout = input(ENTER_TIMEOUT)
    timeout = int(timeout)

    iteration = 0
    total_response_time = 0
    response_times = []
    while True:
        status, response_time, response_content = get_status(url, timeout)
        if response_time is None:
            print(REQUEST_ERROR)
            url = input(ENTER_URL)
            ip = get_ip(url)
            continue
        now = datetime.datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        iteration += 1
        total_response_time += response_time
        avg_response_time = total_response_time / iteration
        avg_response_time = "{:.3f}".format(avg_response_time)
        response_time = "{:.3f}".format(response_time)
        data = f"{date_time},{url},{ip},{status},{response_time},{avg_response_time}"
        response_times.append(response_time)
        print_bar(iteration, response_times)
        print("URL:", url, "Endereço IP:", ip, "Código de Status:", status)
        print("Conteúdo json:", response_content)
        print("Tempo de Resposta:", response_time, "ms", "Data:", now.strftime("%Y-%m-%d"), "Hora:", now.strftime("%H:%M:%S"))
        print("Tempo de Resposta Médio (com base em", iteration, "iterações):", avg_response_time, "ms")
        save(data, log_file)
        time.sleep(timeout)

        # Verifica se é necessário fazer a rotação do arquivo de log
        if datetime.datetime.now().hour == 0:
            rotate_logs(log_file)


if __name__ == "__main__":
    main()


