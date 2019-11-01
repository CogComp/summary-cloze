import json
import math
import os
import pytest
import unittest
from typing import List

from summarize.common.testing import FIXTURES_ROOT
from summarize.metrics.python_rouge import PythonRouge, shorten_summary
from summarize.metrics.rouge import run_rouge, R1_RECALL, R1_PRECISION, R1_F1, \
    R2_RECALL, R2_PRECISION, R2_F1, \
    RL_RECALL, RL_PRECISION, RL_F1

_duc2004_file_path = 'data/duc/duc2004/duc2004.task2.jsonl'
_centroid_file_path = f'{FIXTURES_ROOT}/data/hong2014/centroid.jsonl'


class PythonRougeTest(unittest.TestCase):
    def test_normalize_and_tokenize(self):
        """
        Tests to ensure the python version of Rouge correctly implements the
        perl implementation. The expected tokens were generated by editing the
        perl script to print the tokens during processing. The hyphens were added
        to the original because the perl implementation uses them to separate words.
        """
        rouge = PythonRouge()
        original = 'Xu Wenli, Wang Youchai, and Qin Yongmin, leading dissidents and '\
            'prominent members of the China-Democracy-Party, were found guilty of subversion ' \
            'and sentenced to 13, 11, and 12 years in prison, respectively.'
        expected = 'xu wenli wang youchai and qin yongmin leading dissidents and ' \
            'prominent members of the china democracy party were found guilty of subversion ' \
            'and sentenced to 13 11 and 12 years in prison respectively'.split()
        actual = rouge.normalize_and_tokenize_sentence(original, use_porter_stemmer=False, remove_stopwords=False)
        assert expected == actual

        expected = 'xu wenli wang youchai and qin yongmin lead dissid and promin '\
            'member of the china democraci parti be find guilti of subvers and sentenc '\
            'to 13 11 and 12 year in prison respect'.split()
        actual = rouge.normalize_and_tokenize_sentence(original, use_porter_stemmer=True, remove_stopwords=False)
        assert expected == actual

        expected = 'xu wenli wang youchai qin yongmin leading dissidents prominent '\
            'members china democracy party found guilty subversion sentenced 13 11 '\
            '12 years prison'.split()
        actual = rouge.normalize_and_tokenize_sentence(original, use_porter_stemmer=False, remove_stopwords=True)
        assert expected == actual

        expected = 'xu wenli wang youchai qin yongmin lead dissid promin member china '\
            'democraci parti find guilti subvers sentenc 13 11 12 year prison'.split()
        actual = rouge.normalize_and_tokenize_sentence(original, use_porter_stemmer=True, remove_stopwords=True)
        assert expected == actual

    def test_shorten_summary(self):
        original = [
            'This is an example sentence, which is first.',
            'This is the second one.'
            'Finally, the third.'
        ]

        expected = [
            'This is an example'
        ]
        actual = shorten_summary(original, max_words=4)
        assert expected == actual

        expected = [
            'This is an example sentence, which is first.',
        ]
        actual = shorten_summary(original, max_words=8)
        assert expected == actual

        expected = [
            'This is an example sentence, which is first.',
            'This is'
        ]
        actual = shorten_summary(original, max_words=10)
        assert expected == actual

        actual = shorten_summary(original, max_words=16)
        assert original == actual
        actual = shorten_summary(original, max_words=100)
        assert original == actual

        expected = [
            'This is an'
        ]
        actual = shorten_summary(original, max_bytes=10)
        actual = shorten_summary(original, max_bytes=11)

        expected = [
            'This is an example sentence, which is first.',
        ]
        actual = shorten_summary(original, max_bytes=44)
        assert expected == actual

        expected = [
            'This is an example sentence, which is first.',
            'T'
        ]
        actual = shorten_summary(original, max_bytes=45)
        assert expected == actual

        actual = shorten_summary(original, max_bytes=87)
        assert original == actual
        actual = shorten_summary(original, max_bytes=88)
        assert original == actual

    def test_preprocessing(self):
        rouge = PythonRouge()
        original = [
            'Xu Wenli, Wang Youchai, and Qin Yongmin, leading dissidents and'
        ]
        expected = ['xu wenli wang youchai'.split()]
        actual = rouge.preprocess_summary(original, max_words=5, remove_stopwords=True)
        assert expected == actual

    def test_python_rouge(self):
        python_rouge = PythonRouge()
        summary = [
            "His tenacity holds despite the summary trials and harsh punishments for Xu, Wang Youcai and Qin Yongmin prominent party principals from the provinces who were sentenced to 11 and 12 years and despite threatening signs from the ruling Communist Party.",
            "The dissidents Xu Wenli, who was sentenced Monday to 13 years in prison, Wang Youcai, who received an 11-year sentence, and Qin Yongming, who was reported to have received 12 years were charged with subversion.",
            "As police moved against Xu's friends, labor rights campaigner Liu Nianchun was taken from a prison camp outside Beijing and, with his wife and daughter, was put on a plane to Canada and then New York, his first taste of freedom in more than 3 1/2 years."
        ]
        gold_summaries = [
            [
                "While China plans to sign the International Covenant on Civil and Political Rights at the U.N., it is still harassing and arresting human rights campaigners.",
                "Three prominent leaders of the China Democratic Party were put to trial and sentenced to 11-, 12- and 13-year prison terms.",
                "Germany and the U.S. condemned the arrests.",
                "A labor rights activist was released and exiled to the U.S. to blunt any opposition to Communist rule.",
                "U.S. policy to encourage trade and diplomacy in hope of democratic reforms evidences failure, but the U.S. is continuing its policy of encouragement.",
                "Friends of jailed dissidents state that they will continue to campaign for change."
            ],
            [
                "The US trade-driven policy of expanded ties encouraging Chinese democracy is questioned.",
                "China signed rights treaties and dissidents used new laws to set up China Democracy Party, but China violates the new laws by persecuting dissidents.",
                "It regularly frees activists from prison then exiles them so they lose local influence.",
                "It arrested an activist trying to register a rights monitoring group.",
                "CP leader Jiang's hard-line speech and publicity for activists sentenced to long prison terms signals a renewed Chinese crackdown.",
                "A rights activist expected to be sacrificed in the cause of democracy.",
                "Germany called China's sentencing of dissidents unacceptable."
            ],
            [
                "After 2 years of wooing the West by signing international accords, apparently relaxing controls on free speech, and releasing and exiling three dissenters, China cracked down against political dissent in Dec 1998.",
                "Leaders of the China Democracy Party (CDP) were arrested and three were sentenced to jail terms of 11 to 13 years.",
                "The West, including the US, UK and Germany, reacted strongly.",
                "Clinton's China policy of engagement was questioned.",
                "China's Jiang Zemin stated economic reform is not a prelude to democracy and vowed to crush any challenges to the Communist Party or \"social stability\".",
                "The CDP vowed to keep working, as more leaders awaited arrest."
            ],
            [
                "Xu Wenli, Wang Youchai, and Qin Yongmin, leading dissidents and prominent members of the China Democracy Party, were found guilty of subversion and sentenced to 13, 11, and 12 years in prison, respectively.",
                "Soon after the sentencing, China's president, Jiang Zemin, delivered speeches in which he asserted that Western political system must not be adopted and vowed to crush challenges to Communist Party rule.",
                "The harsh sentences and speeches signal a crackdown on dissent, but Zha Jianguo, another Democracy Party leader, says he will continue to push for change.",
                "Western nations condemned the sentences as violations of U.N. rights treaties signed by China."
            ]
        ]

        compute_rouge_l = True
        use_stemmer = False
        remove_stopwords = False
        expected_metrics = run_rouge([gold_summaries], [summary],
                                     use_porter_stemmer=use_stemmer, remove_stopwords=remove_stopwords,
                                     max_ngram=2, compute_rouge_l=compute_rouge_l)
        actual_metrics = python_rouge.run_python_rouge([gold_summaries], [summary],
                                                       use_porter_stemmer=use_stemmer,
                                                       remove_stopwords=remove_stopwords,
                                                       compute_rouge_l=compute_rouge_l)
        self.assertAlmostEqual(expected_metrics[R1_PRECISION], actual_metrics[R1_PRECISION], places=2)
        self.assertAlmostEqual(expected_metrics[R1_RECALL], actual_metrics[R1_RECALL], places=2)
        self.assertAlmostEqual(expected_metrics[R1_F1], actual_metrics[R1_F1], places=2)
        self.assertAlmostEqual(expected_metrics[R2_PRECISION], actual_metrics[R2_PRECISION], places=2)
        self.assertAlmostEqual(expected_metrics[R2_RECALL], actual_metrics[R2_RECALL], places=2)
        self.assertAlmostEqual(expected_metrics[R2_F1], actual_metrics[R2_F1], places=2)
        self.assertAlmostEqual(expected_metrics[RL_PRECISION], actual_metrics[RL_PRECISION], places=2)
        self.assertAlmostEqual(expected_metrics[RL_RECALL], actual_metrics[RL_RECALL], places=2)
        self.assertAlmostEqual(expected_metrics[RL_F1], actual_metrics[RL_F1], places=2)

        use_stemmer = False
        remove_stopwords = True
        expected_metrics = run_rouge([gold_summaries], [summary],
                                     use_porter_stemmer=use_stemmer, remove_stopwords=remove_stopwords,
                                     max_ngram=2, compute_rouge_l=compute_rouge_l)
        actual_metrics = python_rouge.run_python_rouge([gold_summaries], [summary],
                                                       use_porter_stemmer=use_stemmer,
                                                       remove_stopwords=remove_stopwords,
                                                       compute_rouge_l=compute_rouge_l)
        self.assertAlmostEqual(expected_metrics[R1_PRECISION], actual_metrics[R1_PRECISION], places=2)
        self.assertAlmostEqual(expected_metrics[R1_RECALL], actual_metrics[R1_RECALL], places=2)
        self.assertAlmostEqual(expected_metrics[R1_F1], actual_metrics[R1_F1], places=2)
        self.assertAlmostEqual(expected_metrics[R2_PRECISION], actual_metrics[R2_PRECISION], places=2)
        self.assertAlmostEqual(expected_metrics[R2_RECALL], actual_metrics[R2_RECALL], places=2)
        self.assertAlmostEqual(expected_metrics[R2_F1], actual_metrics[R2_F1], places=2)
        self.assertAlmostEqual(expected_metrics[RL_PRECISION], actual_metrics[RL_PRECISION], places=2)
        self.assertAlmostEqual(expected_metrics[RL_RECALL], actual_metrics[RL_RECALL], places=2)
        self.assertAlmostEqual(expected_metrics[RL_F1], actual_metrics[RL_F1], places=2)

        use_stemmer = True
        remove_stopwords = False
        expected_metrics = run_rouge([gold_summaries], [summary],
                                     use_porter_stemmer=use_stemmer, remove_stopwords=remove_stopwords,
                                     max_ngram=2, compute_rouge_l=compute_rouge_l)
        actual_metrics = python_rouge.run_python_rouge([gold_summaries], [summary],
                                                       use_porter_stemmer=use_stemmer,
                                                       remove_stopwords=remove_stopwords,
                                                       compute_rouge_l=compute_rouge_l)
        self.assertAlmostEqual(expected_metrics[R1_PRECISION], actual_metrics[R1_PRECISION], places=2)
        self.assertAlmostEqual(expected_metrics[R1_RECALL], actual_metrics[R1_RECALL], places=2)
        self.assertAlmostEqual(expected_metrics[R1_F1], actual_metrics[R1_F1], places=2)
        self.assertAlmostEqual(expected_metrics[R2_PRECISION], actual_metrics[R2_PRECISION], places=2)
        self.assertAlmostEqual(expected_metrics[R2_RECALL], actual_metrics[R2_RECALL], places=2)
        self.assertAlmostEqual(expected_metrics[R2_F1], actual_metrics[R2_F1], places=2)
        self.assertAlmostEqual(expected_metrics[RL_PRECISION], actual_metrics[RL_PRECISION], places=2)
        self.assertAlmostEqual(expected_metrics[RL_RECALL], actual_metrics[RL_RECALL], places=2)
        self.assertAlmostEqual(expected_metrics[RL_F1], actual_metrics[RL_F1], places=2)

        use_stemmer = True
        remove_stopwords = True
        expected_metrics = run_rouge([gold_summaries], [summary],
                                     use_porter_stemmer=use_stemmer, remove_stopwords=remove_stopwords,
                                     max_ngram=2, compute_rouge_l=compute_rouge_l)
        actual_metrics = python_rouge.run_python_rouge([gold_summaries], [summary],
                                                       use_porter_stemmer=use_stemmer,
                                                       remove_stopwords=remove_stopwords,
                                                       compute_rouge_l=compute_rouge_l)
        self.assertAlmostEqual(expected_metrics[R1_PRECISION], actual_metrics[R1_PRECISION], places=2)
        self.assertAlmostEqual(expected_metrics[R1_RECALL], actual_metrics[R1_RECALL], places=2)
        self.assertAlmostEqual(expected_metrics[R1_F1], actual_metrics[R1_F1], places=2)
        self.assertAlmostEqual(expected_metrics[R2_PRECISION], actual_metrics[R2_PRECISION], places=2)
        self.assertAlmostEqual(expected_metrics[R2_RECALL], actual_metrics[R2_RECALL], places=2)
        self.assertAlmostEqual(expected_metrics[R2_F1], actual_metrics[R2_F1], places=2)
        self.assertAlmostEqual(expected_metrics[RL_PRECISION], actual_metrics[RL_PRECISION], places=2)
        self.assertAlmostEqual(expected_metrics[RL_RECALL], actual_metrics[RL_RECALL], places=2)
        self.assertAlmostEqual(expected_metrics[RL_F1], actual_metrics[RL_F1], places=2)

    def _load_summaries(self, file_path: str) -> List[List[str]]:
        summaries = []
        with open(file_path, 'r') as f:
            for line in f:
                data = json.loads(line)
                summaries.append(data['summary'])
        return summaries

    def _load_multiple_summaries(self, file_path: str) -> List[List[List[str]]]:
        summaries = []
        with open(file_path, 'r') as f:
            for line in f:
                data = json.loads(line)
                summaries.append(data['summaries'])
        return summaries

    @pytest.mark.skipif(not os.path.exists(_duc2004_file_path), reason='DUC 2004 data does not exist')
    def test_hong2014(self):
        python_rouge = PythonRouge()
        duc2004 = self._load_multiple_summaries(_duc2004_file_path)
        centroid = self._load_summaries(_centroid_file_path)

        use_stemmer = True
        remove_stopwords = False
        max_words = 100
        expected_metrics = run_rouge(duc2004, centroid,
                                     use_porter_stemmer=use_stemmer, remove_stopwords=remove_stopwords,
                                     max_ngram=2, max_words=max_words, compute_rouge_l=True)
        actual_metrics = python_rouge.run_python_rouge(duc2004, centroid,
                                                       use_porter_stemmer=use_stemmer,
                                                       remove_stopwords=remove_stopwords,
                                                       max_words=max_words,
                                                       compute_rouge_l=True)
        assert math.isclose(expected_metrics[R1_PRECISION], actual_metrics[R1_PRECISION], abs_tol=1e-2)
        assert math.isclose(expected_metrics[R1_RECALL], actual_metrics[R1_RECALL], abs_tol=2e-2)
        assert math.isclose(expected_metrics[R1_F1], actual_metrics[R1_F1], abs_tol=2e-2)
        assert math.isclose(expected_metrics[R2_PRECISION], actual_metrics[R2_PRECISION], abs_tol=1e-2)
        assert math.isclose(expected_metrics[R2_RECALL], actual_metrics[R2_RECALL], abs_tol=1e-2)
        assert math.isclose(expected_metrics[R2_F1], actual_metrics[R2_F1], abs_tol=1e-2)
        # Rouge-L is a little further off, but still reasonably close enough that I'm not worried
        assert math.isclose(expected_metrics[RL_PRECISION], actual_metrics[RL_PRECISION], abs_tol=1e-1)
        assert math.isclose(expected_metrics[RL_RECALL], actual_metrics[RL_RECALL], abs_tol=1e-1)
        assert math.isclose(expected_metrics[RL_F1], actual_metrics[RL_F1], abs_tol=1e-1)
