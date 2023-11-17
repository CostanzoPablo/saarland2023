from flask import Flask, render_template
import matplotlib.pyplot as plt
import io
import base64
import threading
import time
import socket
import subprocess
import concurrent.futures
import threading
import queue

## ticks
# -timestamp
# -fk exploit_performances

## exploit_performance 
# exploit_name 
# exploit_arguments 
# flags captured
# ok 
# invalid_format
# invalid_flag
# expired
# already_submitted
# nop_team
# your_own_flag
# ctf_not_running

flag_queue = queue.Queue()
exploit_performance = {}

def calculate_ip(team_id):
    X = team_id // 200
    Y = team_id % 200
    return f"10.32.{X}.{Y}"

def run_exploit(team_ip, exploit_script, extra_args):
    while True:
        exploit_performance[exploit_script] = exploit_performance.get(exploit_script, 0)

        command = [exploit_script, team_ip] + extra_args
        try:
            with subprocess.Popen(command, stdout=subprocess.PIPE, text=True) as proc:
                try:
                    for line in iter(proc.stdout.readline, ''):
                        flag = line.strip()
                        flag_queue.put(flag)
                        exploit_performance[exploit_script] += 1
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.stdout.close()
        except Exception as e:
            print(f"Error running exploit {exploit_script}: {e}")

        time.sleep(90) # should this be here? 

def submit_flags():
    while True:
        flags_to_submit = []
        while not flag_queue.empty():
            flags_to_submit.append(flag_queue.get())

        if flags_to_submit:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("submission.ctf.saarland", 31337))
                for flag in flags_to_submit:
                    s.sendall((flag + "\n").encode())
                    response = s.recv(1024).decode()
                    print(f"Submission Response: {response}")

        time.sleep(120)  # tick

def main(number_of_teams, number_of_processes):
    submission_thread = threading.Thread(target=submit_flags, daemon=True)
    submission_thread.start()

    with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_processes) as executor:
        for team_id in range(number_of_teams):
            team_ip = calculate_ip(team_id)
            exploits = [ # should  this  be a yaml?
                ("exploit1.py", ["arg1", "arg2"]),
            ]
            for script, args in exploits:
                executor.submit(run_exploit, team_ip, script, args)

    submission_thread.join()

    for exploit, count in exploit_performance.items():
        print(f"{exploit} captured {count} flags")


# app = Flask(__name__)

# @app.route('/')
# def index():
#     plot_url = generate_scoreboard_plot()
#     return render_template('scoreboard.html', plot_url=plot_url)

# def generate_scoreboard_plot():
#     with threading.Lock():
#         exploits = list(exploit_performance.keys())
#         counts = [exploit_performance[exploit] for exploit in exploits]

#     plt.figure(figsize=(10, 6))
#     plt.bar(exploits, counts, color='blue')
#     plt.xlabel('Exploits')
#     plt.ylabel('Flags Captured')
#     plt.title('Exploit Performance Scoreboard')
#     plt.xticks(rotation=45)

#     buf = io.BytesIO()
#     plt.savefig(buf, format='png', bbox_inches='tight')
#     buf.seek(0)
#     plot_url = base64.b64encode(buf.getvalue()).decode('utf-8')
#     buf.close()

#     return 'data:image/png;base64,{}'.format(plot_url)

# def run_flask_app():
#     app.run(debug=True, use_reloader=False)


if __name__ == "__main__":
    number_of_teams = 100 
    number_of_processes = 10  

    # flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    # flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    # flask_thread.start()

    main(number_of_teams, number_of_processes)
