from unittest.mock import Mock

from models.team_model import TeamModel


def test_get_all_returns_teams():
    # Arrange
    team_repository = Mock()
    database = Mock()
    database.team_repository = team_repository

    expected_teams = [
        Mock(),
        Mock()
    ]

    team_repository.get_teams.return_value = expected_teams

    model = TeamModel(database)

    # Act
    result = model.get_all()

    # Assert
    assert result == expected_teams
    team_repository.get_teams.assert_called_once_with()


def test_get_team_by_id_returns_team():
    # Arrange
    team_repository = Mock()
    database = Mock()
    database.team_repository = team_repository

    expected_team = Mock()

    team_repository.get_team_by_id.return_value = expected_team

    model = TeamModel(database)

    # Act
    result = model.get_team_by_id(5)

    # Assert
    assert result == expected_team
    team_repository.get_team_by_id.assert_called_once_with(5)


def test_get_teams_by_country_returns_teams():
    # Arrange
    team_repository = Mock()
    database = Mock()
    database.team_repository = team_repository

    expected_teams = [
        Mock(),
        Mock()
    ]

    team_repository.get_teams.return_value = expected_teams

    model = TeamModel(database)

    # Act
    result = model.get_teams_by_country(3)

    # Assert
    assert result == expected_teams
    team_repository.get_teams.assert_called_once_with(3)


def test_add_team_calls_repository():
    # Arrange
    team_repository = Mock()
    database = Mock()
    database.team_repository = team_repository

    model = TeamModel(database)

    # Act
    model.add_team(
        country_id=1,
        team_name="IF Elfsborg",
        display_name="Elfsborg"
    )

    # Assert
    team_repository.add_team.assert_called_once_with(
        country_id=1,
        team_name="IF Elfsborg",
        display_name="Elfsborg"
    )


def test_update_team_calls_repository():
    # Arrange
    team_repository = Mock()
    database = Mock()
    database.team_repository = team_repository

    model = TeamModel(database)

    # Act
    model.update_team(
        team_id=7,
        country_id=1,
        team_name="IF Elfsborg",
        display_name="Elfsborg"
    )

    # Assert
    team_repository.update_team.assert_called_once_with(
        team_id=7,
        country_id=1,
        team_name="IF Elfsborg",
        display_name="Elfsborg"
    )


def test_delete_team_calls_repository():
    # Arrange
    team_repository = Mock()
    database = Mock()
    database.team_repository = team_repository

    model = TeamModel(database)

    # Act
    model.delete_team(7)

    # Assert
    team_repository.delete_team.assert_called_once_with(7)
