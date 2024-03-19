from time_getter import timegetter

def handler(current_task, Task, Users, UserSolved, db, current_user):
    user_obj = Users.query.filter_by(username=current_user.username).first()
    task_obj = Task.query.filter_by(name=current_task).first()
    user_solved = UserSolved.query.filter_by(task_id=task_obj.id, user=user_obj.username).first()
    if user_solved is not None:
        return 'Вы уже решили эту задачу'
    if user_obj is not None and task_obj is not None:
        user_obj.points += int(task_obj.points)
        user_obj.count += 1
        new_solved_user = UserSolved(task_id=task_obj.id, user=user_obj.username, time=timegetter())
        db.session.add(new_solved_user)
        db.session.commit()
        return 'Ваш флаг верен'
    else:
        return 'Произошла ошибка'