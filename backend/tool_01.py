import subprocess

yy = "../archive/StepID-XXX"
aaa = f"--logs-dir={yy}"
print(f"aaa: {aaa}")
cwd = "./output"

command = ["npm", "run", "build:agent", "--", aaa]
result = subprocess.run(command, cwd=cwd)
print(f"result: ${result}")
