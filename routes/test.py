from flask import Blueprint, request, jsonify
from supabase_client import supabase

test_bp = Blueprint('test', __name__)

@test_bp.route('/add', methods=['POST'])
def add_task():
    title = request.json.get('title')
    response = supabase.table('tasks').insert({"title": title, "completed": False}).execute()
    return jsonify(response.data)

@test_bp.route('/tasks', methods=['GET'])
def get_tasks():
    response = supabase.table('tasks').select('*').execute()
    return jsonify(response.data)
