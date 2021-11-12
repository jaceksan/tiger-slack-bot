import time
import re
import random


class Cache:
    def __init__(self):
        self._cache = {}

    def put(self, atom, user, ttl=90):
        ts = time.time()
        try:
            users = self._cache[atom]
            users.append((user, ts + ttl))
        except KeyError:
            self._cache[atom] = [(user, time.time() + ttl)]

    def get(self, atom):
        ts = time.time()
        try:
            new_users = [(user, ttl) for user, ttl in self._cache[atom] if ttl > ts]
            self._cache[atom] = new_users
            return new_users
        except KeyError:
            return []


cache = Cache()
re_report = re.compile(r'^<[^>]+>\s*execute_(tab|csv|vis) ', re.I)


def answer_from_history(q_user_id, text):
    atoms = ["list workspaces", "list data sources", "list labels", "list metrics", "list insights"]

    results = []
    for atom in atoms:
        if atom in text:
            c_res = cache.get(atom)
            if not c_res:
                cache.put(atom, q_user_id)
            else:
                results.append((atom, atom[5:], c_res))

    report_match = re_report.match(text)
    if report_match:
        c_res = cache.get(text)
        if not c_res:
            cache.put(text, q_user_id)
        else:
            results.append((text, "execution", c_res))

    if not results:
        return False, ""

    rand = random.random()
    if rand > 0.8 + (0.2 * (len(results) / (len(atoms) + 1))):
        for atom, _, _ in results:
            cache.put(atom, q_user_id)
        return False, "Lucky you, I answer even boring questions (you have asked the same question few seconds ago)"

    message = "I am not going to answer, you are asking the same question too often. Ask"
    for _, text, c_res in results:
        users = " or ".join([f"<@{user}>" for user, _ in c_res])
        message += f"\n\t{users} for {text}"
    return True, message
