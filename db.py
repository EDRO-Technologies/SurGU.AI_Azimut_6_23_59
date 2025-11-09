import mysql.connector
from typing import Optional, List, Dict


from config import CONFIG


# =============== USERS ===============
def set_user(name: str, job: str, experience: int = 0, email: str = "", phone: str = "") -> Optional[int]:
    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, job, experience, email, phone) VALUES (%s, %s, %s, %s, %s)",
            (name.strip(), job.strip(), experience, email.strip(), phone.strip())
        )
        uid = cursor.lastrowid
        cursor.close()
        conn.close()
        return uid
    except Exception as e:
        print(f"❌ set_user: {e}")
        return None


def get_user_by_id(uid: int) -> Optional[Dict]:
    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (uid,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    except Exception as e:
        print(f"❌ get_user_by_id: {e}")
        return None


def get_all_users() -> List[Dict]:
    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users ORDER BY id")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return users
    except Exception as e:
        print(f"❌ get_all_users: {e}")
        return []


# =============== TESTS ===============
def set_test(user_id: int, module: str, corrects: int = 0) -> Optional[int]:
    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tests (user_id, module, corrects) VALUES (%s, %s, %s)",
            (user_id, module.strip(), corrects)
        )
        tid = cursor.lastrowid
        cursor.close()
        conn.close()
        return tid
    except Exception as e:
        print(f"❌ set_test: {e}")
        return None


def get_test_by_id(tid: int) -> Optional[Dict]:
    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tests WHERE id = %s", (tid,))
        test = cursor.fetchone()
        cursor.close()
        conn.close()
        return test
    except Exception as e:
        print(f"❌ get_test_by_id: {e}")
        return None


def get_all_tests() -> List[Dict]:
    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tests ORDER BY id")
        tests = cursor.fetchall()
        cursor.close()
        conn.close()
        return tests
    except Exception as e:
        print(f"❌ get_all_tests: {e}")
        return []


# =============== SCENARIOS ===============
def set_scenario(user_id: int, is_correct: bool = False) -> Optional[int]:
    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO scenarios (user_id, is_correct) VALUES (%s, %s)",
            (user_id, 1 if is_correct else 0)
        )
        sid = cursor.lastrowid
        cursor.close()
        conn.close()
        return sid
    except Exception as e:
        print(f"❌ set_scenario: {e}")
        return None


def get_scenario_by_id(sid: int) -> Optional[Dict]:
    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM scenarios WHERE id = %s", (sid,))
        scenario = cursor.fetchone()
        cursor.close()
        conn.close()
        return scenario
    except Exception as e:
        print(f"❌ get_scenario_by_id: {e}")
        return None


def get_all_scenarios() -> List[Dict]:
    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM scenarios ORDER BY id")
        scenarios = cursor.fetchall()
        cursor.close()
        conn.close()
        return scenarios
    except Exception as e:
        print(f"❌ get_all_scenarios: {e}")
        return []


# =============== АНАЛИТИКА ===============
def get_user_detailed_stats(uid: int) -> dict:
    """
    📊 Полная статистика по пользователю — готово к графикам.
    """
    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id, name, job, experience FROM users WHERE id = %s", (uid,))
        user = cursor.fetchone()
        if not user:
            return {"error": "Пользователь не найден"}

        cursor.execute("SELECT module, corrects FROM tests WHERE user_id = %s", (uid,))
        tests = cursor.fetchall()

        cursor.execute("SELECT is_correct FROM scenarios WHERE user_id = %s", (uid,))
        scenarios = cursor.fetchall()

        total_tests = len(tests)
        total_corrects = sum(t['corrects'] for t in tests) if tests else 0
        avg_corrects = round(total_corrects / total_tests, 1) if total_tests > 0 else 0.0

        module_stats = {}
        for t in tests:
            mod = t['module']
            if mod not in module_stats:
                module_stats[mod] = {'count': 0, 'total_corrects': 0}
            module_stats[mod]['count'] += 1
            module_stats[mod]['total_corrects'] += t['corrects']

        for mod in module_stats:
            stats = module_stats[mod]
            stats['avg_corrects'] = round(stats['total_corrects'] / stats['count'], 1)

        pie_modules = {
            'labels': list(module_stats.keys()),
            'values': [module_stats[mod]['count'] for mod in module_stats]
        }

        total_scenarios = len(scenarios)
        correct_scenarios = sum(1 for s in scenarios if s['is_correct'])
        success_rate = round(correct_scenarios / total_scenarios * 100, 1) if total_scenarios > 0 else 0.0

        cursor.close()
        conn.close()

        return {
            'user_id': user['id'],
            'name': user['name'],
            'job': user['job'],
            'experience': user['experience'],
            'total_tests': total_tests,
            'total_corrects': total_corrects,
            'avg_corrects': avg_corrects,
            'total_scenarios': total_scenarios,
            'success_rate_percent': success_rate,
            'modules': module_stats,
            'pie_modules': pie_modules
        }

    except Exception as e:
        return {"error": str(e)}


def get_global_analytics() -> dict:
    """
    🧠 Админ-аналитика — по всем пользователям и модулям.
    """
    try:
        conn = mysql.connector.connect(**CONFIG)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) as count FROM users")
        users_total = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM tests")
        tests_total = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM scenarios")
        scenarios_total = cursor.fetchone()['count']

        cursor.execute("SELECT AVG(is_correct) * 100 as rate FROM scenarios")
        success_rate_overall = round(cursor.fetchone()['rate'] or 0.0, 1)

        cursor.execute("""
            SELECT 
                module,
                COUNT(*) as test_count,
                SUM(corrects) as total_corrects,
                AVG(corrects) as avg_corrects
            FROM tests
            GROUP BY module
            ORDER BY avg_corrects ASC
        """)
        modules_raw = cursor.fetchall()
        modules = {}
        for row in modules_raw:
            mod = row['module']
            modules[mod] = {
                'test_count': row['test_count'],
                'total_corrects': row['total_corrects'],
                'avg_corrects': round(row['avg_corrects'], 1)
            }

        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(is_correct) as correct
            FROM scenarios
        """)
        sc_row = cursor.fetchone()
        scenarios_stats = {
            'total': sc_row['total'],
            'correct': int(sc_row['correct'] or 0),
            'incorrect': int(sc_row['total'] - (sc_row['correct'] or 0)),
            'success_rate_percent': round((sc_row['correct'] or 0) / sc_row['total'] * 100, 1) if sc_row['total'] > 0 else 0.0
        }

        hardest_modules = sorted(
            modules.items(),
            key=lambda x: x[1]['avg_corrects']
        )[:5]
        hardest_modules_list = [{'module': m, **stats} for m, stats in hardest_modules]

        cursor.execute("""
            SELECT 
                u.id, u.name, u.job,
                COUNT(s.id) as scenarios_total,
                SUM(s.is_correct) as scenarios_correct,
                (SUM(s.is_correct) / COUNT(s.id)) * 100 as success_rate
            FROM users u
            JOIN scenarios s ON u.id = s.user_id
            GROUP BY u.id, u.name, u.job
            ORDER BY success_rate DESC
        """)
        users_performance = []
        for row in cursor.fetchall():
            users_performance.append({
                'user_id': row['id'],
                'name': row['name'],
                'job': row['job'],
                'scenarios_total': row['scenarios_total'],
                'scenarios_correct': int(row['scenarios_correct']),
                'success_rate_percent': round(row['success_rate'], 1)
            })

        module_labels = [m for m in modules.keys()]
        module_counts = [modules[m]['test_count'] for m in modules.keys()]
        module_avg_vals = [modules[m]['avg_corrects'] for m in modules.keys()]

        cursor.close()
        conn.close()

        return {
            'users_total': users_total,
            'tests_total': tests_total,
            'scenarios_total': scenarios_total,
            'success_rate_overall_percent': success_rate_overall,
            'modules': modules,
            'hardest_modules': hardest_modules_list,
            'scenarios_stats': scenarios_stats,
            'users_performance': users_performance,
            'pie_modules': {
                'labels': module_labels,
                'values': module_counts
            },
            'hist_modules_avg': {
                'labels': module_labels,
                'values': module_avg_vals
            }
        }

    except Exception as e:
        return {"error": str(e)}