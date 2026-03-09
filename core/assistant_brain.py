from core.command_handler import add_task, show_tasks

def process_query(query):
    query = query.lower()

    if "add task" in query:
        task = query.replace("add task", "")
        return add_task(task)

    elif "show tasks" in query:
        return show_tasks()

    elif "hello" in query:
        return "Hello Mitali, how can I help you?"

    else:
        return "Sorry, I didn't understand that."