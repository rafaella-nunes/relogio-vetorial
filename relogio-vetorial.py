import socket
import threading
import time
import random

class VectorClock:
    def __init__(self, process_id, total_processes):
        self.process_id = process_id
        self.total_processes = total_processes
        self.clock = [0] * total_processes

    def update(self):
        self.clock[self.process_id] += 1

    def send_message(self, target_process, socket):
        self.update()
        message = {
            'sender': self.process_id,
            'vector_clock': self.clock.copy()
        }
        print(f"Process {self.process_id} sending message to Process {target_process}: {message['vector_clock']}")
        socket.sendto(str(message).encode(), ('localhost', 5000 + target_process))

    def receive_message(self, message):
        sender = message['sender']
        received_clock = message['vector_clock']

        for i in range(self.total_processes):
            self.clock[i] = max(self.clock[i], received_clock[i])

        self.update()
        print(f"Process {self.process_id} received message from Process {sender}: {received_clock}")
        print(f"Process {self.process_id} updated vector clock: {self.clock}")

def send_random_message(process_id, total_processes, vector_clocks, sockets, stop_flag):
    while not stop_flag.is_set():
        time.sleep(random.uniform(1, 4))
        target_process = random.randint(0, total_processes - 1)
        vector_clocks[process_id].send_message(target_process, sockets[process_id])

def receive_messages(process_id, total_processes, vector_clocks, sockets, stop_flag):
    server_socket = sockets[process_id]
    server_socket.bind(('localhost', 5000 + process_id))

    while not stop_flag.is_set():
        message, addr = server_socket.recvfrom(1024)
        received_message = eval(message.decode())
        vector_clocks[process_id].receive_message(received_message)

def stop_program(threads, stop_flag):
    print("Finalizando...")
    stop_flag.set()  # Seta a flag para parar as threads

    for thread in threads:
        thread.join()  # Espera as threads finalizarem

    print("Comunicação encerrada.")

if __name__ == "__main__":
    total_processes = 4
    vector_clocks = [VectorClock(i, total_processes) for i in range(total_processes)]
    sockets = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in range(total_processes)]
    stop_flag = threading.Event()

    threads = []
    for i in range(total_processes):
        send_thread = threading.Thread(target=send_random_message, args=(i, total_processes, vector_clocks, sockets, stop_flag))
        receive_thread = threading.Thread(target=receive_messages, args=(i, total_processes, vector_clocks, sockets, stop_flag))
        threads.extend([send_thread, receive_thread])

    try:
        for thread in threads:
            thread.start()

        # Roda por 20 segundos
        time.sleep(20)

    except KeyboardInterrupt:
        pass  # Permite que o programa seja interrompido pelo ctrl+c

    finally:
        stop_program(threads, stop_flag)
