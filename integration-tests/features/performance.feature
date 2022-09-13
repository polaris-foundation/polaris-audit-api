Feature: Data migration performance
  As a Software Engineer
  I want my data migrations to be executed fast
  So that I can deliver my code to prod without any remorse

  Background:
    Given I have a valid JWT
    Given the database is empty

  Scenario Outline: all entries uuid to id data migration (Please, be patient, it takes time to seed the db.)
    Given database is downgraded to revision <db_revision_from>
    Given <number_rows> rows with <event_data_keys> keys
    When timing this step
    And database is upgraded to revision <db_revision_to>
    Then it takes less than <seconds_max> seconds to complete
    And all entries keys have changed from <event_data_keys> to <event_data_new_keys>

    Examples:
      | db_revision_from | db_revision_to | event_data_keys                                                                        | event_data_new_keys                                                        | seconds_max | number_rows |
      | 575920a9e769     | 6538146a372f   | device_uuid,clinician_uuid,patient_uuid,encounter_uuid,epr_encounter_uuid,obs_set_uuid | device_id,clinician_id,patient_id,encounter_id,epr_encounter_id,obs_set_id | 20          | 200000      |
