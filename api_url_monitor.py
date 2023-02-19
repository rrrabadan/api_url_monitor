import pathlib
import requests
import datetime
import time
import socket
import json


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
            response_content = "Essa url não possui um JSON válido"
        return status, response_time, response_content
    except requests.exceptions.RequestException as e:
        print(f"Erro ao solicitar a URL {url}: {e}")
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
        print("Host inválido. Por favor, informe um novo host.")
        print(url)
        return None

def save(data, log_file):
    log_path = pathlib.Path(log_file)
    if not log_path.exists():
        with log_path.open("w") as file:
            file.write("Data Hora,URL,Endereço IP,Código de Status,Tempo de Resposta,Tempo de Resposta Médio\n")
    with log_path.open("a") as file:
        file.write(data + "\n")
    print(f"Arquivo salvo em: {log_path.resolve()}\n")

def print_bar(iteration, response_times):
    response_times = [int(float(x)) for x in response_times if x is not None]
    max_response_time = max(response_times) if response_times else 0
    min_response_time = min(response_times) if response_times else 0
    bar_length = max(max_response_time - min_response_time, 1)
    max_bar_length = min(12, bar_length)
    unit = bar_length // max_bar_length
    print(f"Iteração: {iteration}")
    print("Gráfico do tempo de resposta (ms):")
    for i in range(max_bar_length, 0, -1):
        line = "{:4d}|".format(min_response_time + (i * unit))
        for response_time in response_times:
            if response_time >= min_response_time + (i * unit):
                line += "#"
            else:
                line += " "
        print(line)
    print("{:4d}+{}".format(min_response_time, "-" * max_bar_length))

def main():
    log_file = pathlib.Path("log.txt").resolve()
    ip = None
    while not ip:
        URL = input("Digite a URL ou API que deseja verificar: ")
        ip = get_ip(URL)

    TIMEOUT = int(input("Digite o tempo de timeout em segundos: "))
    iteration, total_response_time, response_times = 0, 0, []
    while True:
        status, response_time, response_content = get_status(URL, TIMEOUT)
        if response_time is None:
            URL = input("Erro ao solicitar a URL. Por favor, informe uma nova URL: ")
            ip = get_ip(URL)
            continue
        now = datetime.datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        iteration += 1
        total_response_time += response_time
        avg_response_time = total_response_time / iteration
        avg_response_time = "{:.3f}".format(avg_response_time)
        response_time = "{:.3f}".format(response_time)
        data = f"{date_time},{URL},{ip},{status},{response_time},{avg_response_time}"
        response_times.append(response_time)
        print_bar(iteration, response_times)
        print(f"URL: {URL}, Endereço IP: {ip}, Código de Status: {status}")
        print(f"Conteúdo json: {response_content}")
        print(f"Tempo de Resposta: {response_time} ms, Data: {now.strftime('%Y-%m-%d')}, Hora: {now.strftime('%H:%M:%S')}")
        print(f"Tempo de Resposta Médio (com base em {iteration} iterações): {avg_response_time} ms")
        save(data, log_file)
        time.sleep(TIMEOUT)


if __name__ == "__main__":
    main()

