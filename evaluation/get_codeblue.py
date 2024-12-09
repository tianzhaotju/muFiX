import os
import re
import sys
sys.path.append('../')
import json
import argparse
import tokenize
import numpy as np
from tqdm import tqdm
from io import StringIO
from CodeBLEU import bleu, weighted_ngram_match, syntax_match, dataflow_match


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


def python_process(tokens):
    new_tokens = []
    indent_count = 0
    num_tokens = len(tokens)
    tidx = 0
    while tidx < num_tokens:
        tok = tokens[tidx]
        tok = tok.strip()
        if tok in ["NEW_LINE"]:
            new_tokens.append("\n")
            if tidx + 1 < num_tokens:
                next_token = tokens[tidx + 1]
                if next_token == "INDENT":
                    indent_count += 1
                    tidx += 1
                elif next_token == "DEDENT":
                    indent_count -= 1
                    tidx += 1
            for ic in range(indent_count):
                new_tokens.append("\t")
        else:
            new_tokens.append(tok)
        tidx += 1
    return new_tokens
    pass


def language_specific_processing(tokens, lang):
    if lang == 'python':
        return python_process(tokens)
    else:
        return tokens


def get_codebleu(ref, hyp, lang, params, path, keyword_dir=None):
    lang = 'javascript' if lang == 'js' else lang
    alpha, beta, gamma, theta = [float(x) for x in params.split(',')]

    references = [[ref.strip()]]
    hypothesis = [hyp.strip()]

    print("calculate ngram match (BLEU")
    tokenized_hyps = [language_specific_processing(hyp.split(), lang)]
    tokenized_refs = [[language_specific_processing(ref.split(), lang)]]

    print("calculate corpus BLEU")
    ngram_match_score = bleu.corpus_bleu(tokenized_refs, tokenized_hyps)

    # calculate weighted ngram match
    if keyword_dir is None:
        keyword_dir = '../CodeBLEU/keywords'

    kw_file = os.path.join(keyword_dir, '{}.txt'.format(lang))
    keywords = [x.strip() for x in open(kw_file, 'r', encoding='utf-8').readlines()]

    def make_weights(reference_tokens, key_word_list):
        return {token: 1 if token in key_word_list else 0.2 for token in reference_tokens}

    tokenized_refs_with_weights = [
        [
            [reference_tokens, make_weights(reference_tokens, keywords)] for reference_tokens in reference
        ] for reference in tokenized_refs
    ]

    weighted_ngram_match_score = weighted_ngram_match.corpus_bleu(tokenized_refs_with_weights, tokenized_hyps)

    print("calculate syntax match")
    syntax_match_score = syntax_match.corpus_syntax_match(references, hypothesis, lang, path)

    print("calculate dataflow match")
    try:
        dataflow_match_score = dataflow_match.corpus_dataflow_match(references, hypothesis, lang, path)
    except:
        print([ref])
        print([hyp])

    print(
        'Ngram match:\t%.2f\nWeighted ngram:\t%.2f\nSyntax match:\t%.2f\nDataflow match:\t%.2f' %
        (ngram_match_score * 100, weighted_ngram_match_score * 100,
         syntax_match_score * 100, dataflow_match_score * 100)
    )

    code_bleu_score = alpha * ngram_match_score \
                      + beta * weighted_ngram_match_score \
                      + gamma * syntax_match_score \
                      + theta * dataflow_match_score

    return code_bleu_score


if __name__ == '__main__':
    # python get_codeblue.py --params=0.1,0.1,0.4,0.4
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, type=str)
    parser.add_argument('--lang', type=str, default='python',
                        choices=['java', 'js', 'c_sharp', 'php', 'go', 'python', 'ruby'],
                        help='programming language')
    parser.add_argument('--params', type=str, default='0.1,0.1,0.4,0.4', help='alpha, beta and gamma')
    parser.add_argument('--path', type=str, default='../CodeBLEU/parser/my-languages.so')
    args = parser.parse_args()
    for dataset in ['humaneval', 'humanevalplus', 'mbpp', 'apps']:
        groundtruth = {}
        if dataset in ['humaneval', 'humanevalplus']:
            for p in open(f'../dataset/{dataset}/{dataset}.jsonl', 'r').readlines():
                p_temp = json.loads(p)
                code = p_temp['prompt'] + p_temp['canonical_solution']
                try:
                    code = remove_comments_and_docstrings(code, args.lang)
                except:
                    pass
                groundtruth[p_temp['task_id']] = [code]
        elif dataset in ['mbpp']:
            for p in open(f'../dataset/{dataset}/{dataset}.jsonl', 'r').readlines():
                p_temp = json.loads(p)
                code = p_temp['code']
                try:
                    code = remove_comments_and_docstrings(code, args.lang)
                except:
                    pass
                groundtruth[p_temp['task_id']] = [code]
        elif dataset in ['apps']:
            apps_all = {}
            for p in open(f'../dataset/{dataset}/test.jsonl', 'r').readlines():
                p_temp = json.loads(p)
                try:
                    apps_all[int(p_temp['id'])] = json.loads(p_temp['solutions'])
                except:
                    apps_all[int(p_temp['id'])] = []
            for p in open(f'../dataset/{dataset}/APPS_300.jsonl', 'r').readlines():
                p_temp = json.loads(p)
                temp = apps_all[int(p_temp['task_id'].split('/')[-1])]
                if len(temp) == 0:
                    continue
                groundtruth[p_temp['task_id']] = []
                for t in temp:
                    code = p_temp['prompt']+'\n    ' + t.replace('\n', '\n    ')
                    try:
                        code = remove_comments_and_docstrings(code, args.lang)
                    except:
                        pass
                    groundtruth[p_temp['task_id']].append(code)
        codebleu_list = []
        for tech in [args.model]:
            temp_list = []
            for task_id in groundtruth.keys():
                if dataset in ['humaneval', 'humanevalplus']:
                    generated_code = open(f'./humaneval/{tech}_temp_0.7/HumanEval_{int(task_id.split("/")[-1])}/0.py', 'r').read()
                elif dataset in ['mbpp']:
                    generated_code = open(f'./{dataset}/{tech}_temp_0.7/MBPP_{task_id}/0.py', 'r').read()
                elif dataset in ['apps']:
                    generated_code = open(f'./{dataset}/{tech}_temp_0.7/{task_id.replace("/", "_")}/0.py', 'r').read()

                try:
                    generated_code = remove_comments_and_docstrings(generated_code, args.lang)
                except:
                    pass

                maxx = 0
                for ref in tqdm(groundtruth[task_id]):
                    code_bleu_score = get_codebleu(ref, generated_code, args.lang, args.params, args.path)
                    maxx = max(maxx, code_bleu_score)
                temp_list.append(maxx)
            codebleu_list.append(np.average((temp_list)))
        print(dataset, codebleu_list)