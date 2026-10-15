import json

from models.settings import DATA
from tools.budget import monthly_cost


def load_selection():
    document = json.loads((DATA / 'active_models.json').read_text(encoding='utf-8'))
    budget = json.loads((DATA / 'budget.json').read_text(encoding='utf-8'))
    models = document['models']
    for model in models:
        model['monthly_inr'] = round(monthly_cost(model['input_price'], model['output_price'], budget), 2)
        assert model['monthly_inr'] <= budget['monthly_budget_inr']
    return dict(shortlisted=models, budget=budget, selection_basis=document['selection_basis'])
