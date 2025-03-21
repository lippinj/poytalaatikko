import pathlib
import json
from collections import defaultdict

import requests
import numpy as np


class Api:
    def __init__(self, vaalit="alue-ja-kuntavaalit2025"):
        self.vaalit = vaalit
        self.baseurl = f"https://vaalit.yle.fi/vaalikone/{vaalit}/api/public"
        pathlib.Path(".ylekone-cache").mkdir(exist_ok=True)

    def fetch(self, s):
        url = f"{self.baseurl}/{s}"
        headers = dict(Accept="application/json")
        return requests.get(url, headers=headers).json()

    def fetch_cached(self, s):
        cache_path = f".ylekone-cache/{s.replace('/','-')}.json"
        try:
            with open(cache_path, "r") as f:
                return json.load(f)
        except:
            j = self.fetch(s)
            with open(cache_path, "w") as f:
                json.dump(j, f, indent=4)
            return j

    def constituencies(self):
        return self.fetch_cached("municipality/constituencies")

    def parties(self, constituency_id):
        return self.fetch_cached(
            f"municipality/constituencies/{constituency_id}/parties"
        )

    def candidate(self, constituency_id, candidate_id):
        return self.fetch_cached(
            f"municipality/constituencies/{constituency_id}/candidates/{candidate_id}"
        )

    def candidates(self, constituency_id):
        return self.fetch_cached(
            f"municipality/constituencies/{constituency_id}/candidates"
        )

    def questions(self, constituency_id):
        return self.fetch_cached(
            f"municipality/constituencies/{constituency_id}/questions"
        )


class Vaalikone:
    def __init__(self):
        self.api = Api()
        self.j_constituencies = self.api.constituencies()
        self._cache = {}

    def __repr__(self):
        return f"<Vaalikone>"

    def name_to_id(self, name):
        for j in self.j_constituencies:
            if j["name_fi"] == name:
                return j["id"]
        return None

    def id_to_name(self, id):
        for j in self.j_constituencies:
            if j["id"] == id:
                return j["name_fi"]
        return None

    def __getitem__(self, id):
        if isinstance(id, str):
            id = self.name_to_id(id)
        if id not in self._cache:
            self._cache[id] = Municipality(self, id, self.id_to_name(id))
        return self._cache[id]


class Municipality:
    def __init__(self, parent, id, name):
        self.api = Api()
        self.parent = parent
        self.id = id
        self.j_parties = self.api.parties(id)
        self.j_candidates = self.api.candidates(id)
        self.j_questions = self.api.questions(id)
        self._cache = {}

    @property
    def name(self):
        return self.parent.id_to_name(self.id)

    @property
    def candidate_ids(self):
        for j in self.j_candidates:
            yield j["id"]

    @property
    def party_ids(self):
        for j in self.j_parties:
            yield j["id"]

    @property
    def candidates(self):
        for id in self.candidate_ids:
            yield self[id]

    @property
    def questions(self):
        for j_category in self.j_questions:
            for j_question in j_category["questions"]:
                yield j_question["id"], j_question["text_fi"], j_question

    def question_id_to_text(self, id):
        for j_category in self.j_questions:
            for j_question in j_category["questions"]:
                if j_question["id"] == id:
                    return j_question["text_fi"]
        return None

    def party_id_to_name(self, id):
        for j in self.j_parties:
            if j["id"] == id:
                return j["name_fi"]
        return None

    def party_id_to_short_name(self, id):
        for j in self.j_parties:
            if j["id"] == id:
                return j["short_name_fi"]
        return None

    def candidate_name_to_id(self, name):
        for j in self.j_candidates:
            if j["first_name"] + " " + j["last_name"] == name:
                return j["id"]
        return None

    def __repr__(self):
        return f"<{self.id}:{self.name}>"

    def __getitem__(self, id):
        if isinstance(id, str):
            id = self.candidate_name_to_id(id)
        if id not in self._cache:
            self._cache[id] = Candidate(self, self.id, id)
        return self._cache[id]


class Candidate:
    def __init__(self, parent, municipality_id, candidate_id):
        self.api = Api()
        self.parent = parent
        self.municipality_id = municipality_id
        self.candidate_id = candidate_id
        self.j_candidate = self.api.candidate(municipality_id, candidate_id)

    @property
    def id(self):
        return self.j_candidate["id"]

    @property
    def first_name(self):
        return self.j_candidate["first_name"]

    @property
    def last_name(self):
        return self.j_candidate["last_name"]

    @property
    def name(self):
        return self.first_name + " " + self.last_name

    @property
    def party_id(self):
        return self.j_candidate["party_id"]

    @property
    def party(self):
        return self.parent.party_id_to_name(self.party_id)

    @property
    def party_short(self):
        return self.parent.party_id_to_short_name(self.party_id)

    @property
    def answers_dict(self):
        return {int(k): v["answer"] for k, v in self.j_candidate["answers"].items()}

    @property
    def answers(self):
        for id, j in self.j_candidate["answers"].items():
            yield int(id), j["answer"], j

    def __repr__(self):
        return f"<{self.id}:{self.name} ({self.party_short})>"


class Stat:
    def __init__(self):
        self.party = None
        self._respondents_agree = []
        self._respondents_somewhat_agree = []
        self._respondents_somewhat_disagree = []
        self._respondents_disagree = []

    def __repr__(self):
        return f"<Stat {self.party} {self.dd}/{self.d}/{self.a}/{self.aa}>"

    @property
    def prettystr(self):
        return f"{self.party:>8} | ⮇:{self.dd:<3} ⭣:{self.d:<3} ⭡:{self.a:<3} ⮅:{self.aa:<3} | μ:{self.mean:<+5.2f} σ:{self.std:<+5.2f}"

    @property
    def num_agree(self):
        return len(self._respondents_agree)

    @property
    def num_somewhat_agree(self):
        return len(self._respondents_somewhat_agree)

    @property
    def num_somewhat_disagree(self):
        return len(self._respondents_somewhat_disagree)

    @property
    def num_disagree(self):
        return len(self._respondents_disagree)

    @property
    def dd(self):
        return self.num_disagree

    @property
    def d(self):
        return self.num_somewhat_disagree

    @property
    def a(self):
        return self.num_agree

    @property
    def aa(self):
        return self.num_somewhat_agree

    @property
    def num_total(self):
        return self.aa + self.a + self.d + self.dd

    @property
    def n(self):
        return self.num_total

    @property
    def mean(self):
        return (
            ((-3 * self.dd) + (-1 * self.d) + (+1 * self.a) + (+3 * self.aa)) / self.n
            if self.n
            else 0
        )

    @property
    def mean2(self):
        return (
            ((9 * self.dd) + (1 * self.d) + (1 * self.a) + (9 * self.aa)) / self.n
            if self.n
            else 0
        )

    @property
    def var(self):
        return self.mean2 - self.mean**2

    @property
    def std(self):
        return np.sqrt(self.mean2 - self.mean**2)

    def add(self, answer, respondent):
        if answer == 1:
            self._respondents_disagree.append(respondent)
        elif answer == 2:
            self._respondents_somewhat_disagree.append(respondent)
        elif answer == 4:
            self._respondents_somewhat_agree.append(respondent)
        elif answer == 5:
            self._respondents_agree.append(respondent)
        else:
            raise RuntimeError()


def make_stats(municipality):
    stats = defaultdict(lambda: defaultdict(Stat))
    for candidate in municipality.candidates:
        for qid, answer, _ in candidate.answers:
            stat = stats[qid][candidate.party_short]
            stat.party = stat.party or candidate.party_short
            stat.add(answer, candidate)
    return stats
