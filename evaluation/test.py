import os
import json
import argparse
import numpy as np
from tqdm import tqdm
from evalplus.data import get_human_eval_plus
from human_eval.data import write_jsonl, read_problems


parser = argparse.ArgumentParser()
parser.add_argument("--model", required=True, type=str)
parser.add_argument("--dataset", default="humaneval", type=str, help='humaneval, humanevalplus, humanevalet, mbpp, mbppet, apps, appset')
parser.add_argument("--temperature", default=0.7, type=float)
parser.add_argument("--sanitize", action="store_true")
args = parser.parse_args()


if args.dataset in ['humaneval', 'humanevalplus', 'humanevalet']:
    if args.sanitize:
        workdir = os.path.join('humaneval', args.model + f"_temp_{args.temperature}-sanitized")
    else:
        workdir = os.path.join('humaneval', args.model + f"_temp_{args.temperature}")
elif args.dataset in ['mbpp', 'mbppet']:
    if args.sanitize:
        workdir = os.path.join('mbpp', args.model + f"_temp_{args.temperature}-sanitized")
    else:
        workdir = os.path.join('mbpp', args.model + f"_temp_{args.temperature}")
elif args.dataset in ['apps', 'appset']:
    if args.sanitize:
        workdir = os.path.join('apps', args.model + f"_temp_{args.temperature}-sanitized")
    else:
        workdir = os.path.join('apps', args.model + f"_temp_{args.temperature}")

# load generated codes
if args.dataset == 'humaneval':
    # dict_keys(['task_id', 'prompt', 'entry_point', 'canonical_solution', 'test'])
    problems = read_problems()
elif args.dataset == 'humanevalplus':
    # dict_keys(['task_id', 'prompt', 'entry_point', 'canonical_solution', 'test', 'contract', 'base_input', 'atol', 'plus_input'])
    problems = get_human_eval_plus()
elif args.dataset == 'humanevalet':
    # dict_keys(['task_id', 'prompt', 'entry_point', 'canonical_solution', 'test', 'test_case_list'])
    problems_temp = open('../dataset/humaneval_ET/HumanEval_ET.jsonl', 'r').readlines()
    problems = {}
    for i in problems_temp:
        j = json.loads(i)
        problems[j['task_id']] = {}
        problems[j['task_id']]['task_id'] = j['task_id']
        problems[j['task_id']]['prompt'] = j['prompt']
        problems[j['task_id']]['canonical_solution'] = j['canonical_solution']
        problems[j['task_id']]['test'] = j['test']
        problems[j['task_id']]['entry_point'] = j['entry_point']
        problems[j['task_id']]['test_case_list'] = j['test_case_list']
elif args.dataset == 'mbpp' or args.dataset == 'mbppet':
    def get_mbppet():
        tasks = {}
        # dict_keys(['text', 'code', 'task_id', 'test_setup_code', 'test_list', 'challenge_test_list', 'entry_point'])
        for i in open('../dataset/mbpp-ET/MBPP_ET.jsonl', 'r', encoding='utf-8').readlines():
            task = json.loads(i)
            tasks[f"MBPP/{task['task_id']}"] = ({
                "task_id": f"MBPP/{task['task_id']}",
                "prompt": task["text"],
                "canonical_solution": task["code"],
                "test": "\n\nMETADATA = {\n    'author': 'jt',\n    'dataset': 'test'\n}\n\n\ndef check(candidate):\n",
                "entry_point": task["entry_point"],
                "tab": "    ",
                "test_list": task["test_list"]
            })
        return tasks
    problems = get_mbppet()
elif args.dataset == 'apps' or args.dataset == 'appset':
    def get_appset():
        tasks = {}
        for i in open('../dataset/apps/APPS_300.jsonl', 'r', encoding='utf-8').readlines():
            task = json.loads(i)
            tasks[task['task_id']] = ({
                "task_id": task['task_id'],
                "prompt": task["prompt"],
                "test": task['test'],
                "test-et": task['test-et'],
                "entry_point": task["entry_point"],
                "canonical_solution": task["canonical_solution"],
            })
        return tasks
    problems = get_appset()


def generate_one_completion(prompt):
    return prompt_completion_dic[prompt]


if args.dataset == 'humaneval':
    os.system("rm %s/codes_%s.jsonl" % (workdir, args.dataset))
    os.system('rm %s/codes_%s_eval_results.json' % (workdir, args.dataset))
    prompt_completion_dic = {}
    for i in problems.keys():
        prompt_completion_dic[problems[i]['prompt']] = open(os.path.join(workdir, problems[i]['task_id'].replace('/', '_'), '0.py'), 'r', encoding='utf-8').read()
    num_samples_per_task = 1
    samples = [
        dict(task_id=task_id, completion=generate_one_completion(problems[task_id]["prompt"]))
        for task_id in problems
        for _ in range(num_samples_per_task)
    ]
    write_jsonl("%s/codes_%s.jsonl" % (workdir, args.dataset), samples)
    cmd = 'evaluate_functional_correctness %s/codes_%s.jsonl' % (workdir, args.dataset)
    print('################################')
    print(args.dataset, args.model)
    print('>>>', cmd)
    os.system(cmd)
    print('################################')
elif args.dataset == 'humanevalplus':
    os.system("rm %s/codes_%s.jsonl" % (workdir, args.dataset))
    os.system('rm %s/codes_%s_eval_results.json' % (workdir, args.dataset))
    prompt_completion_dic = {}
    for i in problems.keys():
        prompt_completion_dic[problems[i]['prompt']] = open(
            os.path.join(workdir, problems[i]['task_id'].replace('/', '_'), '0.py'), 'r',
            encoding='utf-8').read()
    num_samples_per_task = 1
    samples = [
        dict(task_id=task_id, completion=generate_one_completion(problems[task_id]["prompt"]))
        for task_id in problems
        for _ in range(num_samples_per_task)
    ]
    write_jsonl("%s/codes_%s.jsonl" % (workdir, args.dataset), samples)
    cmd = 'evalplus.evaluate --dataset humaneval --samples %s/codes_%s.jsonl' % (workdir, args.dataset)
    print('>>>', cmd)
    os.system(cmd)
    results = open('%s/codes_%s_eval_results.json' % (workdir, args.dataset), 'r').read()
    results = json.loads(results)
    # dict_keys(['date', 'hash', 'eval'])
    results = results['eval']
    base_count = 0
    plus_count = 0
    total_count = 0
    base_pass_ratio = []
    plus_pass_ratio = []
    base_detail = []
    plus_detail = []
    for task_id in results.keys():
        total_count += 1
        if len(problems[task_id]['base_input']) == len(results[task_id]['base'][0][1]):
            base_count += 1
            base_detail.append(str(task_id) + ',1\n')
        else:
            base_detail.append(str(task_id) + ',0\n')

        if len(problems[task_id]['plus_input']) == len(results[task_id]['plus'][0][1]):
            plus_count += 1
            plus_detail.append(str(task_id) + ',1\n')
        else:
            plus_detail.append(str(task_id) + ',0\n')

        base_pass_ratio.append(len(results[task_id]['base'][0][1]) / len(problems[task_id]['base_input']))
        plus_pass_ratio.append(len(results[task_id]['plus'][0][1]) / len(problems[task_id]['plus_input']))
    print('################################')
    print(args.dataset, args.model)
    print('base pass@1', base_count / total_count)
    print('plus pass@1', plus_count / total_count)
    print('base AvgPassRatio', np.average(base_pass_ratio))
    print('plus AvgPassRatio', np.average(plus_pass_ratio))
    print('################################')
    open('%s/detail_humanevalplus.csv' % (workdir), 'w').writelines(plus_detail)
    open('%s/result_humanevalplus.csv' % (workdir), 'w').writelines(
        f'pass@1, {plus_count / total_count}\nAvgPassRatio, {np.average(plus_pass_ratio)}\n')
elif args.dataset == 'humanevalet':
    count = 0
    total_count = 0
    pass_ratio = []
    detail = []
    for task_id in tqdm(problems.keys()):
        total_count += 1
        test = problems[task_id]['test']
        test = test.split('assert ')[0]
        completion = open(os.path.join(workdir, task_id.replace('/', '_'), '0.py'), 'r', encoding='utf-8').read()
        example_samples = {"task_id": problems[task_id]['task_id'], "completion": completion}
        example_problem = {"task_id": problems[task_id]['task_id'],
                           "prompt": problems[task_id]['prompt'],
                           "canonical_solution": problems[task_id]['canonical_solution'],
                           "entry_point": problems[task_id]['entry_point']}
        example_samples_list = []
        example_problem_list = []
        for index, test_case in enumerate(problems[task_id]['test_case_list']):
            example_samples_list.append({"task_id": example_samples['task_id']+f'-{index}', "completion": example_samples['completion']})
            example_problem_list.append({
                "task_id": example_problem['task_id']+f'-{index}',
                "prompt": example_problem['prompt'],
                "canonical_solution": example_problem['canonical_solution'],
                "entry_point": example_problem['entry_point'],
                "test": test + test_case.replace(example_problem['entry_point'], 'candidate')
            })
        write_jsonl('temp/example_samples.jsonl', example_samples_list)
        write_jsonl('temp/example_problem.jsonl', example_problem_list)
        cmd = 'evaluate_functional_correctness temp/example_samples.jsonl --problem_file=temp/example_problem.jsonl'
        os.system(cmd + '> /dev/null 2>&1')
        results = open('temp/example_samples.jsonl_results.jsonl', 'r').readlines()
        log = []
        for r in results:
            temp = json.loads(r.strip())
            if temp['passed'] == True:
                log.append(1)
            else:
                log.append(0)
        if len(log) == np.sum(log):
            count += 1
            detail.append(str(task_id) + ',1\n')
        else:
            detail.append(str(task_id) + ',0\n')
        pass_ratio.append(np.sum(log) / len(log))
    print('################################')
    print(args.dataset, args.model)
    print('pass@1', count / total_count)
    print('AvgPassRatio', np.average(pass_ratio))
    print('################################')
    open('%s/detail_%s.csv' % (workdir, args.dataset), 'w').writelines(detail)
    open('%s/result_%s.csv' % (workdir, args.dataset), 'w').writelines(f'pass@1, {count / total_count}\nAvgPassRatio, {np.average(pass_ratio)}\n')
elif args.dataset == 'mbpp' or args.dataset == 'mbppet':
    os.system("rm temp/example_samples.jsonl")
    os.system('rm temp/example_problem.jsonl')
    count = 0
    total_count = 0
    pass_ratio = []
    detail = []
    for task_id in tqdm(problems.keys()):
        total_count += 1
        test = problems[task_id]['test']
        completion = open(os.path.join(workdir, task_id.replace('/', '_'), '0.py'), 'r', encoding='utf-8').read()
        example_samples = {"task_id": problems[task_id]['task_id'], "completion": completion}
        example_problem = {"task_id": problems[task_id]['task_id'],
                           # "prompt": '#' + problems[task_id]['prompt'] + '\n',
                           "prompt": open(f'../results/MBPP-ori/{task_id.split("/")[1]}-prompt', 'r').read()+'\n',
                           "canonical_solution": problems[task_id]['canonical_solution'],
                           "entry_point": problems[task_id]['entry_point']}

        example_samples_list = []
        example_problem_list = []
        for index, test_case in enumerate(problems[task_id]['test_list']):
            if args.dataset == 'mbpp' and index == 3:
                break
            example_samples_list.append({"task_id": example_samples['task_id']+f'-{index}', "completion": example_samples['completion']})
            example_problem_list.append({
                "task_id": example_problem['task_id']+f'-{index}',
                "prompt": example_problem['prompt'],
                "canonical_solution": example_problem['canonical_solution'],
                "entry_point": example_problem['entry_point'],
                "test": test + problems[task_id]['tab'] + test_case.replace(example_problem['entry_point'], 'candidate')
            })

        write_jsonl('temp/example_samples.jsonl', example_samples_list)
        write_jsonl('temp/example_problem.jsonl', example_problem_list)
        cmd = 'evaluate_functional_correctness temp/example_samples.jsonl --problem_file=temp/example_problem.jsonl'
        os.system(cmd + '> /dev/null 2>&1')
        results = open('temp/example_samples.jsonl_results.jsonl', 'r').readlines()
        log = []
        for r in results:
            temp = json.loads(r.strip())
            if temp['passed'] == True:
                log.append(1)
            else:
                log.append(0)
        if len(log) == np.sum(log):
            count += 1
            detail.append(str(task_id) + ',1\n')
        else:
            detail.append(str(task_id) + ',0\n')
        pass_ratio.append(np.sum(log) / len(log))
    print('################################')
    print(args.dataset, args.model)
    print('pass@1', count / total_count)
    print('AvgPassRatio', np.average(pass_ratio))
    open('%s/detail_%s.csv' % (workdir, args.dataset), 'w').writelines(detail)
    open('%s/result_%s.csv' % (workdir, args.dataset), 'w').writelines(f'pass@1, {count/total_count}\nAvgPassRatio, {np.average(pass_ratio)}\n')
    print('################################')
elif args.dataset == 'apps' or args.dataset == 'appset':
    os.system("rm temp/example_samples.jsonl")
    os.system('rm temp/example_problem.jsonl')
    count = 0
    total_count = 0
    pass_ratio = []
    detail = []
    for task_id in tqdm(problems.keys()):
        total_count += 1
        completion = open(os.path.join(workdir, task_id.replace('/', '_'), '0.py'), 'r', encoding='utf-8').read()
        example_samples = {"task_id": problems[task_id]['task_id'], "completion": completion}
        example_problem = {"task_id": problems[task_id]['task_id'],
                           "prompt": problems[task_id]['prompt'] + '\n',
                           "canonical_solution": problems[task_id]['canonical_solution'],
                           "entry_point": problems[task_id]['entry_point']}

        example_samples_list = []
        example_problem_list = []
        if args.dataset == 'apps':
            test = problems[task_id]['test']
        elif args.dataset == 'appset':
            test = problems[task_id]['test-et']
        sig = test.split('assert ')[0].strip() + '\n'
        test_list = []
        for i in test.split('\n'):
            if i.strip()[:7] == 'assert ':
                test_list.append(sig + i + '\n')

        for index, test_case in enumerate(test_list):
            example_samples_list.append({"task_id": example_samples['task_id']+f'-{index}', "completion": example_samples['completion']})
            example_problem_list.append({
                "task_id": example_problem['task_id']+f'-{index}',
                "prompt": example_problem['prompt'],
                "canonical_solution": example_problem['canonical_solution'],
                "entry_point": example_problem['entry_point'],
                "test": test_case
            })

        write_jsonl('temp/example_samples.jsonl', example_samples_list)
        write_jsonl('temp/example_problem.jsonl', example_problem_list)
        cmd = 'evaluate_functional_correctness temp/example_samples.jsonl --problem_file=temp/example_problem.jsonl'
        os.system(cmd + '> /dev/null 2>&1')
        results = open('temp/example_samples.jsonl_results.jsonl', 'r').readlines()
        log = []
        for r in results:
            temp = json.loads(r.strip())
            if temp['passed'] == True:
                log.append(1)
            else:
                log.append(0)
        if len(log) == np.sum(log):
            count += 1
            detail.append(str(task_id) + ',1\n')
        else:
            detail.append(str(task_id) + ',0\n')
        pass_ratio.append(np.sum(log) / len(log))
    print('################################')
    print(args.dataset, args.model)
    print('pass@1', count / total_count)
    print('AvgPassRatio', np.average(pass_ratio))
    print('################################')
    open('%s/detail_%s.csv' % (workdir, args.dataset), 'w').writelines(detail)
    open('%s/result_%s.csv' % (workdir, args.dataset), 'w').writelines(f'pass@1, {count/total_count}\nAvgPassRatio, {np.average(pass_ratio)}\n')