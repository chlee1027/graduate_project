users_db = {}
plans_db = {}
logs_db = []

# recommendation_id -> recommendation data
recommendations_db = {}

# user_id -> plan_id -> stats
bandit_stats = {}


def get_user_bandit_stats(user_id: str) -> dict:
    if user_id not in bandit_stats:
        bandit_stats[user_id] = {}
    return bandit_stats[user_id]


def get_user_plan_stat(user_id: str, plan_id: str) -> dict:
    user_stats = get_user_bandit_stats(user_id)

    if plan_id not in user_stats:
        user_stats[plan_id] = {
            "count": 0,
            "total_reward": 0.0,
            "avg_reward": 0.0,
        }

    return user_stats[plan_id]