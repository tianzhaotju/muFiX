import os
import re
import copy
import json
import time
import openai
import tokenize
import argparse
import threading
from tqdm import tqdm
from io import StringIO
from model import make_model


F = 0

def remove_comments_and_docstrings(source, lang):
    if lang in ['python']:
        io_obj = StringIO(source)
        out = ""
        prev_toktype = tokenize.INDENT
        last_lineno = -1
        last_col = 0
        for tok in tokenize.generate_tokens(io_obj.readline):
            token_type = tok[0]
            token_string = tok[1]
            start_line, start_col = tok[2]
            end_line, end_col = tok[3]
            ltext = tok[4]
            if start_line > last_lineno:
                last_col = 0
            if start_col > last_col:
                out += (" " * (start_col - last_col))
            if token_type == tokenize.COMMENT:
                pass
            elif token_type == tokenize.STRING:
                if prev_toktype != tokenize.INDENT:
                    if prev_toktype != tokenize.NEWLINE:
                        if start_col > 0:
                            out += token_string
            else:
                out += token_string
            prev_toktype = token_type
            last_col = end_col
            last_lineno = end_line
        temp = []
        for x in out.split('\n'):
            if x.strip() != "":
                temp.append(x)
        return '\n'.join(temp)
    elif lang in ['ruby']:
        return source
    else:
        def replacer(match):
            s = match.group(0)
            if s.startswith('/'):
                return " "
            else:
                return s
        pattern = re.compile(
            r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
            re.DOTALL | re.MULTILINE
        )
        temp = []
        for x in re.sub(pattern, replacer, source).split('\n'):
            if x.strip() != "":
                temp.append(x)
        return '\n'.join(temp)


def execute_code(code_string):
    exec_globals = {}
    try:
        exec(code_string, exec_globals)
        return 1
    except Exception as e:
        # print(f"Error: {e}")
        return -1


def get_code_execution_result(code_string):
    exec_globals = {}
    try:
        exec(code_string, exec_globals)
        return exec_globals
    except Exception as e:
        # print(f"Error: {e}")
        return -1


def check_code_execution(code_string, timeout_seconds=10):
    code_executed = threading.Event()

    def code_execution_thread():
        global F
        F = execute_code(code_string)
        code_executed.set()
        return F

    execution_thread = threading.Thread(target=code_execution_thread)
    execution_thread.start()

    code_executed.wait(timeout=timeout_seconds)
    if execution_thread.is_alive():
        print("Error: Execution timed out.")
        return -1

    global F
    if F == 1:
        return 1
    elif F == -1:
        return 0
    return 1


def eval_code(code, test):
    fail = []
    success = []
    test_cases = test.split('\n')
    prompt_2 = '# Execution Results of Test Cases:'
    for i in range(len(test_cases)):
        temp = code + '\n' + test_cases[i]
        check_state = check_code_execution(temp)
        if check_state == 1:
            success.append(i+1)
            prompt_2 += f'\nTest case ({i+1}) passed.'
        elif check_state == 0:
            fail.append(i+1)
            prompt_2 += f'\nTest case ({i+1}) failed.'
        else:
            return -1
    if len(fail) == 0:
        return '1'

    return prompt_2


def get_code(input_string, split_word):
    if input_string.find(split_word[0]) == -1 or input_string.find(split_word[1]) == -1:
        output_string = input_string
    else:
        pattern = re.compile(fr'{re.escape(split_word[0])}(.*?){re.escape(split_word[1])}', re.DOTALL)
        matches = re.findall(pattern, input_string)
        output_string = ''.join(matches)

    code_1 = []
    for i in output_string.split('\n'):
        if i[:7] != 'assert ' and i[:1] != '#':
            code_1.append(i)
    output_string = '\n'.join(code_1)

    try:
        output_string = remove_comments_and_docstrings(output_string, 'python')
    except:
        pass

    return output_string


def call_llms(args, model, content, title=('Prompt', 'Reply')):
    print(f'========================= {title[0]} =========================')
    print(content[-1]['content'])
    if args.model == 'chatgpt':
        while 1:
            try:
                chat = openai.ChatCompletion.create(model=args.openai_model, messages=content, temperature=args.temperature)
                break
            except Exception as e:
                time.sleep(10)
                print(e, 'sleep and retry!')
                continue
        reply = chat.choices[0].message.content
        print(f'========================= {title[1]} =========================')
        print(reply)
        return reply
    elif args.model == 'deepseek-coder':
        reply = model.codegen2(content, do_sample=True, num_samples=1)[0].split('<|EOT|>')[0].strip()
        print(f'========================= {title[1]} =========================')
        print(reply)
        return reply
    else:
        print(f'Error: {args.model} not found.')
        exit()


def thought_eliciting_phase(args, model, path, task_id):
    if args.prompt == 'ori':
        data = open(f'{path}/{task_id}-prompt', 'r', encoding='utf-8').read()
        if data.strip() == '':
            return -1
        content = []
        prompt = f"{data.strip()}\n\n# Instruction: Please complete the code in a markdown style code block:\n\n```python\n\n```\n"
        content.append({"role": "user", "content": f"{prompt}"})
        reply = call_llms(args, model, content, ('Prompt', 'Code'))
        time.sleep({'chatgpt': 20, 'deepseek-coder': 0}[args.model])
        return reply
    elif args.prompt == 'mufix':
        data = open(f'{path}/{task_id}-prompt-1', 'r', encoding='utf-8').read()
        if data.strip() == '':
            data = open(f'{path}/{task_id}-prompt', 'r', encoding='utf-8').read()
            if data.strip() == '':
                return -1
            content = []
            prompt = f"{data.strip()}\n\n# Instruction: Please complete the code in a markdown style code block:\n\n```python\n\n```\n"
            content.append({"role": "user", "content": f"{prompt}"})
            reply = call_llms(args, model, content, ('Prompt', 'Code'))
            time.sleep({'chatgpt': 20, 'deepseek-coder': 0}[args.model])
            return reply
        if data.find('\n(1) assert ') == -1:
            data = open(f'{path}/{task_id}-prompt', 'r', encoding='utf-8').read()
            if data.strip() == '':
                return -1
            content = []
            prompt = f"{data.strip()}\n\n# Instruction: Please complete the code in a markdown style code block:\n\n```python\n\n```\n"
            content.append({"role": "user", "content": f"{prompt}"})
            reply = call_llms(args, model, content, ('Prompt', 'Code'))
            time.sleep({'chatgpt': 20, 'deepseek-coder': 0}[args.model])
            return reply

        index = data.find('\n(1) assert ')
        original_prompt_without_testcases = data[:index].strip()
        testcases_1 = data[index:].strip()
        testcases_2 = data[index:].strip()
        testcases_2 = testcases_2.split('\n')
        testcases = []
        for i in range(len(testcases_2)):
            index = testcases_2[i].find('assert')
            if index != -1:
                testcases.append(testcases_2[i][index:])
        testcases_2 = '\n'.join(testcases)

        # generate analysis - 1
        if os.path.exists(f'{path}/{task_id}-analysis-1'):
            analysis_1 = open(f'{path}/{task_id}-analysis-1', 'r', encoding='utf-8').read()
        else:
            content = []
            prompt = f"# Code:\n{original_prompt_without_testcases}\n\n# Test Cases:\n{testcases_1}\n\n# Instruction: Let's analyze the test cases step by step. You MUST follow the format:\n\"\n(<?>) assert <?> == <?>\nThe input is <?>.\nThe output is <?>.\nAnalysis: <?>.\nTherefore, the expected output is <?>.\n\""
            content.append({"role": "user", "content": f"{prompt}"})
            analysis_1 = call_llms(args, model, content, ('Prompt', 'Reply'))
            # open(f'{path}/{task_id}-analysis-1', 'w', encoding='utf-8').write(analysis_1)
            time.sleep({'chatgpt': 20, 'deepseek-coder': 0}[args.model])

        # generate analysis - 2
        if os.path.exists(f'{path}/{task_id}-analysis-2'):
            analysis_2 = open(f'{path}/{task_id}-analysis-2', 'r', encoding='utf-8').read()
        else:
            try:
                analysis_1_temp = analysis_1.split('Analysis:')[1:]
                initial_analysis = ''
                format_2 = ''
                for i in range(len(testcases)):
                    initial_analysis += f"({i+1}) {testcases[i].split('==')[0].strip('assert').strip()}\n"
                    initial_analysis += f"Analysis: {analysis_1_temp[i].split('Therefore, the expected output is ')[0].strip()}\nTherefore, the expected output is <?>.\n\n"
                    format_2 += f'({i+1}) Therefore, the expected output is ?.\n'
                initial_analysis = initial_analysis.strip()
                content = []
                prompt = f"# Code:\n{original_prompt_without_testcases}\n\n# Analysis of Test Cases:\n{initial_analysis}\n\n# Instruction: According to the above analysis of test cases, please provide the expected output for these test cases. You MUST follow the format:\n\"\n{format_2}\n\""
                content.append({"role": "user", "content": f"{prompt}"})
                analysis_2 = call_llms(args, model, content, ('Prompt', 'Reply'))
                # open(f'{path}/{task_id}-analysis-2', 'w', encoding='utf-8').write(analysis_2)
                time.sleep({'chatgpt': 20, 'deepseek-coder': 0}[args.model])
            except Exception as e:
                data = open(f'{path}/{task_id}-prompt', 'r', encoding='utf-8').read()
                if data.strip() == '':
                    return -1
                content = []
                prompt = f"{data.strip()}\n\n# Instruction: Please complete the code in a markdown style code block:\n\n```python\n\n```\n"
                content.append({"role": "user", "content": f"{prompt}"})
                reply = call_llms(args, model, content, ('Prompt', 'Code'))
                time.sleep({'chatgpt': 20, 'deepseek-coder': 0}[args.model])
                return reply
        try:
            analysis_1_temp = copy.deepcopy(analysis_1)
            analysis_2_temp = analysis_2.split('Therefore, the expected output is')[1:]
            analysis_2_temp = [x.strip() for x in analysis_2_temp]
            analysis_2_correction = ''
            if_need_corerction = False
            for i in range(len(testcases)):
                analysis_1_temp = analysis_1_temp.split(f'({i+1})')[1]
                analysis_2_correction += f"({i+1}) {analysis_1_temp.split('Therefore, the expected output is')[0].strip()}"
                expected_output_1 = testcases[i].split('==')[-1].strip()
                expected_output_2 = analysis_2_temp[i][:len(expected_output_1)] + analysis_2_temp[i][len(expected_output_1):].split('.')[0]
                if expected_output_1 == expected_output_2 and analysis_2_temp[i][len(expected_output_1)] == '.':
                    analysis_2_correction += f'\nTherefore, the expected output is {expected_output_1}.\n'
                else:
                    if_need_corerction = True
                    analysis_2_correction += f'\nTherefore, the expected output is {expected_output_2}.\n'
            analysis_2_correction = analysis_2_correction.strip()
        except Exception as e:
            data = open(f'{path}/{task_id}-prompt', 'r', encoding='utf-8').read()
            if data.strip() == '':
                return -1
            content = []
            prompt = f"{data.strip()}\n\n# Instruction: Please complete the code in a markdown style code block:\n\n```python\n\n```\n"
            content.append({"role": "user", "content": f"{prompt}"})
            reply = call_llms(args, model, content, ('Prompt', 'Code'))
            time.sleep({'chatgpt': 20, 'deepseek-coder': 0}[args.model])
            return reply

        # generate analysis - 3
        if if_need_corerction:
            if os.path.exists(f'{path}/{task_id}-analysis-3'):
                analysis_3 = open(f'{path}/{task_id}-analysis-3', 'r', encoding='utf-8').read()
            else:
                try:
                    content = []
                    prompt = f"# Code:\n{original_prompt_without_testcases}\n\n# Analysis of Test Cases:\n{analysis_2_correction}\n\n# Instruction: The above analysis of test cases is incorrect, provide the correct analysis again. You MUST follow the format:\n\"\n(<?>) assert <?> == <?>\nThe input is <?>.\nThe output is <?>.\nAnalysis: <?>.\nTherefore, the expected output is <?>.\n\""
                    content.append({"role": "user", "content": f"{prompt}"})
                    analysis_3 = call_llms(args, model, content, ('Prompt', 'Reply'))
                    # open(f'{path}/{task_id}-analysis-3', 'w', encoding='utf-8').write(analysis_3)
                    time.sleep({'chatgpt': 20, 'deepseek-coder': 0}[args.model])
                except Exception as e:
                    data = open(f'{path}/{task_id}-prompt', 'r', encoding='utf-8').read()
                    if data.strip() == '':
                        return -1
                    content = []
                    prompt = f"{data.strip()}\n\n# Instruction: Please complete the code in a markdown style code block:\n\n```python\n\n```\n"
                    content.append({"role": "user", "content": f"{prompt}"})
                    reply = call_llms(args, model, content, ('Prompt', 'Code'))
                    time.sleep({'chatgpt': 20, 'deepseek-coder': 0}[args.model])
                    return reply
            testcase_analysis = analysis_3.strip()
        else:
            testcase_analysis = analysis_1.strip()

        # if not os.path.exists(f'{path}/{task_id}-analysis-4'):
        #     open(f'{path}/{task_id}-analysis-4', 'w', encoding='utf-8').write(testcase_analysis)

        # generate code - 1
        if os.path.exists(f'{path}/{task_id}-{int(args.temperature * 10)}-all-1'):
            reply = open(f'{path}/{task_id}-{int(args.temperature * 10)}-all-1', 'r', encoding='utf-8').read()
        else:
            content = []
            prompt = f"# Code:\n{original_prompt_without_testcases}\n\n# Analysis of Test Cases:\n{testcase_analysis}\n\n# Instruction: Please complete the code in a markdown style code block (pay attention to the analysis of test cases):\n\n```python\n\n```\n"
            content.append({"role": "user", "content": f"{prompt}"})
            reply = call_llms(args, model, content, ('Prompt', 'Code'))
            open(f'{path}/{task_id}-{int(args.temperature * 10)}-all-1', 'w', encoding='utf-8').write(reply)
            time.sleep({'chatgpt': 20, 'deepseek-coder': 0}[args.model])
        return reply
    else:
        print(f'Error: {args.prompt} not found.')
        exit()


def feedback_phase(args, model, path, task_id, code_1):
    data = open(f'{path}/{task_id}-prompt-1', 'r', encoding='utf-8').read()
    if data.strip() == '':
        data = open(f'{path}/{task_id}-prompt', 'r', encoding='utf-8').read()
        if data.strip() == '':
            return -1
        content = []
        prompt = f"{data.strip()}\n\n# Instruction: Please complete the code in a markdown style code block:\n\n```python\n\n```\n"
        content.append({"role": "user", "content": f"{prompt}"})
        reply = call_llms(args, model, content, ('Prompt', 'Code'))
        time.sleep({'chatgpt': 20, 'deepseek-coder': 0}[args.model])
        return reply
    if data.find('\n(1) assert ') == -1:
        data = open(f'{path}/{task_id}-prompt', 'r', encoding='utf-8').read()
        if data.strip() == '':
            return -1
        content = []
        prompt = f"{data.strip()}\n\n# Instruction: Please complete the code in a markdown style code block:\n\n```python\n\n```\n"
        content.append({"role": "user", "content": f"{prompt}"})
        reply = call_llms(args, model, content, ('Prompt', 'Code'))
        time.sleep({'chatgpt': 20, 'deepseek-coder': 0}[args.model])
        return reply

    index = data.find('\n(1) assert ')
    original_prompt_without_testcases = data[:index].strip()
    testcases_1 = data[index:].strip()
    testcases_2 = data[index:].strip()
    testcases_2 = testcases_2.split('\n')
    testcases = []
    for i in range(len(testcases_2)):
        index = testcases_2[i].find('assert')
        if index != -1:
            testcases.append(testcases_2[i][index:])
    testcases_2 = '\n'.join(testcases)

    content = []
    testcase_analysis = open(f'{path}/{task_id}-analysis-4', 'r', encoding='utf-8').read()
    prompt = f"# Code:\n{original_prompt_without_testcases}\n\n# Analysis of Test Cases:\n{testcase_analysis}\n\n# Instruction: Please complete the code in a markdown style code block (pay attention to the analysis of test cases):\n\n```python\n\n```\n"
    content.append({"role": "user", "content": f"{prompt}"})
    code_1 = get_code(code_1, ["```python", "```"])
    content.append({"role": "assistant", "content": f"{code_1}"})

    check_state = check_code_execution(code_1 + '\n' + testcases_2)

    if check_state == 1:
        return code_1
    elif check_state == -1:
        prompt = f"# Instruction: Please regenerate the correct code in a markdown style code block:\n\n```python\n\n```\n"
        content.append({"role": "user", "content": f"{prompt}"})
        reply = call_llms(args, model, content, ('Prompt', 'Code'))
        time.sleep({'chatgpt': 20, 'deepseek-coder': 0}[args.model])
        return reply
    else:
        feedback = eval_code(code_1, testcases_2)
        if feedback == '1':
            return code_1
        elif feedback == -1:
            prompt = f"# Instruction: Please regenerate the correct code in a markdown style code block:\n\n```python\n\n```\n"
            content.append({"role": "user", "content": f"{prompt}"})
            reply = call_llms(args, model, content, ('Prompt', 'Code'))
            time.sleep({'chatgpt': 20, 'deepseek-coder': 0}[args.model])
            return reply

        # generate analysis - 5
        if os.path.exists(f'{path}/{task_id}-analysis-5'):
            analysis_5 = open(f'{path}/{task_id}-analysis-5', 'r', encoding='utf-8').read()
        else:
            content2 = []
            prompt2 = f"# Code:\n{code_1}\n\n# Test Cases:\n{testcases_1}\n\n# Instruction: Let's analyze the test cases step by step. You MUST follow the format:\n\"\n(<?>) assert <?> == <?>\nThe input is <?>.\nThe output is <?>.\nAnalysis: <?>.\nTherefore, the expected output is <?>.\n\""
            content2.append({"role": "user", "content": f"{prompt2}"})
            analysis_5 = call_llms(args, model, content2, ('Prompt', 'Reply'))
            # open(f'{path}/{task_id}-analysis-5', 'w', encoding='utf-8').write(analysis_5)
            time.sleep({'chatgpt': 20, 'deepseek-coder': 0}[args.model])

        # generate analysis - 6
        if os.path.exists(f'{path}/{task_id}-analysis-6'):
            analysis_6 = open(f'{path}/{task_id}-analysis-6', 'r', encoding='utf-8').read()
        else:
            content3 = []
            prompt3 = f"# Specification:\n{original_prompt_without_testcases}\n\n"
            prompt3 += f"# Analysis-1:\n{testcase_analysis.strip()}'\n\n"
            prompt3 += f"# Code-1:\n{code_1.strip()}\n\n"
            prompt3 += feedback.strip() + '\n\n'
            prompt3 += f"# Analysis-2:\n{analysis_5.strip()}\n\n"
            prompt3 += "\n# Instruction: Based on the correct Analysis-1, the incorrect Code-1 is generated. And incorrect Code-1 generates incorrect Analysis-2."
            prompt3 += " Please regenerate the more accurate analysis of test cases for generating correct code."
            prompt3 += f" You MUST follow the format:\n\"\n(<?>) assert <?> == <?>\nThe input is <?>.\nThe output is <?>.\nAnalysis: <?>.\nTherefore, the expected output is <?>.\n\""
            content3.append({"role": "user", "content": f"{prompt3}"})
            analysis_6 = call_llms(args, model, content3, ('Prompt', 'Reply'))
            # open(f'{path}/{task_id}-analysis-6', 'w', encoding='utf-8').write(analysis_6)
            time.sleep({'chatgpt': 20, 'deepseek-coder': 0}[args.model])

        # generate code - 2
        if os.path.exists(f'{path}/{task_id}-{int(args.temperature * 10)}-all-2'):
            reply = open(f'{path}/{task_id}-{int(args.temperature * 10)}-all-2', 'r', encoding='utf-8').read()
        else:
            prompt = f"{feedback.strip()}\n\n"
            prompt += f"# Correct Analysis of Test Cases:\n{analysis_6}\n\n# Instruction: The code generated the first time is incorrect. Please regenerate the code in a markdown style code block (pay attention to the correct analysis of test cases):\n\n```python\n\n```\n"
            content.append({"role": "user", "content": f"{prompt}"})
            reply = call_llms(args, model, content, ('Prompt', 'Code'))
            open(f'{path}/{task_id}-{int(args.temperature * 10)}-all-2', 'w', encoding='utf-8').write(reply)
            time.sleep({'chatgpt': 20, 'deepseek-coder': 0}[args.model])
        return reply


if __name__ == '__main__':
    # python generate.py --model=chatgpt --prompt=mufix --dataset=humaneval --temperature=0.7;
    # python generate.py --model=deepseek-coder --prompt=mufix --dataset=humaneval --temperature=0.7;
    openai.api_key = ''
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default='', type=str)
    parser.add_argument("--prompt", default='', type=str)
    parser.add_argument("--dataset", default='', type=str, help='humaneval, mbpp, apps')
    parser.add_argument("--temperature", default=0.7, type=float)
    args = parser.parse_args()

    if args.model == 'chatgpt':
        args.openai_model = 'gpt-3.5-turbo-0613'
        model = None
    elif args.model == 'deepseek-coder':
        args.openai_model = '../../deepseek-ai/deepseek-coder-6.7b-instruct'
        model = make_model(name='deepseek-coder-6.7b-instruct', batch_size=1, temperature=args.temperature)

    if args.dataset == 'humaneval':
        all_task_id = []
        for i in range(0, 164):
            all_task_id.append(str(i))
        path = f'./{args.model}/HumanEval-{args.prompt}'
    elif args.dataset == 'mbpp':
        all_task_id = []
        for i in range(1, 975):
            all_task_id.append(str(i))
        path = f'./{args.model}/MBPP-{args.prompt}'
    elif args.dataset == 'apps':
        all_task_id = []
        for i in tqdm(open('./dataset/apps/APPS_300.jsonl', 'r', encoding='utf-8').readlines()):
            temp = json.loads(i)
            task_id = temp['task_id'].split('/')[-1]
            all_task_id.append(task_id)
        path = f'./{args.model}/APPSEval-{args.prompt}'
    else:
        print(f'Error: {args.dataset} not found.')
        exit()

    for task_id in tqdm(all_task_id):
        print('\n', task_id, '...')
        try:
            reply = thought_eliciting_phase(args, model, path, task_id)
            if not os.path.exists(f'{path}/{task_id}-{int(args.temperature * 10)}-all-1'):
                open(f'{path}/{task_id}-{int(args.temperature * 10)}-all-1', 'w', encoding='utf-8').write(reply)
        except:
            data = open(f'{path}/{task_id}-prompt', 'r', encoding='utf-8').read()
            if data.strip() == '':
                continue
            content = []
            prompt = f"{data.strip()}\n\n# Instruction: Please complete the code in a markdown style code block:\n\n```python\n\n```\n"
            content.append({"role": "user", "content": f"{prompt}"})
            reply = call_llms(args, model, content, ('Prompt', 'Code'))
            open(f'{path}/{task_id}-{int(args.temperature * 10)}-all-1', 'w', encoding='utf-8').write(reply)
            time.sleep({'chatgpt': 20, 'deepseek-coder': 0}[args.model])

        try:
            if args.prompt == 'mufix':
                reply = feedback_phase(args, model, path, task_id, reply)
        except:
            data = open(f'{path}/{task_id}-prompt', 'r', encoding='utf-8').read()
            if data.strip() == '':
                continue
            content = []
            prompt = f"{data.strip()}\n\n# Instruction: Please complete the code in a markdown style code block:\n\n```python\n\n```\n"
            content.append({"role": "user", "content": f"{prompt}"})
            reply = call_llms(args, model, content, ('Prompt', 'Code'))
            open(f'{path}/{task_id}-{int(args.temperature * 10)}-all-2', 'w', encoding='utf-8').write(reply)
            time.sleep({'chatgpt': 20, 'deepseek-coder': 0}[args.model])

        if reply == -1:
            continue
        if not os.path.exists(path):
            os.mkdir(path)
        f = open(f'{path}/{task_id}-{int(args.temperature * 10)}-all', 'w', encoding='utf-8')
        f.write(reply)
        f.close()
        print('\n', task_id, 'Finish.')
        # exit()
