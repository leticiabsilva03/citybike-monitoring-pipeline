import pytest
from airflow.models import DagBag


@pytest.fixture(scope="module")
def dagbag():
    # Carrega apenas seus DAGs, sem os exemplos do Airflow
    return DagBag(include_examples=False)


def test_bronze_dag_loaded(dagbag):
    # Ajuste para usar o dag_id que você definiu ("bronze")
    dag = dagbag.get_dag("bronze")
    assert dag is not None, "DAG 'bronze' deve estar carregado"


def test_expected_tasks(dagbag):
    dag = dagbag.get_dag("bronze")
    task_ids = {task.task_id for task in dag.tasks}
    expected = {"fetch_stations"}  # nome da sua task
    assert expected.issubset(
        task_ids
    ), f"Tasks esperadas faltando: {expected - task_ids}"
