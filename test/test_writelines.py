from pathlib import Path

fw = Path('./test.txt').open('w')

lines = ['123213','4354535','657567']

fw.writelines(line + '\n' for line in lines)