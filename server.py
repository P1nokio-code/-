import socket
import threading

# Налаштування мережевих параметрів сервера
HOST = '0.0.0.0'  # Прослуховуємо всі доступні мережеві інтерфейси
PORT = 8080       # Порт, на якому працює сервер

clients = []  # Список для зберігання активних підключень клієнтів


def broadcast(data, exclude_socket=None):
    for client in clients:
        if client != exclude_socket:  # exclude_socket дозволяє виключити відправника
            try:
                client.sendall(data)  # Метод гарантує повну передачу байтів одержувачу
            except:
                pass


def handle_client(client_socket):
    while True:
        try:
            data = client_socket.recv(4096)  # Отримання даних від клієнта (буфер 4096 байт)
            if not data:
                break  # Якщо дані відсутні, клієнт розірвав з'єднання
            broadcast(data, exclude_socket=client_socket)
        except:
            break  # Примусовий вихід із циклу в разі помилки сокета

    if client_socket in clients:
        clients.remove(client_socket)  # Видалення клієнта зі списку активних при виході
    client_socket.close()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Створення TCP сервера
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Повторне використання порту
    server_socket.bind((HOST, PORT))
    
    # КРИТИЧНО: без цього рядка сервер не прийматиме підключення
    server_socket.listen(5)
    
    print(f'Сервер запущено на {HOST}:{PORT}')

    while True:
        client_socket, addr = server_socket.accept()
        print(f'Підключився клієнт: {addr}')
        clients.append(client_socket)
        
        t = threading.Thread(target=handle_client, args=(client_socket,))
        t.start()


if __name__ == "__main__":
    main()