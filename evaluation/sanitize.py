import os
import re
import pathlib
import argparse
from tqdm import tqdm


SPLIT = ["```python", "```"]


def get_all_files(folder):
    if folder in ['./deepseek-coder/HumanEval-ori',
                  './chatgpt/HumanEval-ori',
                  './deepseek-coder/HumanEval-mufix',
                  './chatgpt/HumanEval-mufix']:
        # return a list of full-path python files
        py_files = []
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith("-7-all"):
                    py_files.append(root + '/' + file)
        return py_files
    else:
        print(f'Error:{folder} not found.')
        exit()


def get_code(input_string, split_word):
    if input_string.find(split_word[0]) != -1 and input_string.find(split_word[1]) != -1:
        pattern = re.compile(fr'{re.escape(split_word[0])}(.*?){re.escape(split_word[1])}', re.DOTALL)
        matches = re.findall(pattern, input_string)
        input_string = ''.join(matches)
    code_1 = []
    for i in input_string.split('\n'):
        if i[:7] != 'assert ' and i[:1] != '#':
            code_1.append(i)
    output_string = '\n'.join(code_1)

    return output_string


def remove_unindented_lines(code, ok_starts):
    new_code = ""
    for line in code.splitlines():
        if any([line.startswith(t) for t in ok_starts]) or line.strip() == "":
            new_code += line + "\n"
            continue

        lspace = len(line) - len(line.lstrip())
        if lspace == 0:
            continue

        new_code += line + "\n"

    return new_code


def to_four_space_indents(old_code):
    new_code = ""
    for line in old_code.splitlines():
        lspace = len(line) - len(line.lstrip())
        if lspace == 3:
            new_code += " "
        new_code += line + "\n"
    return new_code


if __name__ == "__main__":
    # python sanitize.py --folder=./chatgpt/HumanEval-ori
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", type=str, required=True)
    args = parser.parse_args()

    for pyf in tqdm(get_all_files(args.folder)):
        old_code = open(pyf, 'r', encoding='utf-8').read()
        new_code = get_code(old_code, SPLIT)

        # new_code = to_four_space_indents(new_code)
        # remove lines that are not indented
        # new_code = remove_unindented_lines(new_code, ok_starts=[def_left])

        # write to new folder
        new_pyf = pyf + '-sanitized'
        pathlib.Path(new_pyf).parent.mkdir(parents=True, exist_ok=True)
        with open(new_pyf, "w", encoding='utf-8') as f:
            f.write(new_code.strip())