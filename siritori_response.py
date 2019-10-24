#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from random import shuffle, choice
from itertools import count
from collections import defaultdict
import jaconv

class Response:

    def getRes(self,text):

        return str("答えを返す")
        try:
            input = raw_input
        except NameError:
            pass

        ansfilename = r"ans.txt"

        # 答えを辞書にセットする
        with(open(ansfilename, 'r')) as F:
            dic = list(set(F.read().strip().split('\n')))
        first_words = [ e[0] for e in dic ]
        used = defaultdict(int)

        players = [ 'あなた', 'わたし' ]
        shuffle(players)
        startswith = None
        for i in count(1):
            if players[i % len(players)] == 'あなた':
                if startswith == None:
                    startswith = choice(first_words)
                    startswith = jaconv.kata2hira(startswith)
                sys.stdout.write('{0:3}: あなたの番です。 "{1}": '.format(i, startswith))
                s = input()
                s = jaconv.kata2hira(s)
                # 一文字目の確認
                while(not s.startswith(startswith)):
                    print('"{0}"で始まっていません。 '.format(startswith))
                    sys.stdout.write('{0:3}: あなたの番です。 "{1}": '.format(i, startswith))
                    s = input()
                    s = jaconv.kata2hira(s)
                # 既出単語かどうかの確認
                if s in used:
                    print('"{0}"は{1}回目に{2}が使用しています。わたしの勝ちです。'.format(s, used[s], players[used[s]%len(players)]))
                    break
                startswith = s[-1]
                # 最後の文字が「ん」かどうかの確認
                if startswith == 'ん':
                    print('最後に、ん がついたので私の勝ちです。')
                    break
                used[s] = i
            else:
                msg = '{0:3}: わたしの番です。      '.format(i)
                if startswith == None:
                    word = choice(dic)
                    convword = jaconv.kata2hira(word)
                    startswith = convword[-1]
                    used[convword] = i
                    print(msg + '{0}'.format(word))
                else:
                    words = [ e for e in dic if jaconv.kata2hira(e).startswith(startswith) and e not in used ]
                    if len(words) == 0:
                        print('もう思いつきません! あなたの勝ちです。')
                        print('{0} から始まる言葉を教えてください！'.format(startswith))
                        s = input()
                        # 回答リストに書き込む処理
                        with(open(ansfilename, 'a')) as F:
                            F.write(s)
                            F.write('\n')
                        print('ありがとうございます！これでまた賢くなりました！')
                        break
                    else:
                        word = choice(words)
                        convword = jaconv.kata2hira(word)
                        startswith = convword[-1]
                        used[word] = i
                        print(msg + '{0}'.format(word))
        print('今回のしりとりでは{0}個の単語を使用しました。'.format(len(used)))
