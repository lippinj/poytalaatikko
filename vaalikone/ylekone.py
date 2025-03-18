import pathlib
import json
import requests


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
        return self.fetch("municipality/constituencies")

    def parties(self, constituency_id):
        return self.fetch(f"municipality/constituencies/{constituency_id}/parties")

    def candidate(self, constituency_id, candidate_id):
        return self.fetch_cached(
            f"municipality/constituencies/{constituency_id}/candidates/{candidate_id}"
        )

    def candidates(self, constituency_id):
        return self.fetch_cached(
            f"municipality/constituencies/{constituency_id}/candidates"
        )

    def questions(self, constituency_id):
        return self.fetch(f"municipality/constituencies/{constituency_id}/questions")


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
    def party_short(self):
        return self.parent.party_id_to_short_name(self.party_id)

    @property
    def answers_dict(self):
        return {int(k): v["answer"] for k, v in self.j_candidate["answers"].items()}

    def __repr__(self):
        return f"<{self.id}:{self.name} ({self.party_short})>"
