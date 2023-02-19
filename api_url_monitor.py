import os
import requests
import datetime
import time
import socket
import sys

ENTER_URL = "Digite a URL ou API que deseja verificar: "
INVALID_HOST = "Host inválido. Por favor, informe um novo host."
REQUEST_ERROR = "Erro ao solicitar a URL. Por favor, informe uma nova URL."
SAVE_SUCCESS = "Arquivo salvo em:"

def get_status(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    try:
        response = requests.get(url)
        status = response.status_code
        response_time = response.elapsed.microseconds / 1000
        return status, response_time
    except requests.exceptions.RequestException as e:
        print(f"{REQUEST_ERROR} {url}: {e}")
        return None, None

def get_ip(url):
    try:
        ip = socket.gethostbyname(url)
        return ip
    except socket.gaierror:
        print(INVALID_HOST)
        return None

def save(data, file_name):
    file_path = os.path.join(os.path.dirname(sys.executable), file_name)
    print(f"{SAVE_SUCCESS} {file_path}\n")
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            file.write("Data Hora,URL,Endereço IP,Código de Status,Tempo de Resposta,Tempo de Resposta Médio\n")
    with open(file_path, "a") as file:
        file.write(data + "\n")

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
    url = input(ENTER_URL)
    ip = get_ip(url)
    while ip is None:
        url = input(ENTER_URL)
        ip = get_ip(url)
    iteration = 0
    total_response_time = 0
    response_times = []
    while True:
        status, response_time = get_status(url)
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
        file_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.txt")
        response_times.append(response_time)
        print_bar(iteration, response_times)
        print("URL:", url, "Endereço IP:", ip, "Código de Status:", status)
        print("Tempo de Resposta:", response_time, "ms", "Data:", now.strftime("%Y-%m-%d"), "Hora:", now.strftime("%H:%M:%S"))
        print("Tempo de Resposta Médio (com base em", iteration, "iterações):", avg_response_time, "ms")
        save(data, file_name)
        time.sleep(10)

if __name__ == "__main__":
    main()
