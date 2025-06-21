import subprocess

def query_ollama(prompt, model="mistral"):
    command = ['ollama', 'run', model]
    proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, _ = proc.communicate(input=prompt.encode())
    return stdout.decode()
