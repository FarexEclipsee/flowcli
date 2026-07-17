from __future__ import annotations

import time


def test_add_and_get_task(tmp_db):
    task_id = tmp_db.add_task("Write tests", project="flowcli", tag="chore")
    row = tmp_db.get_task(task_id)
    assert row["description"] == "Write tests"
    assert row["project"] == "flowcli"
    assert row["status"] == "open"


def test_list_tasks_filters_by_status(tmp_db):
    open_id = tmp_db.add_task("Open task")
    done_id = tmp_db.add_task("Done task")
    tmp_db.mark_done(done_id)

    open_rows = tmp_db.list_tasks(status="open")
    done_rows = tmp_db.list_tasks(status="done")

    assert {r["id"] for r in open_rows} == {open_id}
    assert {r["id"] for r in done_rows} == {done_id}


def test_list_tasks_filters_by_project(tmp_db):
    tmp_db.add_task("Task A", project="alpha")
    tmp_db.add_task("Task B", project="beta")

    alpha_rows = tmp_db.list_tasks(project="alpha")
    assert len(alpha_rows) == 1
    assert alpha_rows[0]["project"] == "alpha"


def test_mark_done_is_idempotent(tmp_db):
    task_id = tmp_db.add_task("Task")
    assert tmp_db.mark_done(task_id) is True
    assert tmp_db.mark_done(task_id) is False  # already done


def test_delete_task_removes_row(tmp_db):
    task_id = tmp_db.add_task("Task")
    assert tmp_db.delete_task(task_id) is True
    assert tmp_db.get_task(task_id) is None


def test_delete_task_cascades_sessions(tmp_db):
    task_id = tmp_db.add_task("Task")
    tmp_db.start_session(task_id)
    tmp_db.delete_task(task_id)

    with tmp_db.cursor() as cur:
        cur.execute("SELECT COUNT(*) as c FROM sessions WHERE task_id = ?", (task_id,))
        assert cur.fetchone()["c"] == 0


def test_start_and_stop_session(tmp_db):
    task_id = tmp_db.add_task("Task")
    session_id = tmp_db.start_session(task_id)

    assert tmp_db.open_session()["id"] == session_id
    time.sleep(0.01)
    assert tmp_db.stop_session(session_id, note="done a bit") is True
    assert tmp_db.open_session() is None


def test_stop_session_twice_returns_false(tmp_db):
    task_id = tmp_db.add_task("Task")
    session_id = tmp_db.start_session(task_id)
    tmp_db.stop_session(session_id)
    assert tmp_db.stop_session(session_id) is False


def test_sessions_for_report_only_includes_completed(tmp_db):
    task_id = tmp_db.add_task("Task", project="alpha")
    s1 = tmp_db.start_session(task_id)
    tmp_db.stop_session(s1)
    tmp_db.start_session(task_id)  # left running

    rows = tmp_db.sessions_for_report(project="alpha")
    assert len(rows) == 1
    assert rows[0]["id"] == s1
